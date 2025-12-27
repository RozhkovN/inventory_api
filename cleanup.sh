#!/bin/bash
# Полная очистка и переустановка приложения Inventory API
# Запусти этот скрипт на сервере: bash cleanup.sh

set -e

echo "=========================================="
echo "🧹 ПОЛНАЯ ОЧИСТКА ПРИЛОЖЕНИЯ"
echo "=========================================="

cd ~/main/inventory_api

echo ""
echo "1️⃣ Остановка контейнеров..."
docker compose down || true

echo ""
echo "2️⃣ Удаление всех контейнеров приложения..."
docker rm -f inventory_api inventory_frontend inventory_db || true

echo ""
echo "3️⃣ Удаление всех томов (БД)..."
docker volume rm inventory_api_postgres_data || true

echo ""
echo "4️⃣ Удаление всех сетей приложения..."
docker network rm inventory_api_inventory_network || true

echo ""
echo "5️⃣ Удаление старых образов..."
docker rmi inventory_api-backend inventory_api-frontend || true

echo ""
echo "6️⃣ Очистка Docker от неиспользуемых ресурсов..."
docker system prune -f

echo ""
echo "=========================================="
echo "✅ ОЧИСТКА ЗАВЕРШЕНА"
echo "=========================================="
echo ""
echo "Теперь запусти:"
echo ""
echo "  cd ~/main/inventory_api"
echo "  docker compose build --no-cache"
echo "  docker compose up -d"
echo ""
echo "Затем откройся в браузере:"
echo "  http://80.253.19.93:3700"
echo ""
