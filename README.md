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

## Установка в Termux (одна строка)

1. Поставь **Termux** из F-Droid (версия из Play Store устарела): https://f-droid.org/packages/com.termux/
2. В Termux вставь одну команду:
   ```bash
   curl -fsSL https://raw.githubusercontent.com/nazarovvalerij/sql-android/main/bootstrap.sh | bash
   ```
   Она поставит git, склонирует репозиторий в `~/sql-android`, запустит `install.sh`
   (python + зависимости + config + алиас `sql` + иконку для виджета).
3. Впиши доступы к БД:
   ```bash
   nano ~/sql-android/config.json
   ```

<details>
<summary>Установка вручную (если не доверяешь curl | bash)</summary>

```bash
pkg install -y git
git clone https://github.com/nazarovvalerij/sql-android.git
cd sql-android
bash install.sh
nano config.json
```
</details>

## Запуск

Любой из способов:

```bash
sql              # короткий алиас (после перезапуска Termux или `source ~/.bashrc`)
bash ~/sql-android/run.sh
```

Браузер **откроется сам** на `http://localhost:8000` (через системный `am`).
Остановить сервер: `Ctrl+C` в Termux.

### Иконка на главном экране (как приложение)

`install.sh` создаёт launcher `~/.shortcuts/Mobile SQL`. Чтобы получить иконку-кнопку:

1. Поставь дополнение **Termux:Widget** из F-Droid: https://f-droid.org/packages/com.termux.widget/
2. На рабочем столе Android: добавь виджет **Termux:Widget** → выбери **Mobile SQL**.
3. Тап по иконке → сервер стартует и Chrome открывается сам. Termux открывать не нужно.

Можно также в Chrome «Добавить на главный экран» сам редактор — тогда он запускается в отдельном окне без адресной строки.

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
