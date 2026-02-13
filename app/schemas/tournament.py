from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.tournament import TournamentStatus


class TournamentBase(BaseModel):
    name: str
    location: Optional[str] = None
    start_date: datetime
    end_date: datetime


class TournamentCreate(TournamentBase):
    pass


class TournamentUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[TournamentStatus] = None


class TournamentResponse(TournamentBase):
    id: int
    status: TournamentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
