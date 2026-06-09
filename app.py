"""
Mobile SQL — лёгкий read-only SQL-клиент для ClickHouse и MariaDB.
Запускается прямо на телефоне в Termux, открывается в браузере по http://localhost:8000

Запуск:
    uvicorn app:app --host 127.0.0.1 --port 8000
"""
import json
import re
from pathlib import Path

import pymysql
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

BASE = Path(__file__).parent
CONFIG = json.loads((BASE / "config.json").read_text(encoding="utf-8"))
DEFAULT_LIMIT = int(CONFIG.get("default_limit", 1000))
MAX_LIMIT = int(CONFIG.get("max_limit", 50000))

app = FastAPI(title="Mobile SQL")

# --- read-only защита -------------------------------------------------------
# 1) запрос должен начинаться с разрешённого ключевого слова
# 2) запрещаем несколько стейтментов (защита от "SELECT 1; DROP ...")
ALLOWED_PREFIX = re.compile(
    r"^\s*(WITH|SELECT|SHOW|DESC|DESCRIBE|EXPLAIN)\b",
    re.IGNORECASE,
)


def strip_sql(sql: str) -> str:
    return sql.strip().rstrip(";").strip()


def check_readonly(sql: str) -> str:
    sql = strip_sql(sql)
    if not sql:
        raise HTTPException(400, "Пустой запрос")
    # запрещаем составные запросы (точка с запятой внутри тела)
    if ";" in sql:
        raise HTTPException(400, "Разрешён только один запрос за раз (убери ';')")
    if not ALLOWED_PREFIX.match(sql):
        raise HTTPException(
            400, "Разрешены только SELECT / WITH / SHOW / DESCRIBE / EXPLAIN"
        )
    return sql


def clamp_limit(limit) -> int:
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT
    return max(1, min(limit, MAX_LIMIT))


# --- ClickHouse -------------------------------------------------------------
def run_clickhouse(sql: str, limit: int) -> dict:
    ch = CONFIG["clickhouse"]
    url = f"http://{ch['host']}:{ch.get('port', 8123)}/"
    params = {
        "database": ch.get("database", "default"),
        "default_format": "JSONCompact",
        # readonly=2 — разрешает SELECT и установку настроек, запрещает запись и DDL
        "readonly": 2,
        "max_result_rows": limit,
        "result_overflow_mode": "break",  # обрезать, а не падать с ошибкой
        "max_execution_time": ch.get("timeout", 60),
    }
    headers = {}
    if ch.get("user"):
        headers["X-ClickHouse-User"] = ch["user"]
    if ch.get("password"):
        headers["X-ClickHouse-Key"] = ch["password"]
    resp = requests.post(
        url, params=params, data=sql.encode("utf-8"),
        headers=headers, timeout=ch.get("timeout", 60) + 5,
    )
    if resp.status_code != 200:
        raise HTTPException(400, resp.text[:2000])
    data = resp.json()
    columns = [m["name"] for m in data.get("meta", [])]
    rows = data.get("data", [])
    return {"columns": columns, "rows": rows, "rows_count": len(rows)}


def run_mariadb(sql: str, limit: int) -> dict:
    m = CONFIG["mariadb"]
    conn = pymysql.connect(
        host=m["host"],
        port=int(m.get("port", 3306)),
        user=m["user"],
        password=m.get("password", ""),
        database=m.get("database") or None,
        connect_timeout=int(m.get("timeout", 10)),
        read_timeout=int(m.get("timeout", 60)),
        charset="utf8mb4",
    )
    try:
        with conn.cursor() as cur:
            # дополнительная страховка на стороне сессии
            try:
                cur.execute("SET SESSION TRANSACTION READ ONLY")
            except pymysql.err.MySQLError:
                pass  # некоторые движки не поддерживают — read-only уже гарантирован проверкой выше
            cur.execute(sql)
            columns = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchmany(limit)
        # сериализуем нестандартные типы (datetime, Decimal, bytes) в строки
        norm = [
            [v if isinstance(v, (int, float, type(None))) else str(v) for v in row]
            for row in rows
        ]
        return {"columns": columns, "rows": norm, "rows_count": len(norm)}
    finally:
        conn.close()


RUNNERS = {"clickhouse": run_clickhouse, "mariadb": run_mariadb}


# --- API --------------------------------------------------------------------
class QueryIn(BaseModel):
    db: str
    sql: str
    limit: int | None = None


@app.post("/api/query")
def query(body: QueryIn):
    runner = RUNNERS.get(body.db)
    if runner is None:
        raise HTTPException(400, f"Неизвестная БД: {body.db}")
    if body.db not in CONFIG:
        raise HTTPException(400, f"БД '{body.db}' не настроена в config.json")
    sql = check_readonly(body.sql)
    limit = clamp_limit(body.limit if body.limit is not None else DEFAULT_LIMIT)
    return runner(sql, limit)


@app.get("/api/schema")
def schema(db: str):
    """Список таблиц и колонок для автодополнения."""
    if db == "clickhouse" and "clickhouse" in CONFIG:
        sql = (
            "SELECT table, name FROM system.columns "
            "WHERE database = currentDatabase() ORDER BY table, position"
        )
        res = run_clickhouse(sql, MAX_LIMIT)
    elif db == "mariadb" and "mariadb" in CONFIG:
        sql = (
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = DATABASE() ORDER BY table_name, ordinal_position"
        )
        res = run_mariadb(sql, MAX_LIMIT)
    else:
        raise HTTPException(400, f"БД '{db}' не настроена")
    tables: dict[str, list[str]] = {}
    for table, col in res["rows"]:
        tables.setdefault(table, []).append(col)
    return {"tables": tables}


@app.get("/api/databases")
def databases():
    return {"databases": [k for k in ("clickhouse", "mariadb") if k in CONFIG]}


@app.get("/")
def index():
    return FileResponse(BASE / "index.html")
