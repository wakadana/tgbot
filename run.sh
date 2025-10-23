#!/bin/bash

echo "🚀 Запуск Telegram News Bot"
echo "================================"

# Проверка виртуального окружения
if [ ! -f "venv/bin/python" ]; then
    echo "❌ Виртуальное окружение не найдено"
    echo "Запустите setup.py для установки"
    exit 1
fi

# Проверка файла .env
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден"
    echo "Скопируйте .env.example в .env и настройте BOT_TOKEN"
    exit 1
fi

# Проверка BOT_TOKEN
if grep -q "BOT_TOKEN=your_bot_token_here" .env; then
    echo "❌ BOT_TOKEN не настроен"
    echo "Откройте файл .env и укажите ваш токен бота"
    exit 1
fi

echo "✅ Все проверки пройдены"
echo "🚀 Запускаю бота..."
echo

# Запуск бота
venv/bin/python -m bot.main

echo
echo "Бот остановлен"
