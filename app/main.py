import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

from app.admin import setup_admin
from app.config import settings

app = FastAPI(title="API")

# 1. СЕССИИ: Обязательно для работы авторизации в sqladmin
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax"
)

# 2. ЖЕЛЕЗОБЕТОННЫЙ ФИКС HTTPS: Только такой класс на низком уровне
# заставит sqladmin поверить, что мы на HTTPS, и отдать правильные стили.
class PureProxyFixMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] in ("http", "websocket"):
            headers = dict(scope.get("headers", []))
            # Caddy и Ngrok присылают этот заголовок
            if b"x-forwarded-proto" in headers:
                scope["scheme"] = headers[b"x-forwarded-proto"].decode("latin-1")
        await self.app(scope, receive, send)

app.add_middleware(PureProxyFixMiddleware)

# Подключаем админку
setup_admin(app)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    Всё работает <br><br>
    <a href='/admin'>/admin</a> для управления базой данных.
    """