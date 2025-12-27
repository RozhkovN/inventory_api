-- Инициализация базы данных для Inventory API
-- Этот скрипт выполняется при первом запуске PostgreSQL контейнера

-- Убедиться что расширения включены
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- База данных уже будет создана благодаря POSTGRES_DB,
-- но мы гарантируем её существование
DO $$ 
BEGIN 
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'inventory_db') THEN 
    CREATE DATABASE inventory_db;
  END IF;
END 
$$;

-- Убедиться что пользователь имеет доступ
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
