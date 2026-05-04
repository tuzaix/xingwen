from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, SmallInteger
from sqlalchemy.sql import func
from app.db.session import Base

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    real_name = Column(String(50), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    role_id = Column(Integer, ForeignKey("admin_roles.id"))
    status = Column(SmallInteger, default=1)  # 1: active, 0: disabled
    last_login_at = Column(DateTime)
    last_login_ip = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class AdminRole(Base):
    __tablename__ = "admin_roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    permissions = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
