from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, SmallInteger
from sqlalchemy.sql import func
from app.db.session import Base

class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, index=True, nullable=False)
    config_value = Column(Text)
    config_type = Column(String(20), default="string")  # string/number/boolean/json
    description = Column(String(200))
    is_encrypted = Column(SmallInteger, default=0)
    updated_by = Column(Integer, ForeignKey("admin_users.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
