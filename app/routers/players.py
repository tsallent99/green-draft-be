from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.schemas import PlayerResponse, PlayerWithOdds
from app.mock_data import (
    get_mock_players,
    get_mock_player,
    get_mock_player_odds,
    get_mock_player_odds_by_category
)

router = APIRouter(prefix="/players", tags=["players"])


@router.get("")
def get_players():
    """Get all players (mock data)"""
    return get_mock_players()


@router.get("/{player_id}")
def get_player_by_id(player_id: int):
    """Get a specific player by ID (mock data)"""
    player = get_mock_player(player_id)
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found"
        )
    return player


@router.get("/odds/{tournament_id}", response_model=List[PlayerWithOdds])
def get_players_with_odds(
    tournament_id: int,
    category: Optional[int] = Query(None, ge=1, le=5, description="Filter by category (1-5)")
):
    """Get players with their odds for a specific tournament (mock data)"""
    # Get player odds for tournament
    if category:
        odds_list = get_mock_player_odds_by_category(tournament_id, category)
    else:
        odds_list = get_mock_player_odds(tournament_id)

    if not odds_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No player odds found for this tournament"
        )

    # Combine player info with odds
    players_with_odds = []
    for odds in odds_list:
        player = get_mock_player(odds["player_id"])
        if player:
            players_with_odds.append({
                "player_id": player["id"],
                "player_name": player["name"],
                "category": odds["category"],
                "odds": odds["odds"],
                "country": player["country"],
                "world_ranking": player["world_ranking"]
            })

    return players_with_odds
