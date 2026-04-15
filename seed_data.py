import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.database import AsyncSessionLocal
from app.security import get_password_hash
from app.models import (
    User, EquipmentType, EquipmentModel, EquipmentUnit,
    System, DefectType, Defect
)

async def seed():
    async with AsyncSessionLocal() as session:
        try:
            # 0. Очищаем базу от старых тестовых данных (чтобы не было конфликтов уникальности)
            print("Очистка старых данных...")
            await session.execute(text("TRUNCATE TABLE defect_status_history, defect_media, defects, scheduled_maintenance, equipment_units, equipment_models, equipment_types, defect_type_systems, defect_types, systems, users RESTART IDENTITY CASCADE"))
            await session.commit()
        except Exception as e:
            print(f"Ошибка при очистке (возможно база уже пуста): {e}")
            await session.rollback()

        print("Загрузка новых данных (по 5+ вариантов)...")

        # 1. Пользователи (6 штук разных ролей)
        users = [
            User(username="admin", full_name="Иванов И.И. (Админ)", role="admin", department="Управление", hashed_password=get_password_hash("admin")),
            User(username="mechanic_1", full_name="Петров П.П. (Механик 1)", role="mechanic", department="РММ", hashed_password=get_password_hash("123")),
            User(username="mechanic_2", full_name="Сидоров С.С. (Механик 2)", role="mechanic", department="РММ", hashed_password=get_password_hash("123")),
            User(username="driver_1", full_name="Смирнов А.А. (Водитель 1)", role="driver", department="Колонна 1", hashed_password=get_password_hash("123")),
            User(username="driver_2", full_name="Кузнецов В.В. (Водитель 2)", role="driver", department="Колонна 2", hashed_password=get_password_hash("123")),
            User(username="foreman_1", full_name="Михайлов М.М. (Мастер)", role="foreman", department="Мастера", hashed_password=get_password_hash("123"))
        ]
        session.add_all(users)
        await session.flush()

        # 2. Типы техники (5 штук)
        types = [
            EquipmentType(name="Самосвал", description="Перевозка сыпучих грузов"),
            EquipmentType(name="Экскаватор", description="Землеройные работы"),
            EquipmentType(name="Бульдозер", description="Планировка грунта"),
            EquipmentType(name="Грейдер", description="Профилирование дорог"),
            EquipmentType(name="Автокран", description="Погрузочно-разгрузочные работы")
        ]
        session.add_all(types)
        await session.flush()

        # 3. Модели техники (5 штук)
        models = [
            EquipmentModel(name="КАМАЗ-65115", manufacturer="КАМАЗ", type_id=types[0].id, typical_lifespan_hours=10000),
            EquipmentModel(name="Volvo EC220", manufacturer="Volvo", type_id=types[1].id, typical_lifespan_hours=15000),
            EquipmentModel(name="CAT D9", manufacturer="Caterpillar", type_id=types[2].id, typical_lifespan_hours=20000),
            EquipmentModel(name="ДЗ-98", manufacturer="ЧСДМ", type_id=types[3].id, typical_lifespan_hours=12000),
            EquipmentModel(name="КС-45717", manufacturer="Ивановец", type_id=types[4].id, typical_lifespan_hours=15000)
        ]
        session.add_all(models)
        await session.flush()

        # 4. Единицы техники (5 штук)
        units = [
            EquipmentUnit(model_id=models[0].id, reg_number="А001АА77", vin="VIN00000000000001", manufacture_year=2020, current_hours=2500, status="active"),
            EquipmentUnit(model_id=models[1].id, reg_number="В002ВВ77", vin="VIN00000000000002", manufacture_year=2021, current_hours=1200, status="active"),
            EquipmentUnit(model_id=models[2].id, reg_number="С003СС77", vin="VIN00000000000003", manufacture_year=2019, current_hours=5600, status="active"),
            EquipmentUnit(model_id=models[3].id, reg_number="Е004ЕЕ77", vin="VIN00000000000004", manufacture_year=2018, current_hours=8400, status="maintenance"),
            EquipmentUnit(model_id=models[4].id, reg_number="К005КК77", vin="VIN00000000000005", manufacture_year=2022, current_hours=500, status="active")
        ]
        session.add_all(units)
        await session.flush()

        # 5. Системы и узлы (5 штук)
        systems = [
            System(name="Двигатель"),
            System(name="Гидравлика"),
            System(name="Ходовая часть"),
            System(name="Электрика"),
            System(name="Тормозная система")
        ]
        session.add_all(systems)
        await session.flush()

        # 6. Типы дефектов (5 штук)
        defects_types = [
            DefectType(name="Утечка масла", severity_level=2, repair_priority="medium", typical_repair_cost=5000),
            DefectType(name="Потеря мощности", severity_level=3, repair_priority="high", typical_repair_cost=15000),
            DefectType(name="Износ гусениц", severity_level=2, repair_priority="low", typical_repair_cost=80000),
            DefectType(name="Короткое замыкание", severity_level=4, repair_priority="critical", typical_repair_cost=10000),
            DefectType(name="Отказ тормозов", severity_level=5, repair_priority="critical", typical_repair_cost=25000)
        ]
        session.add_all(defects_types)
        await session.flush()

        # 7. Журнал дефектов (пара примеров для старта)
        defects = [
            Defect(equipment_unit_id=units[0].id, defect_type_id=defects_types[0].id, system_id=systems[0].id, detected_at=datetime.now(timezone.utc), detected_by=users[3].id, hours_at_detection=2500, status="open", diagnosis="Подтекает сальник коленвала"),
            Defect(equipment_unit_id=units[1].id, defect_type_id=defects_types[1].id, system_id=systems[1].id, detected_at=datetime.now(timezone.utc), detected_by=users[4].id, hours_at_detection=1200, status="in_diagnosis", diagnosis="Проверить давление в гидросистеме")
        ]
        session.add_all(defects)

        await session.commit()
        print("Успех! База заполнена: по 5 вариантов в каждом справочнике.")

if __name__ == "__main__":
    asyncio.run(seed())
