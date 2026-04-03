import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from app.admin import setup_admin
from app.config import settings

app = FastAPI(title="API")

# 1. Сессии для логина (чтобы пускало в админку)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax"
)

# 2. ЯДЕРНЫЙ ФИКС
# Никаких проверок заголовков. Тупо и жестко форсим HTTPS.
class NuclearHTTPSMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") in ("http", "websocket"):
            scope["scheme"] = "https"  # Ультимативная подмена
        return await self.app(scope, receive, send)

app.add_middleware(NuclearHTTPSMiddleware)

# Инициализация админки
setup_admin(app)

@app.get("/", response_class=HTMLResponse)
async def root():
    return "Всё работает <br><br><a href='/admin'>/admin</a>"