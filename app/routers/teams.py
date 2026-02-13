from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Team, TeamPick, Entry, User, League
from app.schemas import TeamCreate, TeamResponse, TeamUpdate
from app.auth import get_current_user
from app.mock_data import get_mock_player

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_data: TeamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a team with 5 players for an entry"""
    # Verify entry exists and belongs to current user
    entry = db.query(Entry).filter(Entry.id == team_data.entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )

    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this entry"
        )

    # Check if team already exists for this entry
    existing_team = db.query(Team).filter(Team.entry_id == team_data.entry_id).first()
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team already exists for this entry"
        )

    # Verify league is still open
    league = db.query(League).filter(League.id == entry.league_id).first()
    if league.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create team, league is no longer open"
        )

    # Verify all players exist (mock data)
    for pick in team_data.picks:
        player = get_mock_player(pick.player_id)
        if not player:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Player with id {pick.player_id} not found"
            )

    # Create team
    team = Team(entry_id=team_data.entry_id)
    db.add(team)
    db.flush()  # Get team.id without committing

    # Create team picks
    for pick in team_data.picks:
        team_pick = TeamPick(
            team_id=team.id,
            player_id=pick.player_id,
            player_category=pick.player_category
        )
        db.add(team_pick)

    # Calculate validity
    db.flush()
    db.refresh(team)
    team.calculate_validity()

    db.commit()
    db.refresh(team)

    return team


@router.get("/entry/{entry_id}", response_model=TeamResponse)
def get_team_by_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team for a specific entry"""
    # Verify entry exists
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )

    # Get team
    team = db.query(Team).filter(Team.entry_id == entry_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found for this entry"
        )

    return team


@router.get("/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """Get a specific team by ID"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    return team


@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    team_update: TeamUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a team (replace all picks)"""
    # Get team
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Verify ownership
    entry = db.query(Entry).filter(Entry.id == team.entry_id).first()
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this team"
        )

    # Verify league is still open
    league = db.query(League).filter(League.id == entry.league_id).first()
    if league.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update team, league is no longer open"
        )

    if team_update.picks is not None:
        # Verify all players exist
        for pick in team_update.picks:
            player = get_mock_player(pick.player_id)
            if not player:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Player with id {pick.player_id} not found"
                )

        # Delete old picks
        db.query(TeamPick).filter(TeamPick.team_id == team_id).delete()

        # Create new picks
        for pick in team_update.picks:
            team_pick = TeamPick(
                team_id=team.id,
                player_id=pick.player_id,
                player_category=pick.player_category
            )
            db.add(team_pick)

        # Recalculate validity
        db.flush()
        db.refresh(team)
        team.calculate_validity()

    db.commit()
    db.refresh(team)

    return team


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Verify ownership
    entry = db.query(Entry).filter(Entry.id == team.entry_id).first()
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this team"
        )

    # Verify league is still open
    league = db.query(League).filter(League.id == entry.league_id).first()
    if league.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete team, league is no longer open"
        )

    db.delete(team)
    db.commit()
    return None
