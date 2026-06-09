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

APP_DIR="$(pwd)"

# 5. Алиас `sql` для быстрого запуска (идемпотентно)
BASHRC="$HOME/.bashrc"
if ! grep -q "alias sql=" "$BASHRC" 2>/dev/null; then
  echo "alias sql='bash \"$APP_DIR/run.sh\"'" >> "$BASHRC"
  echo "==> Добавлен алиас 'sql' в ~/.bashrc (перезапусти Termux или: source ~/.bashrc)"
fi

# 6. Иконка на главном экране через Termux:Widget
if [ -d "/data/data/com.termux" ]; then
  mkdir -p "$HOME/.shortcuts"
  cat > "$HOME/.shortcuts/Mobile SQL" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
bash "$APP_DIR/run.sh"
EOF
  chmod +x "$HOME/.shortcuts/Mobile SQL"
  echo "==> Создан launcher для Termux:Widget (~/.shortcuts/Mobile SQL)"
fi

echo ""
echo "Готово. Запуск одной из команд:"
echo "   sql                 # короткий алиас"
echo "   bash run.sh         # напрямую"
echo "Или тапни иконку Termux:Widget на главном экране."
echo "Браузер откроется сам на http://localhost:8000"
