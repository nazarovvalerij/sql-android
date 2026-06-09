#!/usr/bin/env bash
# Mobile SQL — установка в одну строку.
# Запуск:
#   curl -fsSL https://raw.githubusercontent.com/nazarovvalerij/sql-android/main/bootstrap.sh | bash
set -e

REPO="https://github.com/nazarovvalerij/sql-android.git"
DIR="$HOME/sql-android"

echo "==> Mobile SQL: bootstrap"

# git (в Termux ставим через pkg, в обычном Linux считаем что уже есть)
if ! command -v git >/dev/null 2>&1; then
  if command -v pkg >/dev/null 2>&1; then
    pkg install -y git
  else
    echo "!! git не найден — поставь его и запусти снова."
    exit 1
  fi
fi

# clone или обновление
if [ -d "$DIR/.git" ]; then
  echo "==> Репозиторий уже есть, обновляю (git pull)..."
  git -C "$DIR" pull --ff-only
else
  git clone "$REPO" "$DIR"
fi

cd "$DIR"
bash install.sh

echo ""
echo "Осталось вписать доступы к БД:"
echo "   nano $DIR/config.json"
echo "И запустить:  sql"
