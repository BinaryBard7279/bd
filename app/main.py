import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.admin import setup_admin
from app.routers import public

app = FastAPI(title="IT BGITU")

# 1. Доверие к Caddy (чтобы работали стили)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 2. Сессии (нужны только чтобы логин в админку работал)
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SECRET_KEY", "simple-key"),
    same_site="lax"
)

# 3. Роуты и админка
app.include_router(public.router)
setup_admin(app)