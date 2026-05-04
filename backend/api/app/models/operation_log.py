from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, BigInteger
from sqlalchemy.sql import func
from app.db.session import Base

class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"))
    operation_type = Column(String(50), nullable=False)
    operation_module = Column(String(50), nullable=False)
    description = Column(Text)
    request_params = Column(JSON)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
