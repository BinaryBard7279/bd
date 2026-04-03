import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from app.admin import setup_admin

app = FastAPI(title="API")

# 1. Сначала базовые настройки
setup_admin(app)

@app.get("/", response_class=HTMLResponse)
async def root():
    return "Всё работает. <a href='/admin'>Перейти в админку</a>"

# 2. Настраиваем сессии 
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-key-for-dev")
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=True,
    same_site="lax"
)

# ВСЁ! Больше никаких мидлварей для принудительного HTTPS здесь не нужно.