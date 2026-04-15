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
    column_labels = {
        "id": "ID",
        "username": "Логин",
        "full_name": "ФИО сотрудника",
        "role": "Роль",
        "department": "Подразделение",
        "created_at": "Дата регистрации"
    }
    column_descriptions = {
        "role": "driver - водитель, mechanic - слесарь, foreman - мастер, admin - администратор",
        "username": "Имя пользователя для входа в систему"
    }

class EquipmentTypeAdmin(ModelView, model=EquipmentType):
    column_list = [EquipmentType.id, EquipmentType.name]
    name_plural = "Типы техники"
    icon = "fa-solid fa-list"
    column_labels = {
        "id": "ID",
        "name": "Название типа",
        "description": "Краткое описание"
    }
    column_descriptions = {
        "name": "Например: Самосвал, Экскаватор, Бульдозер"
    }

class EquipmentModelAdmin(ModelView, model=EquipmentModel):
    column_list = [EquipmentModel.id, EquipmentModel.name, EquipmentModel.manufacturer]
    name_plural = "Модели техники"
    icon = "fa-solid fa-truck-tractor"
    column_labels = {
        "id": "ID",
        "name": "Наименование модели",
        "manufacturer": "Завод-изготовитель",
        "typical_lifespan_hours": "Плановый ресурс (моточасы)",
        "equipment_type": "Тип техники"
    }
    column_descriptions = {
        "typical_lifespan_hours": "Среднее время работы до списания или кап.ремонта"
    }

class EquipmentUnitAdmin(ModelView, model=EquipmentUnit):
    column_list = [EquipmentUnit.id, EquipmentUnit.reg_number, EquipmentUnit.vin, EquipmentUnit.status]
    name_plural = "Парк техники"
    icon = "fa-solid fa-truck"
    column_labels = {
        "id": "ID",
        "model": "Модель",
        "vin": "VIN номер",
        "reg_number": "Госномер",
        "manufacture_year": "Год выпуска",
        "current_hours": "Наработка (м/ч)",
        "status": "Текущее состояние",
        "purchase_date": "Дата ввода в эксплуатацию"
    }
    column_descriptions = {
        "status": "active - в работе, maintenance - на ТО, repair - в ремонте",
        "current_hours": "Текущее значение счетчика моточасов"
    }

class SystemAdmin(ModelView, model=System):
    column_list = [System.id, System.name]
    name_plural = "Узлы и системы"
    icon = "fa-solid fa-cogs"
    column_labels = {
        "id": "ID",
        "name": "Название узла",
        "parent_system": "Родительская система"
    }
    column_descriptions = {
        "name": "Например: Двигатель, Гидравлика, Ковш"
    }

class DefectTypeAdmin(ModelView, model=DefectType):
    column_list = [DefectType.id, DefectType.name, DefectType.severity_level]
    name_plural = "Справочник дефектов"
    icon = "fa-solid fa-book-dead"
    column_labels = {
        "id": "ID",
        "name": "Название неисправности",
        "severity_level": "Критичность (1-5)",
        "repair_priority": "Приоритет ремонта",
        "typical_repair_cost": "Средняя стоимость устранения"
    }
    column_descriptions = {
        "severity_level": "1 - мелкий дефект, 5 - аварийное состояние",
        "repair_priority": "low - низкий, medium - средний, high - высокий, critical - критический"
    }

class DefectAdmin(ModelView, model=Defect):
    column_list = [Defect.id, Defect.equipment_unit_id, Defect.status, Defect.detected_at]
    name_plural = "Журнал дефектов"
    icon = "fa-solid fa-wrench"
    column_labels = {
        "id": "ID",
        "equipment_unit": "Единица техники",
        "defect_type": "Тип поломки",
        "system": "Где обнаружено (система)",
        "detected_at": "Дата/время обнаружения",
        "detected_by_user": "Кто обнаружил",
        "hours_at_detection": "Наработка на момент поломки",
        "diagnosis": "Результат диагностики",
        "status": "Статус",
        "repair_description": "Описание выполненных работ",
        "repair_cost": "Затраты на ремонт",
        "closed_at": "Дата закрытия",
        "closure_comment": "Итоговый комментарий"
    }
    column_descriptions = {
        "status": "open - открыт, in_repair - в ремонте, closed - устранен"
    }

class DefectMediaAdmin(ModelView, model=DefectMedia):
    column_list = [DefectMedia.id, DefectMedia.defect_id, DefectMedia.file_type]
    name_plural = "Фото и видео поломок"
    icon = "fa-solid fa-images"
    column_labels = {
        "id": "ID",
        "defect_id": "ID поломки",
        "file_path": "Путь к файлу",
        "file_type": "Формат",
        "uploaded_at": "Загружено"
    }

class DefectStatusHistoryAdmin(ModelView, model=DefectStatusHistory):
    column_list = [DefectStatusHistory.id, DefectStatusHistory.defect_id, DefectStatusHistory.new_status]
    name_plural = "История изменений статуса"
    icon = "fa-solid fa-history"
    column_labels = {
        "id": "ID",
        "defect_id": "ID поломки",
        "old_status": "Старый статус",
        "new_status": "Новый статус",
        "changed_at": "Дата изменения"
    }

class ScheduledMaintenanceAdmin(ModelView, model=ScheduledMaintenance):
    column_list = [ScheduledMaintenance.id, ScheduledMaintenance.equipment_unit_id, ScheduledMaintenance.maintenance_type]
    name_plural = "Плановое ТО"
    icon = "fa-solid fa-calendar-check"
    column_labels = {
        "id": "ID",
        "equipment_unit": "Техника",
        "maintenance_type": "Вид ТО (ТО-1, ТО-2 и т.д.)",
        "planned_date": "Плановая дата",
        "planned_hours": "Плановая наработка (м/ч)",
        "actual_date": "Фактическая дата выполнения",
        "actual_hours": "Фактическая наработка",
        "notes": "Примечания"
    }
    column_descriptions = {
        "maintenance_type": "Например: Замена масла, Сезонное обслуживание",
        "planned_hours": "При какой наработке нужно провести ТО"
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