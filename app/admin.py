from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy import select
from app.database import engine, AsyncSessionLocal
from app.config import settings
from app.security import verify_password, create_access_token, decode_access_token, get_password_hash
from markupsafe import Markup
from wtforms import FileField
import os
import uuid

# Импортируем все модели
from app.models import (
    User, EquipmentType, EquipmentModel, EquipmentUnit,
    DefectType, System, Defect, DefectMedia, 
    DefectStatusHistory, ScheduledMaintenance
)

# --- АВТОРИЗАЦИЯ ---
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form.get("username"), form.get("password")

        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()

            if user and verify_password(password, user.hashed_password):
                if user.role != "admin":
                    return False
                
                request.session.update({"admin_user": user.username})
                return True
            
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        username = request.session.get("admin_user")
        if not username:
            return False
        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()
            if not user or user.role != "admin":
                return False
            
        return True

authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)

# --- ПРЕДСТАВЛЕНИЯ ТАБЛИЦ ---

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.role, User.full_name]
    form_columns = [User.username, "hashed_password", User.full_name, User.role, User.department]
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"
    column_labels = {
        "id": "ID", "username": "Логин", "hashed_password": "Новый пароль (если нужно сменить)",
        "full_name": "ФИО сотрудника", "role": "Роль", "department": "Подразделение", "created_at": "Дата регистрации"
    }

    async def on_model_change(self, data: dict, model: User, is_created: bool, request: Request) -> None:
        pwd = data.get("hashed_password")
        if pwd and not str(pwd).startswith("$2b$"):
            data["hashed_password"] = get_password_hash(pwd)
        elif not is_created and not pwd:
            data.pop("hashed_password", None)
        elif is_created and not pwd:
            data["hashed_password"] = get_password_hash("changeme")

class EquipmentTypeAdmin(ModelView, model=EquipmentType):
    column_list = [EquipmentType.id, EquipmentType.name]
    name_plural = "Типы техники"
    icon = "fa-solid fa-list"
    column_labels = {
        "id": "ID", "name": "Название типа", "description": "Краткое описание",
        "models": "Связанные модели техники"
    }

class EquipmentModelAdmin(ModelView, model=EquipmentModel):
    column_list = [EquipmentModel.id, "equipment_type", EquipmentModel.name, EquipmentModel.manufacturer]
    form_columns = ["equipment_type", "name", "manufacturer", "typical_lifespan_hours"]
    name_plural = "Модели техники"
    icon = "fa-solid fa-truck-tractor"
    column_labels = {
        "id": "ID", "type_id": "ID Типа", "equipment_type": "Тип техники", 
        "name": "Наименование модели", "manufacturer": "Завод-изготовитель", 
        "typical_lifespan_hours": "Плановый ресурс (моточасы)",
        "units": "Машины в парке"
    }

class EquipmentUnitAdmin(ModelView, model=EquipmentUnit):
    column_list = [EquipmentUnit.id, "model", EquipmentUnit.reg_number, EquipmentUnit.vin, EquipmentUnit.status]
    form_columns = ["model", "vin", "reg_number", "manufacture_year", "current_hours", "status", "purchase_date"]
    name_plural = "Парк техники"
    icon = "fa-solid fa-truck"
    column_labels = {
        "id": "ID", "model_id": "ID Модели", "model": "Модель", "vin": "VIN номер", 
        "reg_number": "Госномер", "manufacture_year": "Год выпуска", 
        "current_hours": "Наработка (м/ч)", "status": "Текущее состояние", 
        "purchase_date": "Дата ввода в эксплуатацию", "created_at": "Зарегистрировано"
    }

class SystemAdmin(ModelView, model=System):
    column_list = [System.id, System.name, "parent_system"]
    form_columns = ["name", "parent_system"] 
    name_plural = "Узлы и системы"
    icon = "fa-solid fa-cogs"
    column_labels = {
        "id": "ID", "name": "Название узла", "parent_system_id": "ID Родителя", 
        "parent_system": "Родительская система", 
        "defect_types": "Возможные дефекты"
    }

class DefectTypeAdmin(ModelView, model=DefectType):
    column_list = [DefectType.id, DefectType.name, DefectType.severity_level]
    form_columns = ["name", "severity_level", "repair_priority", "typical_repair_cost"]
    name_plural = "Справочник дефектов"
    icon = "fa-solid fa-book-dead"
    column_labels = {
        "id": "ID", "name": "Название неисправности", "severity_level": "Критичность (1-5)", 
        "repair_priority": "Приоритет ремонта", "typical_repair_cost": "Средняя стоимость устранения",
        "systems": "Связанные узлы/системы"
    }

class DefectAdmin(ModelView, model=Defect):
    column_list = [Defect.id, "equipment_unit", Defect.status, Defect.detected_at]
    
    column_details_list = [
        "id", "equipment_unit", "defect_type", "system", "detected_at", "detected_by_user", 
        "hours_at_detection", "diagnosis", "diagnosed_at", "diagnosed_by_user", "status", 
        "repair_description", "repaired_at", "repaired_by_user", "repair_cost", 
        "hours_spent_repair", "closed_at", "closure_comment", "media"
    ]
    
    form_columns = [
        "equipment_unit", "defect_type", "system", "status", "detected_at", "detected_by_user", 
        "hours_at_detection", "diagnosis", "diagnosed_at", "diagnosed_by_user", "repair_description", 
        "repaired_at", "repaired_by_user", "repair_cost", "hours_spent_repair", "closed_at", "closure_comment"
    ]
    
    name_plural = "Журнал дефектов"
    icon = "fa-solid fa-wrench"
    column_labels = {
        "id": "ID", "equipment_unit_id": "ID Техники", "equipment_unit": "Единица техники",
        "defect_type_id": "ID Типа", "defect_type": "Тип поломки",
        "system_id": "ID Узла", "system": "Где обнаружено (система)",
        "detected_at": "Дата обнаружения", "detected_by": "ID Обнаружил", "detected_by_user": "Кто обнаружил",
        "hours_at_detection": "Наработка при поломке",
        "diagnosis": "Результат диагностики", "diagnosed_at": "Дата диагностики", 
        "diagnosed_by": "ID Диагноста", "diagnosed_by_user": "Кто диагностировал",
        "status": "Статус",
        "repair_description": "Описание выполненных работ", "repaired_at": "Дата ремонта",
        "repaired_by": "ID Ремонтника", "repaired_by_user": "Кто ремонтировал",
        "repair_cost": "Затраты на ремонт", "hours_spent_repair": "Затрачено часов на ремонт",
        "closed_at": "Дата закрытия", "closure_comment": "Итоговый комментарий",
        "created_at": "Создано в системе",
        "media": "Прикрепленные фото/видео"
    }

    column_formatters_detail = {
        "media": lambda m, a: Markup("".join([
            f'<a href="{photo.file_path}" target="_blank"><img src="{photo.file_path}" height="150" style="margin:5px; border-radius:5px; border:1px solid #ccc;"></a>' 
            for photo in m.media
        ])) if m.media else "Нет прикрепленных файлов"
    }

class DefectMediaAdmin(ModelView, model=DefectMedia):
    column_list = [DefectMedia.id, "defect", DefectMedia.file_type, "file_path"]
    form_columns = ["defect", "file_path"] 
    form_overrides = {"file_path": FileField}
    name_plural = "Фото и видео поломок"
    icon = "fa-solid fa-images"
    
    column_labels = {
        "id": "ID", "defect_id": "ID Поломки", "defect": "Привязка к дефекту",
        "file_path": "Файл", "file_type": "Формат", "uploaded_at": "Дата загрузки",
        "uploaded_by": "ID Загрузившего", "uploaded_by_user": "Кто загрузил"
    }

    column_formatters = {
        "file_path": lambda m, a: Markup(f'<a href="{m.file_path}" target="_blank"><img src="{m.file_path}" height="50" style="border-radius: 3px;"></a>') if m.file_path else ""
    }

    form_ajax_refs = {
        "defect": {
            "fields": ("id", "diagnosis"),
            "order_by": "id"
        }
    }

    async def on_model_change(self, data: dict, model: DefectMedia, is_created: bool, request: Request) -> None:
        file = data.get("file_path")
        if file and hasattr(file, "filename") and file.filename:
            ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"
            upload_dir = "app/uploads"
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            save_path = os.path.join(upload_dir, filename)
            content = await file.read()
            with open(save_path, "wb") as f:
                f.write(content)
            data["file_path"] = f"/media/{filename}"
            data["file_type"] = ext.replace(".", "").lower()
        else:
            if not is_created:
                data.pop("file_path", None)
            else:
                data.pop("file_path", None)

class DefectStatusHistoryAdmin(ModelView, model=DefectStatusHistory):
    column_list = [DefectStatusHistory.id, "defect", DefectStatusHistory.old_status, DefectStatusHistory.new_status]
    name_plural = "История изменений статуса"
    icon = "fa-solid fa-history"
    column_labels = {
        "id": "ID", "defect_id": "ID Поломки", "defect": "Привязка к дефекту",
        "old_status": "Старый статус", "new_status": "Новый статус",
        "changed_at": "Дата изменения", "changed_by": "ID Кто изменил", "changed_by_user": "Кто изменил"
    }

class ScheduledMaintenanceAdmin(ModelView, model=ScheduledMaintenance):
    column_list = [ScheduledMaintenance.id, "equipment_unit", ScheduledMaintenance.maintenance_type, ScheduledMaintenance.planned_date]
    form_columns = ["equipment_unit", "maintenance_type", "planned_date", "planned_hours", "actual_date", "actual_hours", "notes"]
    name_plural = "Плановое ТО"
    icon = "fa-solid fa-calendar-check"
    column_labels = {
        "id": "ID", "equipment_unit_id": "ID Техники", "equipment_unit": "Единица техники",
        "maintenance_type": "Вид ТО (ТО-1, ТО-2 и т.д.)",
        "planned_date": "Плановая дата", "planned_hours": "Плановая наработка (м/ч)",
        "actual_date": "Фактическая дата", "actual_hours": "Фактическая наработка",
        "notes": "Примечания"
    }

# --- ИНИЦИАЛИЗАЦИЯ ---
def setup_admin(app):
    admin = Admin(
        app=app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="Управление автопарком",
        base_url="/admin"
    )
    
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
