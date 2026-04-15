from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Numeric, Date, DateTime, ForeignKey, SmallInteger, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class DefectType(Base):
    __tablename__ = 'defect_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, unique=True)
    severity_level = Column(SmallInteger)
    repair_priority = Column(String(20))
    typical_repair_cost = Column(Numeric(12, 2))

    __table_args__ = (
        CheckConstraint("severity_level BETWEEN 1 AND 5", name='check_severity_level'),
        CheckConstraint("repair_priority IN ('low', 'medium', 'high', 'critical')", name='check_repair_priority'),
    )

    systems = relationship("DefectTypeSystem", back_populates="defect_type")


class System(Base):
    __tablename__ = 'systems'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    parent_system_id = Column(Integer, ForeignKey('systems.id', ondelete='SET NULL'))

    parent_system = relationship("System", remote_side=[id])
    defect_types = relationship("DefectTypeSystem", back_populates="system")


class DefectTypeSystem(Base):
    __tablename__ = 'defect_type_systems'

    defect_type_id = Column(Integer, ForeignKey('defect_types.id', ondelete='CASCADE'), primary_key=True)
    system_id = Column(Integer, ForeignKey('systems.id', ondelete='CASCADE'), primary_key=True)

    defect_type = relationship("DefectType", back_populates="systems")
    system = relationship("System", back_populates="defect_types")


class Defect(Base):
    __tablename__ = 'defects'

    id = Column(Integer, primary_key=True)
    equipment_unit_id = Column(Integer, ForeignKey('equipment_units.id', ondelete='CASCADE'), nullable=False, index=True)
    defect_type_id = Column(Integer, ForeignKey('defect_types.id', ondelete='RESTRICT'), nullable=False)
    system_id = Column(Integer, ForeignKey('systems.id', ondelete='RESTRICT'), nullable=False)
    
    detected_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    detected_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    hours_at_detection = Column(Numeric(12, 2), nullable=False, index=True)
    
    diagnosis = Column(Text)
    diagnosed_at = Column(DateTime(timezone=True))
    diagnosed_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    
    status = Column(String(20), nullable=False, default='open', index=True)
    
    repair_description = Column(Text)
    repaired_at = Column(DateTime(timezone=True))
    repaired_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    repair_cost = Column(Numeric(12, 2))
    hours_spent_repair = Column(Numeric(10, 2))
    
    closed_at = Column(DateTime(timezone=True))
    closure_comment = Column(Text)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("status IN ('open', 'in_diagnosis', 'waiting_parts', 'in_repair', 'closed', 'write_off')", name='check_defect_status'),
    )

class DefectMedia(Base):
    __tablename__ = 'defect_media'

    id = Column(Integer, primary_key=True)
    defect_id = Column(Integer, ForeignKey('defects.id', ondelete='CASCADE'), nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    uploaded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    uploaded_by = Column(Integer, ForeignKey('users.id'))

class DefectStatusHistory(Base):
    __tablename__ = 'defect_status_history'

    id = Column(Integer, primary_key=True)
    defect_id = Column(Integer, ForeignKey('defects.id', ondelete='CASCADE'), nullable=False)
    old_status = Column(String(20))
    new_status = Column(String(20), nullable=False)
    changed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    changed_by = Column(Integer, ForeignKey('users.id'))

class ScheduledMaintenance(Base):
    __tablename__ = 'scheduled_maintenance'

    id = Column(Integer, primary_key=True)
    equipment_unit_id = Column(Integer, ForeignKey('equipment_units.id', ondelete='CASCADE'), nullable=False)
    maintenance_type = Column(String(50), nullable=False)
    planned_date = Column(Date, nullable=False)
    planned_hours = Column(Numeric(12, 2))
    actual_date = Column(Date)
    actual_hours = Column(Numeric(12, 2))
    notes = Column(Text)