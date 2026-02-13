from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class TeamPick(Base):
    __tablename__ = "team_picks"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    player_category = Column(Integer, nullable=False)  # Category at time of selection (1-5)
    player_score = Column(Float, default=0.0)  # Player's score in the tournament
    created_at = Column(DateTime, default=datetime.utcnow)

    # A player can only be picked once per team
    __table_args__ = (
        UniqueConstraint('team_id', 'player_id', name='_team_player_uc'),
    )

    # Relationships
    team = relationship("Team", back_populates="picks")
    player = relationship("Player", back_populates="team_picks")
