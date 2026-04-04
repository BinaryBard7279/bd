from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from app.database import engine
from app.config import settings

# Импортируем все модели
from app.models import (
    User, EquipmentType, EquipmentModel, EquipmentUnit,
    DefectType, System, Defect, DefectMedia, 
    DefectStatusHistory, ScheduledMaintenance
)

# --- АВТОРИЗАЦИЯ (ХАРДКОД) ---
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form.get("username"), form.get("password")

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

# --- ПРЕДСТАВЛЕНИЯ ТАБЛИЦ ---
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.role, User.full_name]
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"

class EquipmentTypeAdmin(ModelView, model=EquipmentType):
    column_list = [EquipmentType.id, EquipmentType.name]
    name_plural = "Типы техники"
    icon = "fa-solid fa-list"

class EquipmentModelAdmin(ModelView, model=EquipmentModel):
    column_list = [EquipmentModel.id, EquipmentModel.name, EquipmentModel.manufacturer]
    name_plural = "Модели техники"
    icon = "fa-solid fa-truck-tractor"

class EquipmentUnitAdmin(ModelView, model=EquipmentUnit):
    column_list = [EquipmentUnit.id, EquipmentUnit.reg_number, EquipmentUnit.vin, EquipmentUnit.status]
    name_plural = "Парк техники"
    icon = "fa-solid fa-truck"

class SystemAdmin(ModelView, model=System):
    column_list = [System.id, System.name]
    name_plural = "Узлы и системы"
    icon = "fa-solid fa-cogs"

class DefectTypeAdmin(ModelView, model=DefectType):
    column_list = [DefectType.id, DefectType.name, DefectType.severity_level]
    name_plural = "Справочник дефектов"
    icon = "fa-solid fa-book-dead"

class DefectAdmin(ModelView, model=Defect):
    column_list = [Defect.id, Defect.equipment_unit_id, Defect.status, Defect.detected_at]
    name_plural = "Журнал дефектов"
    icon = "fa-solid fa-wrench"

class DefectMediaAdmin(ModelView, model=DefectMedia):
    column_list = [DefectMedia.id, DefectMedia.defect_id, DefectMedia.file_type]
    name_plural = "Медиафайлы"
    icon = "fa-solid fa-images"

class DefectStatusHistoryAdmin(ModelView, model=DefectStatusHistory):
    column_list = [DefectStatusHistory.id, DefectStatusHistory.defect_id, DefectStatusHistory.new_status]
    name_plural = "История статусов"
    icon = "fa-solid fa-history"

class ScheduledMaintenanceAdmin(ModelView, model=ScheduledMaintenance):
    column_list = [ScheduledMaintenance.id, ScheduledMaintenance.equipment_unit_id, ScheduledMaintenance.maintenance_type]
    name_plural = "Плановое ТО"
    icon = "fa-solid fa-calendar-check"

# --- ИНИЦИАЛИЗАЦИЯ ---
def setup_admin(app):
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="Управление автопарком",
        base_url="/admin"
    )
    
    # Регистрируем вкладки
    admin.add_view(DefectAdmin)
    admin.add_view(ScheduledMaintenanceAdmin)
    admin.add_view(EquipmentUnitAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(EquipmentTypeAdmin)
    admin.add_view(EquipmentModelAdmin)
    admin.add_view(SystemAdmin)
    admin.add_view(DefectTypeAdmin)
    admin.add_view(DefectMediaAdmin)
    admin.add_view(DefectStatusHistoryAdmin)
    
    return admin