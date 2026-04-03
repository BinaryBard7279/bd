import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from app.admin import setup_admin

app = FastAPI(title="API")

# 1. Сначала базовые настройки
setup_admin(app)

@app.get("/", response_class=HTMLResponse)
async def root():
    return "Всё работает. <a href='/admin'>Перейти в админку</a>"

# 2. Настраиваем сессии (обязательно ДО форсирования HTTPS)
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-key-for-dev")
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=True,
    same_site="lax"
)

# 3. Доверяем заголовкам прокси
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# 4. КРИТИЧЕСКИЙ ФИКС: Принудительный HTTPS
# Эта мидлварь добавлена последней, значит она сработает ПЕРВОЙ.
class ForceHTTPSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Если Caddy говорит, что пришел HTTPS, или если мы на порту 443
        proto = request.headers.get("x-forwarded-proto")
        if proto == "https":
            request.scope["scheme"] = "https"
        
        # Для sqladmin важно, чтобы ссылки генерировались сразу с https
        if "vinogradovnikita.ru" in request.url.netloc:
             request.scope["scheme"] = "https"
             
        return await call_next(request)

app.add_middleware(ForceHTTPSMiddleware)