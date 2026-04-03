import os
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.admin import setup_admin
from app.routers import public

app = FastAPI(title="IT BGITU")

# 1. Подключаем ProxyHeaders из старого проекта
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 2. Тот самый рабочий класс из старого кода, который решает проблему со стилями sqladmin
class ForceHTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        proto = request.headers.get("x-forwarded-proto")
        if proto == "https":
            request.scope["scheme"] = "https"
        return await call_next(request)

app.add_middleware(ForceHTTPSMiddleware)

# 3. Подключаем сессии
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SECRET_KEY", "super-secret-key"),
    same_site="lax",
    max_age=3600 * 24
)

app.include_router(public.router)
setup_admin(app)