#!/bin/sh
# Скрипт запуска фронтенда с поддержкой переменной PORT

PORT=${PORT:-3700}
exec serve -s build -l "$PORT"
