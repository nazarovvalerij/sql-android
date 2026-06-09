#!/data/data/com.termux/files/usr/bin/bash
# Запуск Mobile SQL на телефоне
cd "$(dirname "$0")"
exec uvicorn app:app --host 127.0.0.1 --port 8000
