from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, SmallInteger, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class EquipmentType(Base):
    __tablename__ = 'equipment_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

    models = relationship("EquipmentModel", back_populates="equipment_type")


class EquipmentModel(Base):
    __tablename__ = 'equipment_models'

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('equipment_types.id', ondelete='RESTRICT'), nullable=False)
    name = Column(String(150), nullable=False)
    manufacturer = Column(String(100))
    typical_lifespan_hours = Column(Integer)

    __table_args__ = (
        UniqueConstraint('type_id', 'name', name='uq_equipment_model_name'),
    )

    equipment_type = relationship("EquipmentType", back_populates="models")
    units = relationship("EquipmentUnit", back_populates="model")


class EquipmentUnit(Base):
    __tablename__ = 'equipment_units'

    id = Column(Integer, primary_key=True)
    model_id = Column(Integer, ForeignKey('equipment_models.id', ondelete='RESTRICT'), nullable=False)
    vin = Column(String(50), unique=True)
    reg_number = Column(String(50), unique=True)
    manufacture_year = Column(SmallInteger)
    current_hours = Column(Numeric(12, 2), default=0)
    status = Column(String(20), nullable=False, default='active')
    purchase_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("status IN ('active', 'maintenance', 'repair', 'decommissioned')", name='check_equipment_status'),
    )

    model = relationship("EquipmentModel", back_populates="units")