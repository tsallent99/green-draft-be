from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum
import secrets


class LeagueStatus(str, enum.Enum):
    OPEN = "open"  # Accepting new entries
    CLOSED = "closed"  # No more entries allowed
    IN_PROGRESS = "in_progress"  # Tournament started
    COMPLETED = "completed"  # Tournament finished


class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)
    entry_fee = Column(Float, nullable=False)  # Price to join
    invitation_code = Column(String, unique=True, index=True, nullable=False)
    status = Column(Enum(LeagueStatus), default=LeagueStatus.OPEN)
    max_participants = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="leagues_created", foreign_keys=[creator_id])
    tournament = relationship("Tournament", back_populates="leagues")
    entries = relationship("Entry", back_populates="league", cascade="all, delete-orphan")
    leaderboard = relationship("Leaderboard", back_populates="league", uselist=False, cascade="all, delete-orphan")

    @staticmethod
    def generate_invitation_code():
        """Generate a unique 8-character invitation code"""
        return secrets.token_urlsafe(6).upper()[:8]
