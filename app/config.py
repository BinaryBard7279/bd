import os
from dotenv import load_dotenv

# Загружаем .env.local если есть, иначе обычные .env
load_dotenv(".env.local")
load_dotenv()

class Settings:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "postgres")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    
    # Добавляем SECRET_KEY для работы сессий в админке
    SECRET_KEY = os.getenv("SECRET_KEY", "my_super_secret_key_change_me")

    @property
    def DATABASE_URL(self) -> str:
        # Используем asyncpg для асинхронности
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()