from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, Enum, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    total_score = Column(Float, default=0.0)  # Accumulated points
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # A user can only have one entry per league
    __table_args__ = (
        UniqueConstraint('user_id', 'league_id', name='_user_league_uc'),
    )

    # Relationships
    user = relationship("User", back_populates="entries")
    league = relationship("League", back_populates="entries")
    team = relationship("Team", back_populates="entry", uselist=False)
