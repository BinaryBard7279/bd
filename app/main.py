import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.admin import setup_admin
from app.routers import public

app = FastAPI(title="IT BGITU")

# --- ЯДЕРНЫЙ ФИКС HTTPS (FORCE) ---
# Этот класс принудительно говорит приложению: "ТЫ НА HTTPS"
class ForceHTTPSMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            scope["scheme"] = "https"
        await self.app(scope, receive, send)

# Добавляем этот фикс В САМОМ КОНЦЕ списка мидлварей (чтобы он был внешним слоем)
# Но сначала добавим сессии для админки
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SECRET_KEY", "super-secret-key"),
    same_site="lax"
)

# ТЕПЕРЬ ДОБАВЛЯЕМ ФОРС HTTPS (ОН ДОЛЖЕН БЫТЬ ПОСЛЕДНИМ В КОДЕ)
app.add_middleware(ForceHTTPSMiddleware)
# ----------------------------------

app.include_router(public.router)
setup_admin(app)