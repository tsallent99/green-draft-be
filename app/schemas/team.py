from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional


class TeamPickBase(BaseModel):
    player_id: int
    player_category: int = Field(..., ge=1, le=5)


class TeamPickCreate(TeamPickBase):
    pass


class TeamPickResponse(TeamPickBase):
    id: int
    team_id: int
    player_score: float
    created_at: datetime

    class Config:
        from_attributes = True


class TeamBase(BaseModel):
    entry_id: int


class TeamCreate(BaseModel):
    entry_id: int
    picks: List[TeamPickCreate] = Field(..., min_length=5, max_length=5)

    @field_validator('picks')
    @classmethod
    def validate_picks(cls, v):
        if len(v) != 5:
            raise ValueError('Team must have exactly 5 players')

        # Check sum of categories
        total_category = sum(pick.player_category for pick in v)
        if total_category < 13:
            raise ValueError(f'Sum of player categories must be at least 13, got {total_category}')

        # Check for duplicate players
        player_ids = [pick.player_id for pick in v]
        if len(player_ids) != len(set(player_ids)):
            raise ValueError('Cannot select the same player twice')

        return v


class TeamUpdate(BaseModel):
    picks: Optional[List[TeamPickCreate]] = Field(None, min_length=5, max_length=5)

    @field_validator('picks')
    @classmethod
    def validate_picks(cls, v):
        if v is not None:
            if len(v) != 5:
                raise ValueError('Team must have exactly 5 players')

            total_category = sum(pick.player_category for pick in v)
            if total_category < 13:
                raise ValueError(f'Sum of player categories must be at least 13, got {total_category}')

            player_ids = [pick.player_id for pick in v]
            if len(player_ids) != len(set(player_ids)):
                raise ValueError('Cannot select the same player twice')

        return v


class TeamResponse(TeamBase):
    id: int
    is_valid: bool
    total_category_points: int
    picks: List[TeamPickResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
