import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.admin import setup_admin

app = FastAPI(title="API")

# 1. Доверяем заголовкам (в паре с флагом в Dockerfile это заработает)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 2. Жесткий фикс схемы для всех запросов за прокси
class ForceHTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.headers.get("x-forwarded-proto") == "https":
            request.scope["scheme"] = "https"
        return await call_next(request)

app.add_middleware(ForceHTTPSMiddleware)

setup_admin(app)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    Всё работает <br><br>
    <a href='/admin'>/admin</a> для управления базой данных.
    """