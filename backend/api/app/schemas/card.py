from pydantic import BaseModel, constr, ConfigDict
from datetime import datetime
from typing import List, Optional

class CardVerify(BaseModel):
    card_code: constr(min_length=16, max_length=19)

class CardVerifyResponse(BaseModel):
    valid: bool
    message: str
    card_type: str | None = None
    report_id: str | None = None

class CardCreate(BaseModel):
    count: int
    card_type: str
    valid_days: int
    channel: str = "official"
    remark: Optional[str] = None

class CardInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    card_code: str
    batch_no: str
    card_type: str
    status: int
    expire_at: datetime
    used_at: Optional[datetime] = None
    is_exported: int = 0
    exported_at: Optional[datetime] = None
    batch_remark: Optional[str] = None
    created_at: datetime

class CardListResponse(BaseModel):
    total: int
    items: List[CardInfo]
    page: int
    page_size: int

class CardMarkExport(BaseModel):
    card_ids: List[int]
