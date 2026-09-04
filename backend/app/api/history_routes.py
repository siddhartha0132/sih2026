"""
Saved history — personal-use only. Every route here requires a valid login
token (get_current_user, the strict dependency). Open-use never has a token
and therefore never lands in these tables at all.
"""
import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.db import get_db
from app.models_db import HistoryEntry, User
from app.schemas import AdvisoryRequest, AdvisoryResponse, HistoryEntryDetail, HistoryEntrySummary

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[HistoryEntrySummary])
def list_history(
    business_name: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    All saved runs for the logged-in user, newest first. Pass ?business_name=
    to filter to one ongoing venture (used by the growth-over-time timeline).
    """
    query = db.query(HistoryEntry).filter(HistoryEntry.user_id == current_user.id)
    if business_name:
        query = query.filter(HistoryEntry.business_name == business_name)
    entries = query.order_by(HistoryEntry.created_at.asc()).all()

    summaries = []
    for e in entries:
        req = json.loads(e.request_json)
        resp = json.loads(e.response_json)
        summaries.append(
            HistoryEntrySummary(
                id=e.id,
                business_name=e.business_name,
                created_at=e.created_at.isoformat(),
                village=req.get("village", ""),
                district=req.get("district", ""),
                business_category=req.get("business_category", ""),
                business_opportunity_score=resp["feasibility_report"]["business_opportunity_score"],
                selected_scheme=resp["financial_plan"]["selected_scheme"],
            )
        )
    return summaries


@router.get("/{entry_id}", response_model=HistoryEntryDetail)
def get_history_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = (
        db.query(HistoryEntry)
        .filter(HistoryEntry.id == entry_id, HistoryEntry.user_id == current_user.id)
        .first()
    )
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="History entry not found.")
    return HistoryEntryDetail(
        id=entry.id,
        business_name=entry.business_name,
        created_at=entry.created_at.isoformat(),
        request=AdvisoryRequest(**json.loads(entry.request_json)),
        response=AdvisoryResponse(**json.loads(entry.response_json)),
    )
