#!/usr/bin/env python3
"""
Автоматическая установка и настройка Telegram News Bot
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, shell=True):
    """Выполнить команду и показать результат"""
    print(f"Выполняю: {cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Ошибка: {result.stderr}")
        return False
    if result.stdout:
        print(result.stdout)
    return True


def check_python():
    """Проверить версию Python"""
    if sys.version_info < (3, 10):
        print("❌ Требуется Python 3.10 или выше")
        print(f"Текущая версия: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True


def setup_venv():
    """Создать виртуальное окружение"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Виртуальное окружение уже существует")
        return True
    
    print("📦 Создаю виртуальное окружение...")
    if not run_command(f"{sys.executable} -m venv venv"):
        return False
    print("✅ Виртуальное окружение создано")
    return True


def get_pip_command():
    """Получить команду pip для текущей ОС"""
    if os.name == 'nt':  # Windows
        return "venv\\Scripts\\pip"
    else:  # Linux/Mac
        return "venv/bin/pip"


def get_python_command():
    """Получить команду python для текущей ОС"""
    if os.name == 'nt':  # Windows
        return "venv\\Scripts\\python"
    else:  # Linux/Mac
        return "venv/bin/python"


def install_dependencies():
    """Установить зависимости"""
    pip_cmd = get_pip_command()
    
    print("📦 Устанавливаю зависимости...")
    if not run_command(f"{pip_cmd} install --upgrade pip"):
        return False
    
    if not run_command(f"{pip_cmd} install -r requirements.txt"):
        return False
    
    print("📱 Устанавливаю telethon для парсинга Telegram-каналов...")
    if not run_command(f"{pip_cmd} install telethon==1.35.0"):
        print("⚠️  Не удалось установить telethon, но это не критично")
    
    print("✅ Зависимости установлены")
    return True


def setup_env():
    """Настроить файл .env"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print("✅ Файл .env уже существует")
        return True
    
    if not env_example_path.exists():
        print("❌ Файл .env.example не найден")
        return False
    
    print("📝 Создаю файл .env...")
    shutil.copy(env_example_path, env_path)
    print("✅ Файл .env создан")
    print("⚠️  Не забудьте указать BOT_TOKEN в файле .env!")
    return True


def main():
    """Главная функция установки"""
    print("🚀 Автоматическая установка Telegram News Bot")
    print("=" * 50)
    
    # Проверка Python
    if not check_python():
        return False
    
    # Создание venv
    if not setup_venv():
        return False
    
    # Установка зависимостей
    if not install_dependencies():
        return False
    
    # Настройка .env
    if not setup_env():
        return False
    
    print("\n" + "=" * 50)
    print("✅ Установка завершена!")
    print("\n📋 Следующие шаги:")
    print("1. Откройте файл .env и укажите ваш BOT_TOKEN")
    print("2. Запустите бота командой:")
    if os.name == 'nt':
        print("   run.bat")
    else:
        print("   ./run.sh")
    print("\n🎉 Готово к работе!")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
