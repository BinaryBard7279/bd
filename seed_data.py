import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.security import get_password_hash
from app.models import (
    User, EquipmentType, EquipmentModel, EquipmentUnit,
    System, DefectType, DefectTypeSystem, Defect, 
    ScheduledMaintenance, DefectMedia, DefectStatusHistory
)

async def seed():
    async with AsyncSessionLocal() as session:
        try:
            print("Очистка старых данных...")
            await session.execute(text("TRUNCATE TABLE defect_status_history, defect_media, defects, scheduled_maintenance, equipment_units, equipment_models, equipment_types, defect_type_systems, defect_types, systems, users RESTART IDENTITY CASCADE"))
            await session.commit()
        except Exception as e:
            print(f"Ошибка при очистке: {e}")
            await session.rollback()

        print("Загрузка эталонной базы данных со всеми связями...")

        # 1. Пользователи (Все роли из CheckConstraint)
        users = [
            User(username="admin", full_name="Иванов И.И. (Админ)", role="admin", department="Управление", hashed_password=get_password_hash("admin")),
            User(username="mechanic_1", full_name="Петров П.П. (Старший механик)", role="mechanic", department="РММ №1", hashed_password=get_password_hash("123")),
            User(username="mechanic_2", full_name="Сидоров С.С. (Слесарь-гидравлик)", role="mechanic", department="РММ №1", hashed_password=get_password_hash("123")),
            User(username="driver_1", full_name="Смирнов А.А. (Водитель КАМАЗа)", role="driver", department="Автоколонна №1", hashed_password=get_password_hash("123")),
            User(username="driver_2", full_name="Кузнецов В.В. (Машинист экскаватора)", role="driver", department="Участок механизации", hashed_password=get_password_hash("123")),
            User(username="foreman_1", full_name="Михайлов М.М. (Мастер смены)", role="foreman", department="Управление производством", hashed_password=get_password_hash("123"))
        ]
        session.add_all(users)
        await session.flush()

        # 2. Типы техники
        types = [
            EquipmentType(name="Самосвал", description="Транспортировка сыпучих строительных и промышленных грузов"),
            EquipmentType(name="Экскаватор", description="Гусеничная карьерная и строительная землеройная техника"),
            EquipmentType(name="Бульдозер", description="Послойная разработка и перемещение грунтов"),
            EquipmentType(name="Грейдер", description="Профилирование и планировка дорожного полотна"),
            EquipmentType(name="Автокран", description="Погрузочно-разгрузочные и монтажные работы")
        ]
        session.add_all(types)
        await session.flush()

        # 3. Модели техники (Соблюдаем uq_equipment_model_name)
        models = [
            EquipmentModel(name="КАМАЗ-65115", manufacturer="КАМАЗ", type_id=types[0].id, typical_lifespan_hours=10000),
            EquipmentModel(name="Volvo EC220", manufacturer="Volvo", type_id=types[1].id, typical_lifespan_hours=15000),
            EquipmentModel(name="CAT D9", manufacturer="Caterpillar", type_id=types[2].id, typical_lifespan_hours=20000),
            EquipmentModel(name="ДЗ-98", manufacturer="ЧСДМ", type_id=types[3].id, typical_lifespan_hours=12000),
            EquipmentModel(name="КС-45717", manufacturer="Ивановец", type_id=types[4].id, typical_lifespan_hours=15000)
        ]
        session.add_all(models)
        await session.flush()

        # 4. Единицы техники (Парк машин во всех статусах из CheckConstraint)
        units = [
            EquipmentUnit(model_id=models[0].id, reg_number="А001АА77", vin="VIN00000000000001", manufacture_year=2020, current_hours=Decimal("2500.50"), status="active", purchase_date=datetime(2021, 1, 15).date()),
            EquipmentUnit(model_id=models[1].id, reg_number="В002ВВ77", vin="VIN00000000000002", manufacture_year=2021, current_hours=Decimal("1200.00"), status="active", purchase_date=datetime(2021, 6, 20).date()),
            EquipmentUnit(model_id=models[2].id, reg_number="С003СС77", vin="VIN00000000000003", manufacture_year=2019, current_hours=Decimal("5680.15"), status="repair", purchase_date=datetime(2019, 11, 2).date()),
            EquipmentUnit(model_id=models[3].id, reg_number="Е004ЕЕ77", vin="VIN00000000000004", manufacture_year=2018, current_hours=Decimal("8420.00"), status="maintenance", purchase_date=datetime(2018, 5, 14).date()),
            EquipmentUnit(model_id=models[4].id, reg_number="К005КК77", vin="VIN00000000000005", manufacture_year=2022, current_hours=Decimal("510.30"), status="decommissioned", purchase_date=datetime(2022, 3, 10).date())
        ]
        session.add_all(units)
        await session.flush()

        # 5. Иерархическая структура систем и узлов (parent_system_id)
        sys_engine = System(name="Двигатель")
        sys_hydraulics = System(name="Гидравлика")
        sys_tracks = System(name="Ходовая часть")
        sys_electric = System(name="Электрика")
        sys_brakes = System(name="Тормозная система")
        session.add_all([sys_engine, sys_hydraulics, sys_tracks, sys_electric, sys_brakes])
        await session.flush()

        # Дочерние узлы для демонстрации вложенности
        sys_fuel = System(name="Топливная система (ДВС)", parent_system_id=sys_engine.id)
        sys_cylinders = System(name="Гидроцилиндры стрелы", parent_system_id=sys_hydraulics.id)
        session.add_all([sys_fuel, sys_cylinders])
        await session.flush()

        # 6. Справочник дефектов (Критичность и Приоритеты из ограничений)
        defects_types = [
            DefectType(name="Утечка моторного масла", severity_level=2, repair_priority="medium", typical_repair_cost=Decimal("5500.00")),
            DefectType(name="Падение давления в рампе", severity_level=4, repair_priority="high", typical_repair_cost=Decimal("32000.00")),
            DefectType(name="Критический износ траков", severity_level=3, repair_priority="low", typical_repair_cost=Decimal("120000.00")),
            DefectType(name="Замыкание проводки стартера", severity_level=4, repair_priority="critical", typical_repair_cost=Decimal("8500.00")),
            DefectType(name="Отказ пневмоусилителя тормозов", severity_level=5, repair_priority="critical", typical_repair_cost=Decimal("45000.00"))
        ]
        session.add_all(defects_types)
        await session.flush()

        # Связываем типы дефектов с узлами в таблице defect_type_systems (Многие-ко-многим)
        m2m_links = [
            DefectTypeSystem(defect_type_id=defects_types[0].id, system_id=sys_engine.id),
            DefectTypeSystem(defect_type_id=defects_types[1].id, system_id=sys_fuel.id),
            DefectTypeSystem(defect_type_id=defects_types[2].id, system_id=sys_tracks.id),
            DefectTypeSystem(defect_type_id=defects_types[3].id, system_id=sys_electric.id),
            DefectTypeSystem(defect_type_id=defects_types[4].id, system_id=sys_brakes.id)
        ]
        session.add_all(m2m_links)
        await session.flush()

        # 7. Журнал дефектов (Полностью заполненные цепочки полей под разные статусы)
        now_tz = datetime.now(timezone.utc)
        defects = [
            # Дефект 1: В процессе ремонта
            Defect(
                equipment_unit_id=units[0].id, defect_type_id=defects_types[0].id, system_id=sys_engine.id, 
                detected_at=now_tz - timedelta(days=3), detected_by=users[3].id, hours_at_detection=Decimal("2480.00"), 
                status="in_repair", diagnosis="Пробой прокладки поддона картера, требуется замена",
                diagnosed_at=now_tz - timedelta(days=2), diagnosed_by=users[1].id,
                repair_description="Слит остаток масла, демонтирован поддон. Ожидание новой прокладки.",
                repair_cost=Decimal("0.00"), hours_spent_repair=Decimal("1.50")
            ),
            # Дефект 2: Свежий на диагностике
            Defect(
                equipment_unit_id=units[1].id, defect_type_id=defects_types[1].id, system_id=sys_fuel.id, 
                detected_at=now_tz - timedelta(hours=6), detected_by=users[4].id, hours_at_detection=Decimal("1200.00"), 
                status="in_diagnosis", diagnosis="Предположительно забит топливный фильтр тонкой очистки или неисправен ТНВД"
            ),
            # Дефект 3: Полностью закрытый архивный ремонт
            Defect(
                equipment_unit_id=units[2].id, defect_type_id=defects_types[4].id, system_id=sys_brakes.id, 
                detected_at=now_tz - timedelta(days=12), detected_by=users[3].id, hours_at_detection=Decimal("5550.00"), 
                status="closed", diagnosis="Предельный износ фрикционных накладок тормозных колодок заднего моста",
                diagnosed_at=now_tz - timedelta(days=11), diagnosed_by=users[2].id,
                repair_description="Произведена комплексная замена колодок на задней оси, заменены ремкомплекты суппортов, система прокачана.", 
                repaired_at=now_tz - timedelta(days=10), repaired_by=users[1].id,
                repair_cost=Decimal("38400.00"), hours_spent_repair=Decimal("6.50"), 
                closed_at=now_tz - timedelta(days=10), closure_comment="Испытания на стенде пройдены успешно. Тормозной путь в пределах нормы. Техника возвращена на линию."
            )
        ]
        session.add_all(defects)
        await session.flush()

        # 8. Плановое ТО (Календарный график и наработка)
        maintenances = [
            ScheduledMaintenance(equipment_unit_id=units[0].id, maintenance_type="ТО-1 (Квартальное)", planned_date=(now_tz + timedelta(days=5)).date(), planned_hours=Decimal("2600.00"), notes="Замена масла ДВС, масляного и воздушного фильтров, шприцевание узлов трения"),
            ScheduledMaintenance(equipment_unit_id=units[1].id, maintenance_type="ТО-2 (Годовое)", planned_date=(now_tz - timedelta(days=4)).date(), planned_hours=Decimal("1150.00"), actual_date=(now_tz - timedelta(days=4)).date(), actual_hours=Decimal("1148.50"), notes="Выполнено планово в полном объеме регламентных работ"),
            ScheduledMaintenance(equipment_unit_id=units[2].id, maintenance_type="ТО-3 (Комплекс)", planned_date=(now_tz + timedelta(days=20)).date(), planned_hours=Decimal("6000.00"), notes="Плановое инспектирование гидротрансформатора и редукторов"),
            ScheduledMaintenance(equipment_unit_id=units[3].id, maintenance_type="ТО-1", planned_date=(now_tz - timedelta(days=1)).date(), planned_hours=Decimal("8400.00"), actual_date=now_tz.date(), actual_hours=Decimal("8420.00"), notes="Замена элементов гидравлических фильтров высокого давления")
        ]
        session.add_all(maintenances)

        # 9. Фото поломок (Локальные файловые заглушки в папку app/uploads)
        media_files = [
            DefectMedia(defect_id=defects[0].id, file_path="/media/defect_oil_leak.jpg", file_type="jpg", uploaded_at=now_tz - timedelta(days=3), uploaded_by=users[3].id),
            DefectMedia(defect_id=defects[1].id, file_path="/media/defect_fuel_pump.jpg", file_type="jpg", uploaded_at=now_tz - timedelta(hours=5), uploaded_by=users[4].id),
            DefectMedia(defect_id=defects[2].id, file_path="/media/defect_brake_wear.jpg", file_type="jpg", uploaded_at=now_tz - timedelta(days=12), uploaded_by=users[3].id)
        ]
        session.add_all(media_files)

        # 10. Журнал истории изменения статусов (Аудит действий персонала)
        history = [
            # История дефекта №1
            DefectStatusHistory(defect_id=defects[0].id, old_status="open", new_status="in_diagnosis", changed_at=now_tz - timedelta(days=2, hours=4), changed_by=users[1].id),
            DefectStatusHistory(defect_id=defects[0].id, old_status="in_diagnosis", new_status="in_repair", changed_at=now_tz - timedelta(days=1, hours=2), changed_by=users[5].id),
            # История дефекта №2
            DefectStatusHistory(defect_id=defects[1].id, old_status="open", new_status="in_diagnosis", changed_at=now_tz - timedelta(hours=5), changed_by=users[2].id),
            # История дефекта №3
            DefectStatusHistory(defect_id=defects[2].id, old_status="open", new_status="in_repair", changed_at=now_tz - timedelta(days=11), changed_by=users[5].id),
            DefectStatusHistory(defect_id=defects[2].id, old_status="in_repair", new_status="closed", changed_at=now_tz - timedelta(days=10), changed_by=users[0].id)
        ]
        session.add_all(history)

        await session.commit()
        print("Успех! База наполнена идеальными связанными данными.")

if __name__ == "__main__":
    asyncio.run(seed())