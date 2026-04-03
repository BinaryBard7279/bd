from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.admin import setup_admin
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

app = FastAPI(title="API")

# Добавляем middleware для обработки заголовков прокси (X-Forwarded-Proto и т.д.)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

# Дополнительный middleware для принудительной установки схемы https, 
# если прокси сообщает, что запрос пришел по HTTPS. 
# Это решает проблему Mixed Content (content mix) в SQLAdmin и редиректах.
@app.middleware("http")
async def set_https_scheme(request: Request, call_next):
    if request.headers.get("x-forwarded-proto") == "https":
        request.scope["scheme"] = "https"
    response = await call_next(request)
    return response

setup_admin(app)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    Всё работает <br><br>
    <a href='/admin'>/admin</a> для управления базой данных.
    """