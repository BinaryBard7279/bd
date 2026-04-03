import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASS = os.getenv("DB_PASS", "postgres")
    DB_NAME = os.getenv("DB_NAME", "eos_db")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-prod")

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
