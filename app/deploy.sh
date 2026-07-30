#!/bin/sh
set -e

echo "===================================================="
echo "🚀 Запуск развертывания Crypto Auth API..."
echo "===================================================="

echo "🧹 Очистка фантомного кэша Python..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

echo "⏳ Ожидание готовности базы данных PostgreSQL..."
until pg_isready -h "$POSTGRES_SERVER" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
    printf '.'
    sleep 1
done
echo -e "\n🟢 База данных готова к работе!"

echo "⚙️  Применение миграций Alembic..."
# Переходим в корень проекта, где лежит alembic.ini
cd /app
alembic upgrade head

echo "🌱 Запуск наполнения базы данных начальными данными..."
python app/seed.py

echo "===================================================="
echo "🎉 Развертывание успешно завершено!"
echo "===================================================="

exec "$@"
