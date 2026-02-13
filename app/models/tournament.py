from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class TournamentStatus(str, enum.Enum):
    UPCOMING = "upcoming"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Masters Tournament"
    location = Column(String)  # e.g., "Augusta National Golf Club"
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(Enum(TournamentStatus), default=TournamentStatus.UPCOMING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    leagues = relationship("League", back_populates="tournament")
    player_odds = relationship("PlayerOdds", back_populates="tournament")
