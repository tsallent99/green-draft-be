from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.entry import PaymentStatus


class EntryBase(BaseModel):
    user_id: int
    league_id: int


class EntryCreate(BaseModel):
    league_id: int


class EntryUpdate(BaseModel):
    payment_status: Optional[PaymentStatus] = None
    total_score: Optional[float] = None


class EntryResponse(EntryBase):
    id: int
    payment_status: PaymentStatus
    total_score: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
