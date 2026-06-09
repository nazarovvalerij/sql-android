# Mobile SQL — SQL-клиент прямо на телефоне

Read-only клиент для **ClickHouse** и **MariaDB**, который крутится локально на Samsung S25 Ultra
в Termux. Редактор открываешь в браузере по `http://localhost:8000`. Сетевой доступ к БД даёт
твой рабочий VPN (трафик Termux идёт через системный VPN Android).

Возможности: подсветка SQL, автодополнение по ключевым словам **и по твоим таблицам/колонкам**
(схема подтягивается из `system.columns` / `information_schema`), история запросов, экспорт CSV,
дефолтный LIMIT.

## Архитектура

```
[ Браузер телефона ]  →  [ FastAPI в Termux ]  →  VPN  →  [ ClickHouse :8123 / MariaDB :3306 ]
   index.html              app.py (localhost)
```

Ничего наружу не торчит: сервер слушает только `127.0.0.1`, секреты БД лежат в `config.json`
на телефоне.

## Установка в Termux (быстрый путь, из GitHub)

1. Поставь **Termux** из F-Droid (версия из Play Store устарела): https://f-droid.org/packages/com.termux/
2. В Termux одной пачкой:
   ```bash
   pkg install -y git
   git clone https://github.com/nazarovvalerij/sql-android.git
   cd sql-android
   bash install.sh        # поставит python + зависимости, создаст config.json
   nano config.json       # впиши свои хосты/логины
   ```

`install.sh` сам определяет Termux, ставит `python` через `pkg`, зависимости через `pip`
и копирует `config.example.json` → `config.json`.

## Запуск

```bash
cd sql-android
bash run.sh
```

Открой в Chrome на телефоне: **http://localhost:8000**
Чтобы было как приложение — в меню Chrome «Добавить на главный экран» (запустится в отдельном окне).

Остановить: в Termux `Ctrl+C`.

## Безопасность (важно)

- В приложении жёстко разрешены только `SELECT / WITH / SHOW / DESCRIBE / EXPLAIN`, составные
  запросы через `;` блокируются.
- ClickHouse выполняется с `readonly=2`, MariaDB — `SET SESSION TRANSACTION READ ONLY`.
- **Всё равно заведи отдельного read-only пользователя БД** — это главный рубеж защиты,
  а не клиент. Для ClickHouse: профиль с `readonly=1`. Для MariaDB: `GRANT SELECT`.
- Сервер слушает только localhost — из сети телефон недоступен.

## Зависимости фронта

CodeMirror 5 грузится с CDN (cdnjs). Нужен интернет на телефоне. Если хочешь полностью
офлайн — скачай 5 файлов CM локально и поправь пути в `index.html` (могу сделать).

## Возможные доработки

- Несколько баз/схем в выпадашке
- Пагинация результата
- Подсветка медленных запросов / `EXPLAIN` в один тап
- Избранные запросы
