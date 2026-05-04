from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, SmallInteger, JSON, Float
from sqlalchemy.sql import func
from app.db.session import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(String(32), primary_key=True, index=True)
    user_id = Column(String(64), index=True, nullable=False)
    user_name = Column(String(50))
    gender = Column(String(10))
    birthday = Column(DateTime)
    focus_area = Column(String(50))  # 情感/事业/财富
    location = Column(String(100))
    mbti = Column(String(10))
    calendar_type = Column(String(20), default="gregorian")
    zodiac = Column(String(20))
    bazi = Column(String(100))
    bazi_favorable_elements = Column(String(200))
    
    left_hand_image = Column(String(255))
    right_hand_image = Column(String(255))
    
    card_code = Column(String(32), ForeignKey("card_codes.card_code"))
    
    palm_features = Column(JSON)  # Extracted palmistry features
    sections = Column(JSON)       # Structured report sections
    model_name = Column(String(50))
    content = Column(Text)  # Markdown content
    status = Column(SmallInteger, default=0)  # 0: generating, 1: completed, 2: failed
    progress = Column(Integer, default=0)  # 0-100
    progress_desc = Column(String(100))
    error_msg = Column(String(500))
    
    generation_time = Column(Float)  # in seconds
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
