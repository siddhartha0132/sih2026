import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user_optional
from app.db import get_db
from app.models_db import HistoryEntry, User
from app.schemas import (
    AdvisoryRequest,
    AdvisoryResponse,
    FinancialPlan,
    IdeaSuggestionRequest,
    IdeaSuggestionResponse,
)
from app.services import financial_calculator, i18n, idea_suggester
from app.services.feasibility_engine import build_feasibility_report

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "GramVyapaar AI backend"}


@router.post("/advisory", response_model=AdvisoryResponse)
def get_advisory(
    request: AdvisoryRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    """
    Single endpoint that returns BOTH:
      - Module 1: Hyper-Local Business Feasibility Report
      - Module 2: Smart Financial Calculator & Scheme Router output

    Open-use: no Authorization header is sent by the frontend, so
    `current_user` is None and this behaves exactly as before — stateless,
    nothing written anywhere.

    Personal-use: the frontend attaches the logged-in user's token, so this
    run is auto-saved as a history row after computing it. The engine itself
    doesn't know or care whether it's being called from personal or open mode
    — it always runs the same real calculations either way.
    """
    financial_plan: FinancialPlan = financial_calculator.build_financial_plan(
        request.available_margin_capital,
        business_category=request.business_category.value,
        applicant_gender=request.applicant_gender,
        is_first_time_entrepreneur=request.is_first_time_entrepreneur,
        language=request.language,
    )
    feasibility_report = build_feasibility_report(request, financial_plan.project_cost)

    response = AdvisoryResponse(
        request_echo=request,
        feasibility_report=feasibility_report,
        financial_plan=financial_plan,
        disclaimer=i18n.DISCLAIMER[i18n.normalize_language(request.language)],
    )

    if current_user is not None:
        entry = HistoryEntry(
            user_id=current_user.id,
            business_name=request.business_name,
            request_json=request.model_dump_json(),
            response_json=response.model_dump_json(),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        response.history_id = entry.id

    return response


@router.post("/financial-plan", response_model=FinancialPlan)
def get_financial_plan_only(available_margin_capital: float):
    """Standalone endpoint for just the Smart Scheme Calculator (no feasibility report)."""
    return financial_calculator.build_financial_plan(available_margin_capital)


@router.post("/idea-suggestion", response_model=IdeaSuggestionResponse)
def get_idea_suggestion(request: IdeaSuggestionRequest):
    """
    Reverse-flow: applicant describes their idea in free text (in their own
    words, no formal category names needed) and gets back a suggested
    business category, a plausible starting margin-capital figure, and a
    scheme hint — to pre-fill the main form rather than replace it.
    """
    return idea_suggester.suggest_from_idea(
        request.business_idea_description, request.available_margin_capital, request.language
    )
