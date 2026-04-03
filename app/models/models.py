from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, SmallInteger, DateTime, Date, CheckConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(200))
    role = Column(String(30))
    department = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("role IN ('driver', 'mechanic', 'foreman', 'admin')", name="check_user_role"),
    )

class EquipmentType(Base):
    __tablename__ = "equipment_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    models = relationship("EquipmentModel", back_populates="type")

class EquipmentModel(Base):
    __tablename__ = "equipment_models"
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey("equipment_types.id", ondelete="RESTRICT"), nullable=False)
    name = Column(String(150), nullable=False)
    manufacturer = Column(String(100))
    typical_lifespan_hours = Column(Integer)

    type = relationship("EquipmentType", back_populates="models")
    units = relationship("EquipmentUnit", back_populates="model")

class EquipmentUnit(Base):
    __tablename__ = "equipment_units"
    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey("equipment_models.id", ondelete="RESTRICT"), nullable=False)
    vin = Column(String(50), unique=True)
    reg_number = Column(String(50), unique=True)
    manufacture_year = Column(SmallInteger)
    current_hours = Column(Numeric(12, 2), default=0)
    status = Column(String(20), nullable=False, default='active')
    purchase_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())

    model = relationship("EquipmentModel", back_populates="units")

    __table_args__ = (
        CheckConstraint("status IN ('active', 'maintenance', 'repair', 'decommissioned')", name="check_unit_status"),
    )

class DefectType(Base):
    __tablename__ = "defect_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    severity_level = Column(SmallInteger)
    repair_priority = Column(String(20))
    typical_repair_cost = Column(Numeric(12, 2))

    __table_args__ = (
        CheckConstraint("severity_level BETWEEN 1 AND 5", name="check_severity"),
        CheckConstraint("repair_priority IN ('low', 'medium', 'high', 'critical')", name="check_priority"),
    )

class System(Base):
    __tablename__ = "systems"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    parent_system_id = Column(Integer, ForeignKey("systems.id", ondelete="SET NULL"))

class DefectTypeSystem(Base):
    __tablename__ = "defect_type_systems"
    defect_type_id = Column(Integer, ForeignKey("defect_types.id", ondelete="CASCADE"), nullable=False)
    system_id = Column(Integer, ForeignKey("systems.id", ondelete="CASCADE"), nullable=False)
    __table_args__ = (PrimaryKeyConstraint('defect_type_id', 'system_id'),)

class Defect(Base):
    __tablename__ = "defects"
    id = Column(Integer, primary_key=True)
    equipment_unit_id = Column(Integer, ForeignKey("equipment_units.id", ondelete="CASCADE"), nullable=False)
    defect_type_id = Column(Integer, ForeignKey("defect_types.id", ondelete="RESTRICT"), nullable=False)
    system_id = Column(Integer, ForeignKey("systems.id"), nullable=False)

    detected_at = Column(DateTime, server_default=func.now())
    detected_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    hours_at_detection = Column(Numeric(12, 2), nullable=False)

    diagnosis = Column(Text)
    diagnosed_at = Column(DateTime)
    diagnosed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    status = Column(String(20), nullable=False, default='open')
    repair_description = Column(Text)
    repaired_at = Column(DateTime)
    repaired_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    repair_cost = Column(Numeric(12, 2))
    hours_spent_repair = Column(Numeric(10, 2))

    closed_at = Column(DateTime)
    closure_comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('open', 'in_diagnosis', 'waiting_parts', 'in_repair', 'closed', 'write_off')", name="check_defect_status"),
    )

class DefectMedia(Base):
    __tablename__ = "defect_media"
    id = Column(Integer, primary_key=True)
    defect_id = Column(Integer, ForeignKey("defects.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    uploaded_at = Column(DateTime, server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"))

class ScheduledMaintenance(Base):
    __tablename__ = "scheduled_maintenance"
    id = Column(Integer, primary_key=True)
    equipment_unit_id = Column(Integer, ForeignKey("equipment_units.id", ondelete="CASCADE"), nullable=False)
    maintenance_type = Column(String(50), nullable=False)
    planned_date = Column(Date, nullable=False)
    planned_hours = Column(Numeric(12, 2))
    actual_date = Column(Date)
    actual_hours = Column(Numeric(12, 2))
    notes = Column(Text)


class DefectStatusHistory(Base):
    __tablename__ = "defect_status_history"
    id = Column(Integer, primary_key=True)
    defect_id = Column(Integer, ForeignKey("defects.id", ondelete="CASCADE"), nullable=False)
    old_status = Column(String(20))
    new_status = Column(String(20), nullable=False)
    changed_at = Column(DateTime, server_default=func.now())
    changed_by = Column(Integer, ForeignKey("users.id"))
