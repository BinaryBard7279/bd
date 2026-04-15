import asyncio
from decimal import Decimal
from datetime import datetime, date, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, engine
from app.security import get_password_hash
from app.models import (
    User, EquipmentType, EquipmentModel, EquipmentUnit,
    System, DefectType, Defect
)

async def seed():
    async with AsyncSessionLocal() as session:
        # 1. Пользователи
        admin = User(
            username="admin", 
            full_name="Иванов Иван Иванович", 
            role="admin", 
            department="Управление",
            hashed_password=get_password_hash("admin")
        )
        mechanic = User(
            username="mechanic_petr", 
            full_name="Петров Петр Петрович", 
            role="mechanic", 
            department="РММ",
            hashed_password=get_password_hash("12345")
        )
        driver = User(
            username="driver_sergey", 
            full_name="Сидоров Сергей", 
            role="driver", 
            department="Автоколонна №1",
            hashed_password=get_password_hash("12345")
        )
        
        session.add_all([admin, mechanic, driver])
        await session.flush()

        # 2. Типы и модели техники
        truck_type = EquipmentType(name="Самосвал", description="Грузовая техника для перевозки сыпучих грузов")
        excavator_type = EquipmentType(name="Экскаватор", description="Землеройная техника")
        session.add_all([truck_type, excavator_type])
        await session.flush()

        kamaz = EquipmentModel(name="KAMAZ-65115", manufacturer="КАМАЗ", equipment_type=truck_type, typical_lifespan_hours=10000)
        volvo = EquipmentModel(name="Volvo EC220DL", manufacturer="Volvo", equipment_type=excavator_type, typical_lifespan_hours=15000)
        session.add_all([kamaz, volvo])
        await session.flush()

        # 3. Единицы техники
        unit1 = EquipmentUnit(model=kamaz, reg_number="А001АА77", vin="KMZ65115X12345678", manufacture_year=2022, current_hours=1250.5, status="active")
        unit2 = EquipmentUnit(model=volvo, reg_number="Е999КХ99", vin="VLVEC220X87654321", manufacture_year=2021, current_hours=3400, status="active")
        session.add_all([unit1, unit2])
        await session.flush()

        # 4. Узлы и системы
        engine_sys = System(name="Двигатель")
        hydraulics_sys = System(name="Гидравлика")
        session.add_all([engine_sys, hydraulics_sys])
        await session.flush()

        # 5. Справочник дефектов
        oil_leak = DefectType(name="Утечка масла", severity_level=2, repair_priority="medium")
        low_power = DefectType(name="Потеря мощности", severity_level=3, repair_priority="high")
        session.add_all([oil_leak, low_power])
        await session.flush()

        # 6. Пример дефекта
        defect1 = Defect(
            equipment_unit_id=unit1.id,
            defect_type_id=oil_leak.id,
            system_id=engine_sys.id,
            detected_at=datetime.now(timezone.utc) - timedelta(days=1),
            detected_by=driver.id,
            hours_at_detection=1248,
            status="open",
            diagnosis="Течь прокладки клапанной крышки"
        )
        session.add(defect1)
        
        await session.commit()
        print("Тестовые данные успешно загружены!")

if __name__ == "__main__":
    asyncio.run(seed())
