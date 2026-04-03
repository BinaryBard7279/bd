import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.admin import setup_admin

app = FastAPI(title="API")

# 1. Стандартный прокси-мидлвар
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 2. Магия из старого проекта: принудительный HTTPS
class ForceHTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        proto = request.headers.get("x-forwarded-proto")
        if proto == "https":
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