from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PlayerBase(BaseModel):
    name: str
    country: Optional[str] = None
    world_ranking: Optional[int] = None


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    world_ranking: Optional[int] = None


class PlayerResponse(PlayerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
