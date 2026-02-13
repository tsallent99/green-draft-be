from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas import TournamentResponse
from app.mock_data import get_mock_tournaments, get_mock_tournament

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


@router.get("", response_model=List[TournamentResponse])
def get_tournaments():
    """Get all tournaments (mock data)"""
    return get_mock_tournaments()


@router.get("/{tournament_id}", response_model=TournamentResponse)
def get_tournament_by_id(tournament_id: int):
    """Get a specific tournament by ID (mock data)"""
    tournament = get_mock_tournament(tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    return tournament
