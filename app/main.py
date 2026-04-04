import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import public
# 1. Добавляем импорт нашей функции
from app.admin import setup_admin 

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

app = FastAPI(title="IT BGITU Remake")

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# --- Middleware для статики и шаблонов ---
if os.path.isdir("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

if os.path.isdir("app/uploads"):
    app.mount("/media", StaticFiles(directory="app/uploads"), name="upload")

if not os.path.isdir("app/templates"):
    os.makedirs("app/templates")

templates = Jinja2Templates(directory="app/templates")

# 2. Инициализируем админку (лучше делать это до подключения роутеров)
admin = setup_admin(app)

# --- Подключение роутеров ---
app.include_router(public.router)

@app.get("/")
async def read_root(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception:
        return {"status": "IT BGITU Remake is running", "message": "index.html not found"}

@app.get("/api/debug-headers")
async def debug_headers(request: Request):
    return {
        "scheme": request.url.scheme, # Что думает приложение: http или https?
        "headers": dict(request.headers) # Какие заголовки дошли?
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)