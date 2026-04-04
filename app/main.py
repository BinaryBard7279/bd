import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
# Импорт роутеров (убедись, что файлы routers существуют)
from app.routers import public # , auth, cms 

app = FastAPI(title="IT BGITU Remake")

# --- Middleware для статики и шаблонов ---
# Убедись, что папки app/static и app/templates существуют
if os.path.isdir("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

if os.path.isdir("app/uploads"):
    app.mount("/media", StaticFiles(directory="app/uploads"), name="upload")

# Создаем папки если их нет, чтобы шаблоны не падали при инициализации
if not os.path.isdir("app/templates"):
    os.makedirs("app/templates")

templates = Jinja2Templates(directory="app/templates")

# --- Подключение роутеров ---
app.include_router(public.router)
# app.include_router(auth.router)
# app.include_router(cms.router)

# Простой роут для главной страницы (если нет роутера public)
@app.get("/")
async def read_root(request: Request):
    # Пытаемся отдать index.html, если его нет - отдаем JSON
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception:
        return {"status": "IT BGITU Remake is running", "message": "index.html not found in app/templates"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
