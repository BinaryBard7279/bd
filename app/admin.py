from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from app.database import engine
from app.config import settings

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form.get("username"), form.get("password")

        # ВНИМАНИЕ: хардкод! Позже заменим на проверку по базе данных
        if username == "admin" and password == "admin":
            request.session.update({"token": "admin_token"})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "token" in request.session

authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)

def setup_admin(app):
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="Админ-панель",
        base_url="/admin"
    )
    
    # Позже будем добавлять модели вот так:
    # admin.add_view(UserAdmin)
    
    return admin