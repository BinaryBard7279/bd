from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint
from app.models.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(200))
    role = Column(String(30)) 
    department = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("role IN ('driver', 'mechanic', 'foreman', 'admin')", name='check_user_role'),
    )