from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📰 Добавить источник", callback_data="menu:sources"))
    builder.row(InlineKeyboardButton(text="🎯 Интересы", callback_data="menu:interests"))
    builder.row(InlineKeyboardButton(text="⏰ Расписание", callback_data="menu:schedule"))
    builder.row(InlineKeyboardButton(text="📨 Получить дайджест", callback_data="digest:run"))
    return builder.as_markup()


def get_sources_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📱 Добавить Telegram-канал", callback_data="sources:add_telegram"))
    builder.row(InlineKeyboardButton(text="➕ Добавить RSS", callback_data="sources:add_rss"))
    builder.row(InlineKeyboardButton(text="🌐 Добавить сайт", callback_data="sources:add_web"))
    builder.row(InlineKeyboardButton(text="📋 Список источников", callback_data="sources:list"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="menu:root"))
    return builder.as_markup()


def get_interests_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Добавить тему", callback_data="interests:add"))
    builder.row(InlineKeyboardButton(text="📋 Мои темы", callback_data="interests:list"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="menu:root"))
    return builder.as_markup()


def get_schedule_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🌅 Утро (8:00)", callback_data="schedule:set:08:00"))
    builder.row(InlineKeyboardButton(text="☀️ Обед (12:00)", callback_data="schedule:set:12:00"))
    builder.row(InlineKeyboardButton(text="🌆 Вечер (18:00)", callback_data="schedule:set:18:00"))
    builder.row(InlineKeyboardButton(text="🔕 Отключить", callback_data="schedule:off"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="menu:root"))
    return builder.as_markup()


def get_digest_actions():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔄 Обновить", callback_data="digest:refresh"))
    builder.row(InlineKeyboardButton(text="📑 По темам", callback_data="digest:group:topics"))
    builder.row(InlineKeyboardButton(text="📚 По источникам", callback_data="digest:group:sources"))
    return builder.as_markup()


def get_source_list_keyboard(sources):
    builder = InlineKeyboardBuilder()
    for src in sources:
        # Красивое отображение типов источников
        type_icons = {
            'rss': '📡',
            'website': '🌐', 
            'telegram': '📱'
        }
        type_names = {
            'rss': 'RSS',
            'website': 'Сайт',
            'telegram': 'Telegram'
        }
        
        icon = type_icons.get(src['type'], '📄')
        type_name = type_names.get(src['type'], src['type'].upper())
        title = f"{icon} {type_name}: {src['url']}"
        
        # Для Telegram-каналов делаем ссылку на канал
        if src['type'] == 'telegram':
            channel_url = f"https://t.me/{src['url'].replace('@', '')}"
            builder.row(
                InlineKeyboardButton(text=title, url=channel_url)
            )
        else:
            builder.row(
                InlineKeyboardButton(text=title, url=src['url'])
            )
        builder.row(
            InlineKeyboardButton(text="❌ Удалить", callback_data=f"sources:del:{src['source_id']}")
        )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="menu:sources"))
    return builder.as_markup()


def get_interest_list_keyboard(interests):
    builder = InlineKeyboardBuilder()
    for it in interests:
        builder.row(
            InlineKeyboardButton(text=f"🎯 {it['interest_text']}", callback_data="noop")
        )
        builder.row(
            InlineKeyboardButton(text="❌ Удалить", callback_data=f"interests:del:{it['interest_id']}")
        )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="menu:interests"))
    return builder.as_markup()


def get_popular_topics_keyboard():
    """Клавиатура с популярными тематиками новостей"""
    builder = InlineKeyboardBuilder()
    
    # Технологии и IT
    builder.row(InlineKeyboardButton(text="💻 Технологии", callback_data="topic:tech"))
    builder.row(InlineKeyboardButton(text="🤖 ИИ и машинное обучение", callback_data="topic:ai"))
    builder.row(InlineKeyboardButton(text="📱 Мобильные приложения", callback_data="topic:mobile"))
    
    # Экономика и финансы
    builder.row(InlineKeyboardButton(text="💰 Криптовалюты", callback_data="topic:crypto"))
    builder.row(InlineKeyboardButton(text="📈 Фондовый рынок", callback_data="topic:stocks"))
    builder.row(InlineKeyboardButton(text="🏦 Банки и финансы", callback_data="topic:finance"))
    
    # Политика и общество
    builder.row(InlineKeyboardButton(text="🏛️ Политика", callback_data="topic:politics"))
    builder.row(InlineKeyboardButton(text="🌍 Международные новости", callback_data="topic:world"))
    builder.row(InlineKeyboardButton(text="⚖️ Право и законы", callback_data="topic:law"))
    
    # Наука и медицина
    builder.row(InlineKeyboardButton(text="🔬 Наука", callback_data="topic:science"))
    builder.row(InlineKeyboardButton(text="🏥 Медицина", callback_data="topic:medicine"))
    builder.row(InlineKeyboardButton(text="🌱 Экология", callback_data="topic:ecology"))
    
    # Спорт и развлечения
    builder.row(InlineKeyboardButton(text="⚽ Спорт", callback_data="topic:sports"))
    builder.row(InlineKeyboardButton(text="🎬 Кино и сериалы", callback_data="topic:movies"))
    builder.row(InlineKeyboardButton(text="🎮 Игры", callback_data="topic:gaming"))
    
    # Бизнес и стартапы
    builder.row(InlineKeyboardButton(text="🚀 Стартапы", callback_data="topic:startups"))
    builder.row(InlineKeyboardButton(text="💼 Бизнес", callback_data="topic:business"))
    builder.row(InlineKeyboardButton(text="🛒 E-commerce", callback_data="topic:ecommerce"))
    
    # Дополнительные опции
    builder.row(InlineKeyboardButton(text="✏️ Ввести вручную", callback_data="interests:add_manual"))
    builder.row(InlineKeyboardButton(text="✅ Готово", callback_data="menu:interests"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="menu:interests"))
    
    return builder.as_markup()


