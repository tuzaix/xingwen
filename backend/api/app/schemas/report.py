from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class ReportCreate(BaseModel):
    name: str
    gender: str
    birthday: str
    focus_area: str
    location: Optional[str] = None
    mbti: Optional[str] = None
    calendar_type: Optional[str] = "gregorian" # gregorian or lunar
    zodiac: Optional[str] = None
    bazi: Optional[str] = None
    bazi_favorable_elements: Optional[str] = None
    left_hand_image: Optional[str] = None
    right_hand_image: Optional[str] = None
    card_code: str

class ReportResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()
    )

    id: str
    user_id: str
    user_name: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[datetime] = None
    focus_area: Optional[str] = None
    location: Optional[str] = None
    mbti: Optional[str] = None
    calendar_type: Optional[str] = None
    zodiac: Optional[str] = None
    bazi: Optional[str] = None
    bazi_favorable_elements: Optional[str] = None
    left_hand_image: Optional[str] = None
    right_hand_image: Optional[str] = None
    card_code: Optional[str] = None
    palm_features: Optional[dict] = None
    sections: Optional[list] = None
    model_name: Optional[str] = None
    content: Optional[str] = None
    status: int
    progress: Optional[int] = 0
    progress_desc: Optional[str] = None
    error_msg: Optional[str] = None
    generation_time: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class ReportListResponse(BaseModel):
    total: int
    items: list[ReportResponse]
    page: int
    page_size: int
