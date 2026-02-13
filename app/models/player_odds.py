from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class PlayerOdds(Base):
    __tablename__ = "player_odds"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)
    category = Column(Integer, nullable=False)  # 1-5 based on odds
    odds = Column(Float)  # Actual odds value (e.g., 8.5)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ensure a player has only one odds entry per tournament
    __table_args__ = (
        UniqueConstraint('player_id', 'tournament_id', name='_player_tournament_uc'),
    )

    # Relationships
    player = relationship("Player", back_populates="player_odds")
    tournament = relationship("Tournament", back_populates="player_odds")
