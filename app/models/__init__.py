from app.models.base import Base

# Импортируем все модели из разбитых файлов
from app.models.users import User
from app.models.equipment import EquipmentType, EquipmentModel, EquipmentUnit
from app.models.defects import (
    DefectType, System, DefectTypeSystem, 
    Defect, DefectMedia, DefectStatusHistory, ScheduledMaintenance
)