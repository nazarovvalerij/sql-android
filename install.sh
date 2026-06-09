#!/usr/bin/env bash
# Mobile SQL — установщик. Работает в Termux (Android) и в обычном Linux.
set -e
cd "$(dirname "$0")"

echo "==> Mobile SQL: установка"

# 1. Termux? Ставим системный python через pkg
if [ -d "/data/data/com.termux" ]; then
  echo "==> Termux обнаружен, ставлю python..."
  pkg install -y python
fi

# 2. python должен быть в наличии
if ! command -v python3 >/dev/null 2>&1; then
  echo "!! python3 не найден. Установи Python и запусти снова."
  exit 1
fi

# 3. Зависимости
echo "==> Ставлю зависимости..."
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

# 4. Конфиг
if [ ! -f config.json ]; then
  cp config.example.json config.json
  echo "==> Создан config.json — впиши свои хосты/логины:  nano config.json"
else
  echo "==> config.json уже есть, не трогаю."
fi

echo ""
echo "Готово. Запуск:   bash run.sh"
echo "Затем открой в браузере телефона:  http://localhost:8000"
