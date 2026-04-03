import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.proxy_headers import ProxyHeadersMiddleware
from app.admin import setup_admin

app = FastAPI(title="API")

# 1. Сначала прокси-заголовки (чтобы FastAPI видел X-Forwarded-Proto)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 2. Фикс схемы (Force HTTPS) — ASGI версия надежнее
@app.middleware("http")
async def https_redirect_middleware(request, call_next):
    # Если Caddy прислал заголовок https, форсим схему
    if request.headers.get("x-forwarded-proto") == "https":
        request.scope["scheme"] = "https"
    return await call_next(request)

# 3. Сессии
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "dev-key"),
    https_only=True,
    same_site="lax"
)

@app.get("/")
async def root():
    return {"message": "API работает. Перейти в админку: /admin"}

# 4. И ТОЛЬКО ТЕПЕРЬ ПОДКЛЮЧАЕМ АДМИНКУ!
setup_admin(app)