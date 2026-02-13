from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("entries.id"), nullable=False, unique=True)
    is_valid = Column(Boolean, default=False)  # True if sum of categories >= 13
    total_category_points = Column(Integer, default=0)  # Sum of player categories
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    entry = relationship("Entry", back_populates="team")
    picks = relationship("TeamPick", back_populates="team", cascade="all, delete-orphan")

    def calculate_validity(self):
        """Calculate if team is valid (sum of categories >= 13 and exactly 5 players)"""
        if len(self.picks) != 5:
            return False
        total = sum([pick.player_category for pick in self.picks])
        self.total_category_points = total
        self.is_valid = total >= 13
        return self.is_valid
