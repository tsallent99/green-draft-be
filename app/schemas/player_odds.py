from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PlayerOddsBase(BaseModel):
    player_id: int
    tournament_id: int
    category: int = Field(..., ge=1, le=5)  # Must be between 1 and 5
    odds: Optional[float] = None


class PlayerOddsCreate(PlayerOddsBase):
    pass


class PlayerOddsUpdate(BaseModel):
    category: Optional[int] = Field(None, ge=1, le=5)
    odds: Optional[float] = None


class PlayerOddsResponse(PlayerOddsBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlayerWithOdds(BaseModel):
    """Player with odds information for a specific tournament"""
    player_id: int
    player_name: str
    category: int
    odds: Optional[float] = None
    country: Optional[str] = None
    world_ranking: Optional[int] = None

    class Config:
        from_attributes = True
