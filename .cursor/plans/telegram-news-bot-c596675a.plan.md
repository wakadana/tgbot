<!-- c596675a-93a3-433c-b4d6-c958ca9c3321 3a78eddc-8320-4d3d-a035-6d53634cfef2 -->
# План разработки Telegram News Digest Bot

## Архитектура проекта

```
JUST-DIE-BOT/
├── bot/
│   ├── __init__.py
│   ├── main.py                 # Точка входа, инициализация бота
│   ├── config.py               # Конфигурация (токен, настройки)
│   ├── handlers/               # Обработчики команд и callback'ов
│   │   ├── __init__.py
│   │   ├── start.py           # /start, /help
│   │   ├── sources.py         # Управление источниками (RSS, веб)
│   │   ├── interests.py       # Управление интересами/темами
│   │   └── digest.py          # /digest и inline-кнопки дайджеста
│   ├── parsers/               # Парсеры для разных источников
│   │   ├── __init__.py
│   │   ├── rss_parser.py      # Парсинг RSS-лент (feedparser)
│   │   ├── web_parser.py      # Веб-скрейпинг (beautifulsoup4)
│   │   └── telegram_parser.py # Парсинг Telegram-каналов (telethon)
│   ├── filters/               # Фильтрация контента
│   │   ├── __init__.py
│   │   └── content_filter.py  # TF-IDF + косинусное сходство
│   ├── database/              # Работа с БД
│   │   ├── __init__.py
│   │   ├── models.py          # Схема БД (Users, Sources, Interests)
│   │   └── db.py              # Асинхронные функции работы с БД
│   ├── scheduler/             # Планировщик задач
│   │   ├── __init__.py
│   │   └── tasks.py           # Автоматическая отправка по расписанию
│   └── keyboards/             # Inline-клавиатуры
│       ├── __init__.py
│       └── inline.py          # Конструкторы клавиатур для меню
├── requirements.txt           # Зависимости проекта
├── .env.example              # Пример файла переменных окружения
├── .gitignore
└── README.md                 # Документация проекта
```

## Технологический стек

- **aiogram 3.x** - асинхронный фреймворк для Telegram Bot API
- **feedparser** - парсинг RSS/Atom лент
- **beautifulsoup4 + requests** - парсинг HTML страниц
- **telethon** - парсинг Telegram-каналов через MTProto API
- **aiosqlite** - асинхронная работа с SQLite
- **APScheduler** - планирование автоматических задач
- **scikit-learn** - TF-IDF векторизация и косинусное сходство
- **python-dotenv** - управление переменными окружения

## Этапы реализации

### Этап 1: Базовая инфраструктура

**1.1 Инициализация проекта**

- Создать структуру директорий
- Создать `requirements.txt` с зависимостями:
  ```
  aiogram==3.15.0
  feedparser==6.0.11
  beautifulsoup4==4.12.3
  requests==2.32.3
  telethon==1.36.0
  aiosqlite==0.20.0
  apscheduler==3.10.4
  scikit-learn==1.5.2
  python-dotenv==1.0.1
  lxml==5.3.0
  ```

- Создать `.env.example` с примером:
  ```
  BOT_TOKEN=your_bot_token_here
  DATABASE_PATH=bot_database.db
  LOG_LEVEL=INFO
  # Telegram API для парсинга каналов (опционально)
  API_ID=your_api_id_here
  API_HASH=your_api_hash_here
  PHONE_NUMBER=your_phone_number_here
  ```

- Создать `.gitignore`:
  ```
  __pycache__/
  *.pyc
  .env
  *.db
  venv/
  .idea/
  ```


**1.2 Конфигурация**

- `bot/config.py`: класс `Config` для загрузки настроек из `.env`
  - Использовать `python-dotenv` для загрузки переменных
  - Валидация обязательных параметров (BOT_TOKEN)
  - Значения по умолчанию для опциональных параметров

**1.3 База данных**

- `bot/database/models.py`: определить схему БД
  - Таблица `users`:
    - `user_id` INTEGER PRIMARY KEY
    - `chat_id` INTEGER UNIQUE
    - `schedule` TEXT (формат: "HH:MM" или NULL)
    - `created_at` TIMESTAMP
  - Таблица `sources`:
    - `source_id` INTEGER PRIMARY KEY AUTOINCREMENT
    - `user_id` INTEGER (FK → users.user_id)
    - `type` TEXT ('rss', 'website', 'telegram')
    - `url` TEXT
    - `added_at` TIMESTAMP
  - Таблица `interests`:
    - `interest_id` INTEGER PRIMARY KEY AUTOINCREMENT
    - `user_id` INTEGER (FK → users.user_id)
    - `interest_text` TEXT
    - `added_at` TIMESTAMP

- `bot/database/db.py`: асинхронные функции для работы с БД
  - `init_db()` - создание таблиц
  - Пользователи: `add_user()`, `get_user()`, `update_schedule()`
  - Источники: `add_source()`, `get_user_sources()`, `delete_source()`
  - Интересы: `add_interest()`, `get_user_interests()`, `delete_interest()`
  - Использовать `aiosqlite` для асинхронных операций

### Этап 2: Inline-клавиатуры

**2.1 Конструкторы клавиатур**

- `bot/keyboards/inline.py`:
  - `get_main_menu()` - главное меню:
    - "📰 Добавить источник"
    - "📋 Мои источники"
    - "🎯 Интересы"
    - "⏰ Расписание"
    - "📨 Получить дайджест"

  - `get_sources_menu()` - меню источников:
    - "➕ Добавить RSS"
    - "🌐 Добавить сайт"
    - "📱 Добавить Telegram-канал"
    - "📋 Список источников"
    - "🔙 Назад"

  - `get_interests_menu()` - меню интересов:
    - "➕ Добавить тему"
    - "📋 Мои темы"
    - "🔙 Назад"

  - `get_schedule_menu()` - меню расписания:
    - "🌅 Утро (8:00)"
    - "☀️ Обед (12:00)"
    - "🌆 Вечер (18:00)"
    - "🔕 Отключить"
    - "🔙 Назад"

  - `get_digest_actions()` - кнопки дайджеста:
    - "🔄 Обновить"
    - "📑 По темам"
    - "📚 По источникам"

  - `get_source_list_keyboard(sources)` - список с кнопками удаления
  - `get_interest_list_keyboard(interests)` - список с кнопками удаления

  - Использовать `InlineKeyboardBuilder` и `CallbackData` factories

### Этап 3: Обработчики команд

**3.1 Стартовые команды**

- `bot/handlers/start.py`:
  - `/start`:
    - Регистрация пользователя в БД
    - Приветственное сообщение
    - Отображение главного меню через `get_main_menu()`

  - `/help`:
    - Справка по всем командам
    - Примеры использования
    - Inline-кнопка "В главное меню"

  - Callback-обработчик для главного меню

**3.2 Управление источниками**

- `bot/handlers/sources.py`:
  - Callback-обработчик для меню источников
  - FSM (Finite State Machine) для добавления источника:
    - Состояние ожидания URL
    - Валидация RSS (проверка через feedparser)
    - Валидация веб-сайта (проверка доступности)
    - Валидация Telegram-канала (проверка через telethon)
    - Сохранение в БД

  - Отображение списка источников:
    - Группировка по типам (RSS / Веб-сайты / Telegram-каналы)
    - Inline-кнопки удаления для каждого источника

  - Callback-обработчик удаления источника:
    - Подтверждение удаления
    - Обновление списка

**3.3 Управление интересами**

- `bot/handlers/interests.py`:
  - Callback-обработчик для меню интересов
  - FSM для добавления темы:
    - Состояние ожидания текста темы
    - Валидация (не пустая строка, макс. 100 символов)
    - Сохранение в БД

  - Отображение списка интересов:
    - Нумерованный список
    - Inline-кнопки удаления

  - Callback-обработчик удаления темы

**3.4 Настройка расписания**

- `bot/handlers/sources.py` (дополнение):
  - Callback-обработчики для выбора времени
  - Сохранение расписания в формате "HH:MM"
  - Регистрация задачи в планировщике
  - Подтверждение настройки

### Этап 4: Парсеры контента

**4.1 RSS-парсер**

- `bot/parsers/rss_parser.py`:
  - Класс `RSSParser`:
    - Метод `async def parse_feed(url: str) -> List[Dict]`
    - Использование `feedparser.parse()`
    - Извлечение полей:
      - `title` - заголовок новости
      - `link` - ссылка на оригинал
      - `published` - дата публикации
      - `summary` - краткое описание
      - `source_name` - название источника

    - Обработка ошибок:
      - Невалидный RSS
      - Недоступный источник
      - Пустая лента

    - Фильтрация дубликатов
    - Ограничение по количеству (последние N новостей)
    - Возврат списка словарей

**4.2 Веб-парсер**

- `bot/parsers/web_parser.py`:
  - Класс `WebParser`:
    - Метод `async def parse_page(url: str) -> List[Dict]`
    - Использование `requests` + `BeautifulSoup`
    - Универсальная логика парсинга:
      - Извлечение заголовков (`<h1>`, `<h2>`, `<h3>`)
      - Поиск основного контента (`<article>`, `<main>`, `<div class="content">`)
      - Извлечение параграфов (`<p>`)
      - Очистка от скриптов, стилей, комментариев

    - Обработка ошибок HTTP (404, 500, timeout)
    - User-Agent для обхода блокировок
    - Возврат структурированных данных

**4.3 Telegram-парсер**

- `bot/parsers/telegram_parser.py`:
  - Класс `TelegramParser`:
    - Инициализация с API_ID, API_HASH, номером телефона
    - Контекстный менеджер для управления сессией
    - Метод `async def parse_channel(channel_url: str, limit: int = 50) -> List[Dict]`:
      - Получение entity канала через `get_entity()`
      - Проверка типа (Channel, Chat)
      - Парсинг сообщений за последние 7 дней
      - Извлечение полей:
        - `title` - заголовок из текста сообщения
        - `content` - полный текст сообщения
        - `link` - ссылка на сообщение в канале
        - `published` - дата публикации
        - `source_name` - название канала
        - `message_id` - ID сообщения
        - `views`, `forwards` - статистика

    - Обработка ошибок:
      - `FloodWaitError` - автоматическое ожидание при rate limiting
      - `ChannelPrivateError` - недоступные каналы
      - `ChatAdminRequiredError` - каналы без прав доступа

    - Дополнительные методы:
      - `validate_channel()` - проверка доступности канала
      - `get_channel_info()` - получение информации о канале
      - `_extract_title()` - извлечение заголовка из текста

    - Глобальные функции:
      - `parse_telegram_channel()` - удобная функция для парсинга
      - `validate_telegram_channel()` - удобная функция для валидации

### Этап 5: Фильтрация контента (TF-IDF)

**5.1 Модуль фильтрации**

- `bot/filters/content_filter.py`:
  - Класс `ContentFilter`:
    - Инициализация:
      - `TfidfVectorizer` из scikit-learn
      - Настройки для русского языка: `max_features=1000, ngram_range=(1,2)`

    - Метод `filter_by_interests(items: List[Dict], interests: List[str]) -> List[Dict]`:
      - Объединение title + summary для каждой новости
      - Векторизация текстов новостей
      - Векторизация интересов пользователя
      - Вычисление косинусного сходства (`cosine_similarity`)
      - Фильтрация по порогу (например, similarity > 0.2)
      - Сортировка по убыванию релевантности
      - Добавление поля `relevance_score` к каждой новости

    - Метод `extract_keywords(text: str) -> List[str]`:
      - Извлечение ключевых слов через TF-IDF
      - Для улучшения группировки по темам

### Этап 6: Генерация и отправка дайджеста

**6.1 Обработчик дайджеста**

- `bot/handlers/digest.py`:
  - Команда `/digest`:
    - Получение источников пользователя из БД
    - Получение интересов пользователя из БД
    - Проверка наличия настроек
    - Запуск процесса генерации

  - Функция `generate_digest(user_id: int) -> str`:
    - Параллельный парсинг всех источников (RSS + веб)
    - Объединение результатов
    - Применение фильтра по интересам
    - Форматирование в Markdown:
      ```
      📰 *Ваш дайджест новостей*
      
      🔹 *Заголовок новости 1*
      📌 Источник: Название
      🔗 [Читать полностью](ссылка)
      _Релевантность: 85%_
      
      🔹 *Заголовок новости 2*
      ...
      ```

    - Добавление inline-кнопок действий

  - Callback-обработчики для кнопок:
    - "Обновить" - повторная генерация
    - "По темам" - группировка по ключевым словам
    - "По источникам" - группировка по источникам

  - Обработка ошибок:
    - Нет источников - предложить добавить
    - Нет интересов - предложить добавить
    - Ошибки парсинга - показать какие источники недоступны
    - Нет релевантного контента - сообщение с рекомендацией

### Этап 7: Планировщик автоматической отправки

**7.1 Модуль планировщика**

- `bot/scheduler/tasks.py`:
  - Инициализация `AsyncIOScheduler`:
    - Настройка timezone
    - Job stores (memory для разработки)

  - Функция `async def send_scheduled_digest(bot, user_id: int)`:
    - Получение источников и интересов
    - Генерация дайджеста через `generate_digest()`
    - Отправка сообщения пользователю
    - Логирование успешной отправки
    - Обработка ошибок (пользователь заблокировал бота)

  - Функция `setup_user_schedule(scheduler, bot, user_id: int, time_str: str)`:
    - Удаление старой задачи пользователя (если есть)
    - Парсинг времени (например, "08:00")
    - Создание CronTrigger
    - Добавление задачи в планировщик с уникальным ID

  - Функция `remove_user_schedule(scheduler, user_id: int)`:
    - Удаление задачи из планировщика

  - Функция `start_scheduler(bot)`:
    - Запуск планировщика при старте бота
    - Восстановление всех расписаний из БД

### Этап 8: Точка входа и запуск

**8.1 Главный файл**

- `bot/main.py`:
  - Импорты всех модулей
  - Функция `async def main()`:
    - Загрузка конфигурации из `Config`
    - Инициализация бота: `Bot(token=config.BOT_TOKEN)`
    - Инициализация диспетчера: `Dispatcher()`
    - Инициализация БД: `await init_db()`
    - Регистрация роутеров:
      - `start_router`
      - `sources_router`
      - `interests_router`
      - `digest_router`
    - Запуск планировщика: `await start_scheduler(bot)`
    - Удаление вебхука (для polling)
    - Запуск polling: `await dp.start_polling(bot)`

  - Graceful shutdown:
    - Обработка SIGINT/SIGTERM
    - Остановка планировщика
    - Закрытие соединения с БД

  - Entry point:
    ```python
    if __name__ == "__main__":
        asyncio.run(main())
    ```


**8.2 README.md**

- Описание проекта
- Установка:
  ```bash
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```

- Настройка:
  - Создать `.env` из `.env.example`
  - Получить токен бота от @BotFather
  - Вставить токен в `.env`
- Запуск:
  ```bash
  python -m bot.main
  ```

- Команды бота
- Примеры использования

## Дополнительные улучшения (опционально)

- **Логирование**: Модуль `logging` для отслеживания событий и ошибок
- **Кэширование**: Сохранение спарсенных новостей с timestamp для избежания повторного парсинга
- **Pagination**: Для длинных списков источников/интересов (через inline-кнопки "Назад/Вперед")
- **Статистика**: Счетчики отправленных дайджестов, количество отобранных новостей
- **Rate limiting**: Ограничение частоты парсинга источников
- **Уведомления**: Уведомление о недоступных источниках

## План тестирования

1. **Парсеры**:

   - Тест RSS-парсера на реальных лентах (Lenta.ru, Habr, TechCrunch)
   - Тест веб-парсера на разных структурах сайтов
   - Проверка обработки ошибок

2. **Фильтрация**:

   - Тест TF-IDF на русских и английских текстах
   - Проверка релевантности фильтрации
   - Граничные случаи (пустые интересы, нет совпадений)

3. **Handlers**:

   - Тест всех команд и callback'ов
   - Проверка FSM (корректные и некорректные вводы)
   - Проверка inline-кнопок

4. **Планировщик**:

   - Тест настройки расписания
   - Проверка автоматической отправки
   - Множественные пользователи с разными расписаниями

5. **База данных**:

   - Тест CRUD операций
   - Проверка внешних ключей
   - Конкурентный доступ

### To-dos

- [ ] Создать структуру проекта, requirements.txt, .env.example, .gitignore
- [ ] Реализовать config.py для загрузки настроек из переменных окружения
- [ ] Создать database/models.py со схемой БД (Users, Sources, Interests)
- [ ] Реализовать database/db.py с асинхронными CRUD операциями
- [ ] Создать handlers/start.py с командами /start и /help, главным меню
- [ ] Реализовать handlers/sources.py для управления источниками (добавление, удаление, список)
- [ ] Реализовать handlers/interests.py для управления темами интересов
- [ ] Создать parsers/rss_parser.py для парсинга RSS-лент через feedparser
- [ ] Создать parsers/web_parser.py для парсинга веб-страниц через BeautifulSoup
- [ ] Реализовать filters/content_filter.py с TF-IDF и косинусным сходством
- [ ] Создать handlers/digest.py с командой /digest и inline-кнопками
- [ ] Реализовать scheduler/tasks.py с APScheduler для автоматической отправки
- [ ] Создать keyboards/inline.py со всеми конструкторами inline-клавиатур
- [ ] Создать main.py с инициализацией бота, регистрацией handlers и запуском
- [ ] Протестировать все модули: парсеры, фильтры, handlers, планировщик