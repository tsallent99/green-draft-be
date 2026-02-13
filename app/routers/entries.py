from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Entry, User
from app.models.entry import PaymentStatus
from app.schemas import EntryResponse, EntryUpdate
from app.auth import get_current_user

router = APIRouter(prefix="/entries", tags=["entries"])


@router.get("/my-entries", response_model=List[EntryResponse])
def get_my_entries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all entries for the current user"""
    entries = db.query(Entry).filter(Entry.user_id == current_user.id).all()
    return entries


@router.get("/{entry_id}", response_model=EntryResponse)
def get_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific entry by ID"""
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )

    # Check if user has access to this entry
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this entry"
        )

    return entry


@router.patch("/{entry_id}", response_model=EntryResponse)
def update_entry(
    entry_id: int,
    entry_update: EntryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an entry (mainly for payment status)"""
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )

    # Check if user has access to this entry
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this entry"
        )

    # Update fields
    if entry_update.payment_status is not None:
        entry.payment_status = entry_update.payment_status
    if entry_update.total_score is not None:
        entry.total_score = entry_update.total_score

    db.commit()
    db.refresh(entry)

    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an entry (leave league)"""
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entry not found"
        )

    # Check if user has access to this entry
    if entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this entry"
        )

    # Check if payment was already made
    if entry.payment_status == PaymentStatus.PAID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot leave league after payment has been made"
        )

    db.delete(entry)
    db.commit()
    return None
