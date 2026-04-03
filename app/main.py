import os
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from app.admin import setup_admin
from app.routers import public

app = FastAPI(title="IT BGITU")

# Добавляем сессии для админки
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SECRET_KEY", "super-secret-key"),
    same_site="lax",
    https_only=True # Раз уж мы точно на HTTPS, лучше включить это для безопасности сессий
)

app.include_router(public.router)
setup_admin(app)