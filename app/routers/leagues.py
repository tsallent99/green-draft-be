from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import League, User, Entry, Leaderboard
from app.models.entry import PaymentStatus
from app.schemas import LeagueCreate, LeagueResponse, LeagueJoin, EntryResponse, LeagueCreateResponse, LeagueJoinResponse
from app.auth import get_current_user
from app.mock_data import get_mock_tournament
from app.services.stripe_service import create_checkout_session

router = APIRouter(prefix="/leagues", tags=["leagues"])


@router.post("", response_model=LeagueCreateResponse, status_code=status.HTTP_201_CREATED)
def create_league(
    league: LeagueCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new league"""
    # Verify tournament exists (mock data)
    tournament = get_mock_tournament(league.tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )

    # Generate unique invitation code
    invitation_code = League.generate_invitation_code()
    while db.query(League).filter(League.invitation_code == invitation_code).first():
        invitation_code = League.generate_invitation_code()

    # Create league
    db_league = League(
        name=league.name,
        creator_id=current_user.id,
        tournament_id=league.tournament_id,
        entry_fee=league.entry_fee,
        max_participants=league.max_participants,
        invitation_code=invitation_code
    )
    db.add(db_league)
    db.commit()
    db.refresh(db_league)

    # Create entry for the league creator with PENDING payment
    creator_entry = Entry(
        user_id=current_user.id,
        league_id=db_league.id,
        payment_status=PaymentStatus.PENDING
    )
    db.add(creator_entry)

    # Create leaderboard for the league
    leaderboard = Leaderboard(league_id=db_league.id)
    db.add(leaderboard)
    db.commit()
    db.refresh(creator_entry)

    # Create Stripe Checkout Session
    checkout_url = create_checkout_session(
        entry_id=creator_entry.id,
        entry_fee=db_league.entry_fee,
        league_name=db_league.name,
        league_id=db_league.id,
    )

    return LeagueCreateResponse(
        league=LeagueResponse.model_validate(db_league),
        checkout_url=checkout_url,
    )


@router.get("", response_model=List[LeagueResponse])
def get_user_leagues(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all leagues created by or joined by the current user"""
    # Leagues created by user
    created_leagues = db.query(League).filter(League.creator_id == current_user.id).all()

    # Leagues joined by user
    entries = db.query(Entry).filter(Entry.user_id == current_user.id).all()
    joined_league_ids = [entry.league_id for entry in entries]
    joined_leagues = db.query(League).filter(League.id.in_(joined_league_ids)).all() if joined_league_ids else []

    # Combine and remove duplicates
    all_leagues = {league.id: league for league in created_leagues + joined_leagues}
    return list(all_leagues.values())


@router.get("/{league_id}", response_model=LeagueResponse)
def get_league(league_id: int, db: Session = Depends(get_db)):
    """Get a specific league by ID"""
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )
    return league


@router.post("/join", response_model=LeagueJoinResponse, status_code=status.HTTP_201_CREATED)
def join_league(
    join_data: LeagueJoin,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join a league using invitation code"""
    # Find league by invitation code
    league = db.query(League).filter(League.invitation_code == join_data.invitation_code).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invitation code"
        )

    # Check if league is open
    if league.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="League is not accepting new entries"
        )

    # Check if user already joined
    existing_entry = db.query(Entry).filter(
        Entry.user_id == current_user.id,
        Entry.league_id == league.id
    ).first()
    if existing_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already joined this league"
        )

    # Check max participants
    current_entries = db.query(Entry).filter(Entry.league_id == league.id).count()
    if current_entries >= league.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="League is full"
        )

    # Create entry with PENDING payment
    entry = Entry(
        user_id=current_user.id,
        league_id=league.id,
        payment_status=PaymentStatus.PENDING
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Create Stripe Checkout Session
    checkout_url = create_checkout_session(
        entry_id=entry.id,
        entry_fee=league.entry_fee,
        league_name=league.name,
        league_id=league.id,
    )

    return LeagueJoinResponse(
        entry=EntryResponse.model_validate(entry),
        checkout_url=checkout_url,
    )


@router.get("/{league_id}/entries", response_model=List[EntryResponse])
def get_league_entries(league_id: int, db: Session = Depends(get_db)):
    """Get all entries for a specific league"""
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )

    entries = db.query(Entry).filter(Entry.league_id == league_id).all()
    return entries


@router.delete("/{league_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_league(
    league_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a league (only creator can delete)"""
    league = db.query(League).filter(League.id == league_id).first()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )

    # Check if current user is the creator
    if league.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the league creator can delete it"
        )

    db.delete(league)
    db.commit()
    return None
