import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.routers import public
from app.admin import setup_admin 
from app.config import settings
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

app = FastAPI(title="Управление автопарком")

# Сессии для админки (нужны для аутентификации)
app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.SECRET_KEY, 
    same_site="lax"
)

# Защита от Mixed Content при работе за Caddy
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# Раздача медиафайлов (пригодится для фоток дефектов)
if not os.path.isdir("app/uploads"):
    os.makedirs("app/uploads")
app.mount("/media", StaticFiles(directory="app/uploads"), name="upload")

# Инициализируем админку
admin = setup_admin(app)

# Подключаем роутеры (API)
app.include_router(public.router)

@app.get("/fix-admin", include_in_schema=False)
async def fix_admin():
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models.users import User
    from app.security import get_password_hash
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        user = result.scalar_one_or_none()
        if user:
            user.hashed_password = get_password_hash("admin")
            await session.commit()
            return {"status": "Admin password updated to 'admin'"}
        return {"status": "Admin user not found"}

# Прямой редирект в админку с главной страницы
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/admin")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)