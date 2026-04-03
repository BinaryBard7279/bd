import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.admin import setup_admin
from app.config import settings

app = FastAPI(title="API")

# 1. Тот самый рабочий ProxyHeadersMiddleware из старого проекта
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 2. Тот самый рабочий класс из старого проекта
class ForceHTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        proto = request.headers.get("x-forwarded-proto")
        if proto == "https":
            request.scope["scheme"] = "https"
        return await call_next(request)

app.add_middleware(ForceHTTPSMiddleware)

# 3. Обязательные сессии для логина
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax"
)

setup_admin(app)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    Всё работает <br><br>
    <a href='/admin'>/admin</a> для управления базой данных.
    """