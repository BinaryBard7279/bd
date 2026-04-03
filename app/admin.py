from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from app.database import engine
from app.config import settings
from app.models.models import (
    User, EquipmentType, EquipmentModel, EquipmentUnit,
    DefectType, System, DefectTypeSystem, Defect,
    DefectMedia, ScheduledMaintenance, DefectStatusHistory
)

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form.get("username"), form.get("password")
        # ВАЖНО: В будущем замени на проверку из БД
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

# Описываем виды для каждой таблицы
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.role, User.department]
    name = "Пользователь"
    name_plural = "Пользователи"

class EquipmentTypeAdmin(ModelView, model=EquipmentType):
    column_list = "__all__"
    name = "Тип техники"
    name_plural = "Типы техники"

class EquipmentUnitAdmin(ModelView, model=EquipmentUnit):
    column_list = [EquipmentUnit.reg_number, EquipmentUnit.status, EquipmentUnit.current_hours]
    name = "Единица техники"
    name_plural = "Парк техники"

class DefectAdmin(ModelView, model=Defect):
    column_list = [Defect.id, Defect.status, Defect.detected_at]
    name = "Дефект"
    name_plural = "Журнал дефектов"

class EquipmentModelAdmin(ModelView, model=EquipmentModel):
    column_list = "__all__"
    name = "Модель техники"
    name_plural = "Модели техники"

class DefectTypeAdmin(ModelView, model=DefectType):
    column_list = "__all__"
    name = "Вид поломки"
    name_plural = "Виды поломок"

class SystemAdmin(ModelView, model=System):
    column_list = "__all__"
    name = "Узел/Система"
    name_plural = "Системы"

class MaintenanceAdmin(ModelView, model=ScheduledMaintenance):
    column_list = "__all__"
    name = "Плановое ТО"
    name_plural = "График ТО"

class DefectStatusHistoryAdmin(ModelView, model=DefectStatusHistory):
    column_list = "__all__"
    name = "История статусов дефекта"
    name_plural = "Истории статусов дефектов"

class DefectMediaAdmin(ModelView, model=DefectMedia):
    column_list = [DefectMedia.id, DefectMedia.defect_id, DefectMedia.file_path, DefectMedia.uploaded_at]
    name = "Медиа дефекта"
    name_plural = "Медиа файлы"


def setup_admin(app):
    admin = Admin(
        app,
        engine,
        authentication_backend=authentication_backend,
        title="Система учета дефектов",
        base_url="/admin"
    )
    admin.add_view(UserAdmin)
    admin.add_view(EquipmentTypeAdmin)
    admin.add_view(EquipmentModelAdmin)
    admin.add_view(EquipmentUnitAdmin)
    admin.add_view(DefectTypeAdmin)
    admin.add_view(SystemAdmin)
    admin.add_view(DefectAdmin)
    admin.add_view(MaintenanceAdmin)
    admin.add_view(DefectStatusHistoryAdmin)
    admin.add_view(DefectMediaAdmin)


