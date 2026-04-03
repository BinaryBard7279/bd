import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

from app.admin import setup_admin
from app.config import settings

app = FastAPI(title="API")

# 1. Сессии для работы авторизации sqladmin
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax"
)

# 2. БРОНЕБОЙНЫЙ ФИКС HTTPS
class ForceHTTPSMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            headers = dict(scope.get("headers", []))
            host = headers.get(b"host", b"").decode("latin-1")
            
            # Если домен НЕ начинается с localhost или 127.0.0.1 (значит это ngrok или сервер)
            # Жестко включаем генерацию HTTPS ссылок
            if not host.startswith("localhost") and not host.startswith("127.0.0.1"):
                scope["scheme"] = "https"
                
        await self.app(scope, receive, send)

app.add_middleware(ForceHTTPSMiddleware)

# Подключаем админку
setup_admin(app)

@app.get("/", response_class=HTMLResponse)
async def root():
    return "Всё работает <br><br><a href='/admin'>/admin</a>"