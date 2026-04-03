import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.admin import setup_admin
from app.routers import public

app = FastAPI(title="IT BGITU")

# 1. ЖЕЛЕЗОБЕТОННЫЙ ФИКС: Учим FastAPI доверять заголовкам от Caddy
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 2. Сессии для админки
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SECRET_KEY", "super-secret-key"),
    same_site="lax"
)

app.include_router(public.router)
setup_admin(app)