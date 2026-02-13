from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.league import LeagueStatus


class LeagueBase(BaseModel):
    name: str
    tournament_id: int
    entry_fee: float = Field(..., ge=0)
    max_participants: Optional[int] = Field(50, ge=2)


class LeagueCreate(LeagueBase):
    pass


class LeagueUpdate(BaseModel):
    name: Optional[str] = None
    entry_fee: Optional[float] = Field(None, ge=0)
    max_participants: Optional[int] = Field(None, ge=2)
    status: Optional[LeagueStatus] = None


class LeagueResponse(LeagueBase):
    id: int
    creator_id: int
    invitation_code: str
    status: LeagueStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeagueJoin(BaseModel):
    invitation_code: str
