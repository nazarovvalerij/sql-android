#!/data/data/com.termux/files/usr/bin/bash
# Запуск Mobile SQL на телефоне
cd "$(dirname "$0")"

URL="http://localhost:8000"

# Открыть браузер автоматически. Сначала пробуем termux-open-url (нужен termux-api),
# иначе — системный `am`, который есть в Termux без доп. приложений.
open_url() {
  if command -v termux-open-url >/dev/null 2>&1; then
    termux-open-url "$1"
  elif command -v am >/dev/null 2>&1; then
    am start --user 0 -a android.intent.action.VIEW -d "$1" >/dev/null 2>&1
  fi
}

# Ждём пару секунд (чтобы сервер успел подняться) и открываем браузер в фоне.
(sleep 2; open_url "$URL") >/dev/null 2>&1 &

echo "==> Mobile SQL запущен на $URL   (Ctrl+C — остановить)"
exec uvicorn app:app --host 127.0.0.1 --port 8000
