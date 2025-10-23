@echo off
echo 🚀 Запуск Telegram News Bot
echo ================================

REM Проверка виртуального окружения
if not exist "venv\Scripts\python.exe" (
    echo ❌ Виртуальное окружение не найдено
    echo Запустите setup.py для установки
    pause
    exit /b 1
)

REM Проверка файла .env
if not exist ".env" (
    echo ❌ Файл .env не найден
    echo Скопируйте .env.example в .env и настройте BOT_TOKEN
    pause
    exit /b 1
)

REM Проверка BOT_TOKEN
findstr /C:"BOT_TOKEN=your_bot_token_here" .env >nul
if not errorlevel 1 (
    echo ❌ BOT_TOKEN не настроен
    echo Откройте файл .env и укажите ваш токен бота
    pause
    exit /b 1
)

echo ✅ Все проверки пройдены
echo 🚀 Запускаю бота...
echo.

REM Запуск бота
venv\Scripts\python -m bot.main

echo.
echo Бот остановлен
pause
