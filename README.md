# Telegram News Digest Bot

Асинхронный Telegram-бот (aiogram 3) для агрегации новостей из RSS и веб-сайтов, фильтрации по интересам (TF-IDF + косинусное сходство) и отправки дайджестов вручную (/digest) и автоматически по расписанию (APScheduler).

## 🚀 Автоматический запуск (рекомендуется)

### Windows:
```bash
python setup.py
# Настройте BOT_TOKEN в файле .env
run.bat
```

### Linux/Mac:
```bash
python3 setup.py
# Настройте BOT_TOKEN в файле .env
./run.sh
```

## 📋 Ручная установка

1) Python 3.10+

```bash
python -m venv venv
venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
```

2) Настройте переменные окружения:

Скопируйте `.env.example` в `.env` и настройте:
- `BOT_TOKEN` - токен бота от @BotFather
- `API_ID`, `API_HASH`, `PHONE_NUMBER` - для парсинга Telegram-каналов (опционально)

3) Запуск:

```bash
python -m bot.main
```

## Основные команды

- /start — регистрация и главное меню
- /help — помощь
- /digest — сгенерировать дайджест сейчас

## 📱 Поддержка Telegram-каналов

Бот может парсить Telegram-каналы и анализировать их по ключевым словам:

### Настройка:
1. Зайдите на https://my.telegram.org
2. Войдите в аккаунт и создайте приложение
3. Скопируйте `API_ID` и `API_HASH`
4. Укажите их в `.env` файле
5. Добавьте свой номер телефона

### Использование:
- Добавьте Telegram-канал через меню "📱 Добавить Telegram-канал"
- Укажите ссылку: `@channel_name` или `https://t.me/channel_name`
- Бот автоматически будет собирать посты и фильтровать по интересам

В меню доступны inline-кнопки для управления источниками, интересами и расписанием.

## Стек

- aiogram 3.x
- feedparser, beautifulsoup4 + requests
- aiosqlite (SQLite)
- scikit-learn (TF-IDF)
- APScheduler

## Структура
См. план в `.cursor/plans/...` или в файле проекта.

## 🛠️ Автоматизация

Проект включает автоматизированные скрипты:

- **`setup.py`** — автоматическая установка зависимостей и настройка
- **`run.bat`** (Windows) / **`run.sh`** (Linux/Mac) — запуск с проверками
- **`.env.example`** — шаблон конфигурации

## Примечания
- Для MVP используется SQLite. При масштабировании можно перейти на PostgreSQL.
- Парсинг Telegram-каналов отключён в MVP согласно требованиям.


