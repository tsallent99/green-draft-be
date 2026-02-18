from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Leaderboard(Base):
    __tablename__ = "leaderboards"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False, unique=True)
    rankings = Column(JSON)  # Store rankings as JSON: [{"entry_id": 1, "position": 1, "score": 150.5, "prize": 600}, ...]
    prize_pool = Column(Float, default=0.0)  # Total prize pool (entry_fee * num_entries)
    first_place_prize = Column(Float, default=0.0)  # 60% of pool
    second_place_prize = Column(Float, default=0.0)  # 30% of pool
    third_place_prize = Column(Float, default=0.0)  # 10% of pool
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    league = relationship("League", back_populates="leaderboard")

    def calculate_prizes(self, entries):
        """Calculate prize distribution based on actual amounts received after Stripe fees"""
        self.prize_pool = round(sum(e.amount_paid for e in entries), 2)
        self.first_place_prize = round(self.prize_pool * 0.60, 2)
        self.second_place_prize = round(self.prize_pool * 0.30, 2)
        self.third_place_prize = round(self.prize_pool * 0.10, 2)
