from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, SmallInteger, BigInteger
from sqlalchemy.sql import func
from app.db.session import Base

class CardCode(Base):
    __tablename__ = "card_codes"

    id = Column(BigInteger, primary_key=True, index=True)
    card_code = Column(String(32), unique=True, index=True, nullable=False)
    card_secret = Column(String(255), nullable=False)  # Encrypted
    batch_no = Column(String(50), index=True, nullable=False)
    card_type = Column(String(20), nullable=False)  # month/quarter/year/once
    total_times = Column(Integer, default=1)
    remain_times = Column(Integer, default=1)
    status = Column(SmallInteger, default=0)  # 0: unused, 1: used, 2: expired, 3: invalid
    expire_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime)
    used_by = Column(String(64))  # User ID
    is_exported = Column(SmallInteger, default=0) # 0: no, 1: yes
    exported_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey("admin_users.id"))
    created_at = Column(DateTime, server_default=func.now())
    channel = Column(String(50), index=True)  # Distribution channel
    batch_remark = Column(String(200))        # Remark for this batch
