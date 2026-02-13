from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any


class RankingEntry(BaseModel):
    entry_id: int
    user_id: int
    username: str
    position: int
    score: float
    prize: float


class LeaderboardBase(BaseModel):
    league_id: int


class LeaderboardResponse(LeaderboardBase):
    id: int
    rankings: Optional[List[Dict[str, Any]]] = None
    prize_pool: float
    first_place_prize: float
    second_place_prize: float
    third_place_prize: float
    last_updated: datetime

    class Config:
        from_attributes = True


class LeaderboardDetailed(BaseModel):
    """Detailed leaderboard with full ranking information"""
    league_id: int
    league_name: str
    tournament_name: str
    prize_pool: float
    first_place_prize: float
    second_place_prize: float
    third_place_prize: float
    rankings: List[RankingEntry]
    last_updated: datetime

    class Config:
        from_attributes = True
