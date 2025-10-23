import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    bot_token: str
    database_path: str = "bot_database.db"
    log_level: str = "INFO"
    api_id: str = ""
    api_hash: str = ""
    phone_number: str = ""


def load_config() -> Config:
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set in environment")
    database_path = os.getenv("DATABASE_PATH", "bot_database.db")
    log_level = os.getenv("LOG_LEVEL", "INFO")
    api_id = os.getenv("API_ID", "")
    api_hash = os.getenv("API_HASH", "")
    phone_number = os.getenv("PHONE_NUMBER", "")
    return Config(
        bot_token=token, 
        database_path=database_path, 
        log_level=log_level,
        api_id=api_id,
        api_hash=api_hash,
        phone_number=phone_number
    )


