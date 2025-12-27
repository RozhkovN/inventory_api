-- Инициализация базы данных для Inventory API
-- Этот скрипт выполняется при первом запуске PostgreSQL контейнера

-- Убедиться что расширения включены
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Гарантировать права доступа
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
