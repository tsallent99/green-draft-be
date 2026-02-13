from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Leaderboard, League, Entry, User
from app.schemas import LeaderboardResponse, LeaderboardDetailed, RankingEntry
from app.mock_data import get_mock_tournament

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("/{league_id}", response_model=LeaderboardDetailed)
def get_leaderboard(league_id: int, db: Session = Depends(get_db)):
    """Get leaderboard for a specific league"""
    # Get league
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )

    # Get leaderboard
    leaderboard = db.query(Leaderboard).filter(Leaderboard.league_id == league_id).first()
    if not leaderboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leaderboard not found"
        )

    # Get all entries for this league
    entries = db.query(Entry).filter(Entry.league_id == league_id).all()

    # Calculate prizes
    num_entries = len(entries)
    leaderboard.calculate_prizes(num_entries, league.entry_fee)

    # Sort entries by score (descending)
    sorted_entries = sorted(entries, key=lambda e: e.total_score, reverse=True)

    # Build rankings
    rankings = []
    for position, entry in enumerate(sorted_entries, start=1):
        user = db.query(User).filter(User.id == entry.user_id).first()

        # Determine prize
        prize = 0.0
        if position == 1:
            prize = leaderboard.first_place_prize
        elif position == 2:
            prize = leaderboard.second_place_prize
        elif position == 3:
            prize = leaderboard.third_place_prize

        rankings.append(RankingEntry(
            entry_id=entry.id,
            user_id=user.id,
            username=user.username,
            position=position,
            score=entry.total_score,
            prize=prize
        ))

    # Update leaderboard rankings
    leaderboard.rankings = [
        {
            "entry_id": r.entry_id,
            "user_id": r.user_id,
            "username": r.username,
            "position": r.position,
            "score": r.score,
            "prize": r.prize
        }
        for r in rankings
    ]
    db.commit()

    # Get tournament info
    tournament = get_mock_tournament(league.tournament_id)

    return LeaderboardDetailed(
        league_id=league.id,
        league_name=league.name,
        tournament_name=tournament["name"] if tournament else "Unknown",
        prize_pool=leaderboard.prize_pool,
        first_place_prize=leaderboard.first_place_prize,
        second_place_prize=leaderboard.second_place_prize,
        third_place_prize=leaderboard.third_place_prize,
        rankings=rankings,
        last_updated=leaderboard.last_updated
    )


@router.post("/{league_id}/refresh", response_model=LeaderboardResponse)
def refresh_leaderboard(league_id: int, db: Session = Depends(get_db)):
    """Refresh/recalculate leaderboard for a league"""
    # Get league
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )

    # Get leaderboard
    leaderboard = db.query(Leaderboard).filter(Leaderboard.league_id == league_id).first()
    if not leaderboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leaderboard not found"
        )

    # Get all entries
    entries = db.query(Entry).filter(Entry.league_id == league_id).all()

    # Recalculate prizes
    num_entries = len(entries)
    leaderboard.calculate_prizes(num_entries, league.entry_fee)

    # Sort entries by score
    sorted_entries = sorted(entries, key=lambda e: e.total_score, reverse=True)

    # Update rankings
    rankings = []
    for position, entry in enumerate(sorted_entries, start=1):
        user = db.query(User).filter(User.id == entry.user_id).first()

        prize = 0.0
        if position == 1:
            prize = leaderboard.first_place_prize
        elif position == 2:
            prize = leaderboard.second_place_prize
        elif position == 3:
            prize = leaderboard.third_place_prize

        rankings.append({
            "entry_id": entry.id,
            "user_id": user.id,
            "username": user.username,
            "position": position,
            "score": entry.total_score,
            "prize": prize
        })

    leaderboard.rankings = rankings
    db.commit()
    db.refresh(leaderboard)

    return leaderboard
