"""
Pydantic schemas — the contract between frontend and backend.
These map 1:1 onto the inputs/outputs named in the SIH26091 problem statement.
"""
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BusinessCategory(str, Enum):
    dairy = "Dairy"
    retail = "Retail"
    textiles = "Textiles"
    food_processing = "Food Processing"
    poultry = "Poultry"
    handicrafts = "Handicrafts"
    agri_input_store = "Agri Input Store"
    tailoring = "Tailoring"
    other = "Other"


class SchemeName(str, Enum):
    micro_finance = "Micro Finance Scheme"
    suvidha = "SUVIDHA Loan Scheme"
    utkarsh = "UTKARSH Loan Scheme"
    not_eligible = "Not Eligible (Project cost exceeds Rs. 50 Lakh)"


class ConfidenceLevel(str, Enum):
    high = "High"
    medium = "Medium"
    low = "Low"


class BusinessStage(str, Enum):
    idea = "idea"                # "I just have an idea"
    researching = "researching"  # "I'm researching, nothing started"
    ongoing = "ongoing"          # "I already run this business"


class LegalStructure(str, Enum):
    none_informal = "none_informal"        # No formal registration, runs informally / on trust
    proprietorship = "proprietorship"      # Sole proprietorship (most common for micro-enterprise)
    partnership = "partnership"            # Partnership firm
    shg_or_cooperative = "shg_or_cooperative"  # Self-Help Group / cooperative society
    private_limited = "private_limited"    # Private Limited Company
    llp = "llp"                            # Limited Liability Partnership
    opc = "opc"                            # One Person Company
    not_sure = "not_sure"                  # Applicant doesn't know / hasn't decided yet


# ---------------------------------------------------------------------------
# Request: the three inputs named explicitly in the PS
# ---------------------------------------------------------------------------

class AdvisoryRequest(BaseModel):
    village: str = Field(..., description="Village / Town name")
    block: Optional[str] = Field(None, description="Block / Tehsil name")
    district: str = Field(..., description="District name")
    state: str = Field(..., description="State name")
    pincode: Optional[str] = Field(None, description="6-digit PIN code, improves geo lookups")

    available_margin_capital: float = Field(
        ..., gt=0, description="Beneficiary's own contribution, e.g. 100000 (Rs. 1,00,000)"
    )
    business_category: BusinessCategory
    business_category_other: Optional[str] = Field(
        None, description="Free text if business_category == 'Other'"
    )

    applicant_gender: Optional[str] = None
    applicant_age: Optional[int] = None
    is_first_time_entrepreneur: Optional[bool] = True
    language: str = Field("en", description="ISO code for report language: en, hi (more can be added).")

    business_name: Optional[str] = Field(
        None,
        description="Free-text label for this venture, e.g. 'Meena's Dairy'. "
        "Optional for a one-off (open-use) run. For personal-use, reusing the "
        "same business_name across multiple runs groups them as one ongoing "
        "business's timeline in the saved history.",
    )

    # ── Business context — asked before generating the plan ──────────────────
    # These directly change both the tone of the report (an ongoing business
    # gets a "grow" narrative, a fresh idea gets a "validate before you spend"
    # narrative) and the numbers themselves (an ongoing business's own current
    # revenue is a far better anchor than a generic district-level estimate).
    business_stage: Optional[BusinessStage] = Field(
        BusinessStage.idea,
        description="Is this just an idea, something being researched, or an "
        "already-running business? Changes both tone and the revenue math.",
    )
    legal_structure: Optional[LegalStructure] = Field(
        LegalStructure.none_informal,
        description="How the business is (or will be) legally run. Most rural "
        "micro-enterprises are informal/proprietorship — that is completely "
        "normal and does not block scheme eligibility.",
    )
    current_monthly_revenue: Optional[float] = Field(
        None, ge=0,
        description="Only relevant when business_stage='ongoing'. The business's "
        "actual current monthly revenue (Rs.), used to ground the revenue "
        "projection in the applicant's real numbers instead of a district average.",
    )
    business_idea_description: Optional[str] = Field(
        None, max_length=1000,
        description="Free-text description of the business idea in the "
        "applicant's own words, e.g. 'I want to sell milk from my 2 buffaloes "
        "to my village'. Used by the /api/idea-suggestion reverse-flow endpoint "
        "to suggest a business_category, a starting margin-capital figure, and "
        "a likely scheme before the applicant fills in the rest of the form.",
    )


# ---------------------------------------------------------------------------
# Module 2 — Financial Structuring & Scheme Router (fully deterministic)
# ---------------------------------------------------------------------------

class SchemeOption(BaseModel):
    """
    One row in the "all schemes you might qualify for" list. Unlike
    `selected_scheme` (the single NSFDC tier the Module-2 calculator routes
    to, with a full EMI schedule), this is a broader eligibility scan across
    every major central-government credit scheme relevant to a rural
    micro-entrepreneur, so the applicant sees every real door open to them —
    not just one.
    """
    scheme_name: str
    operating_agency: str            # e.g. "NSFDC", "KVIC (PMEGP)", "Banks/NBFCs (MUDRA)", "SIDBI (Stand-Up India)"
    is_eligible: bool
    is_recommended: bool = False     # true for the one auto-selected as the primary plan
    eligibility_note: str            # plain-language why eligible / why not
    max_project_cost: float
    max_loan_amount: float
    subsidy_or_margin_money_note: str  # e.g. "15-25% capital subsidy for PMEGP" vs "None (loan only)"
    interest_rate_percent_range: str   # a range string since MUDRA/PMEGP vary by bank
    tenure_years: str                  # string because some are "up to 7", not fixed
    description: str                   # 1-2 sentence plain-language description
    official_source_url: str
    terms_verified_on: str


class RevenueProjection(BaseModel):
    """
    The "full truth" revenue picture — not just the upside. Grounded in real,
    cited methodology per category (see revenue_estimator.py), with an
    explicit low/mid/high range rather than one optimistic number, plus the
    realistic count of customers, distributors and raw-material sources the
    entrepreneur will actually have to line up.
    """
    monthly_revenue_low: float
    monthly_revenue_mid: float
    monthly_revenue_high: float
    monthly_operating_cost_estimate: float
    monthly_net_income_estimate: float
    estimated_active_customers: int
    estimated_distributors_or_buyers: int
    estimated_raw_material_sources: int
    raw_material_source_examples: List[str]
    distributor_examples: List[str]
    downside_risk_note: str          # explicit "this can go wrong" statement — the demanded "full truth"
    methodology: str
    data_source: str
    source_url: str = ""
    used_applicant_reported_revenue: bool = False


class FlowchartStep(BaseModel):
    step_number: int
    title: str
    description: str


class RepaymentInstallment(BaseModel):
    period_label: str          # e.g. "Quarter 5"
    opening_balance: float
    principal_component: float
    interest_component: float
    installment_amount: float
    closing_balance: float


class FinancialPlan(BaseModel):
    available_margin_capital: float
    margin_percentage: float = 10.0
    project_cost: float
    max_loan_amount: float
    loan_percentage: float = 90.0

    selected_scheme: SchemeName
    interest_rate_percent: float
    tenure_years: int
    moratorium_months: int

    quarterly_installment_amount: float
    total_interest_payable: float
    total_repayable: float

    repayment_schedule: List[RepaymentInstallment]

    scheme_explanation: str  # "Why this scheme?" — plain-language justification
    warnings: List[str] = []  # e.g. project cost exceeds Rs 50L ceiling

    official_source_url: str = Field(
        "", description="Direct link to the official NSFDC page these terms were "
        "verified against — render this as a clickable citation in the UI."
    )
    terms_verified_on: str = Field(
        "", description="Date (YYYY-MM-DD) these scheme terms were last checked "
        "live against the official source."
    )

    all_schemes: List[SchemeOption] = Field(
        default_factory=list,
        description="Every major scheme (NSFDC tiers, PMEGP, MUDRA, Stand-Up "
        "India) evaluated for this project cost and applicant profile — not "
        "just the one selected_scheme. Shown to the user so they see every "
        "real avenue, each with its own link and description.",
    )


# ---------------------------------------------------------------------------
# Module 1 — Hyper-Local Business Feasibility Report
# ---------------------------------------------------------------------------

class SWOTAnalysis(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]


class CompetitorMapping(BaseModel):
    estimated_similar_businesses_nearby: int
    density_rating: str          # "Low" / "Moderate" / "High"
    nearest_competitor_distance_km: Optional[float] = None
    data_source: str
    source_url: str = ""
    confidence: ConfidenceLevel


class PricingRecommendation(BaseModel):
    suggested_price_range_min: float
    suggested_price_range_max: float
    unit: str                     # e.g. "per litre", "per piece"
    predicted_local_market_value: float
    pricing_rationale: str
    data_source: str
    source_url: str = ""
    confidence: ConfidenceLevel


class OpportunityAnalysis(BaseModel):
    underserved_niches: List[str]
    rationale: str


class ThreatFlag(BaseModel):
    threat: str
    severity: str  # Low / Medium / High
    mitigation: str


class MarketReach(BaseModel):
    radius_km: float
    estimated_consumer_base: int
    primary_distribution_channels: List[str]
    data_source: str
    source_url: str = ""
    confidence: ConfidenceLevel


class FeasibilityReport(BaseModel):
    business_opportunity_score: int = Field(..., ge=0, le=100)
    overall_confidence: ConfidenceLevel

    market_reach: MarketReach
    opportunity_analysis: OpportunityAnalysis
    swot: SWOTAnalysis
    threats: List[ThreatFlag]
    competitor_mapping: CompetitorMapping
    pricing: PricingRecommendation

    narrative_summary: str  # short AI-generated plain-language summary
    actionable_next_steps: List[str]

    revenue_projection: Optional[RevenueProjection] = None
    journey_flowchart: List[FlowchartStep] = Field(
        default_factory=list,
        description="Simple step-by-step flowchart of the journey from idea to "
        "a growing business — shown as a visual flowchart in the UI instead of "
        "a data graph, since it is easier for a first-time, low-financial-"
        "literacy audience to follow than a chart with axes.",
    )


# ---------------------------------------------------------------------------
# Combined response
# ---------------------------------------------------------------------------

class AdvisoryResponse(BaseModel):
    request_echo: AdvisoryRequest
    feasibility_report: FeasibilityReport
    financial_plan: FinancialPlan
    disclaimer: str = (
        "This report is an AI-generated advisory tool to aid decision-making. "
        "It does not constitute an official loan sanction or government approval. "
        "Final eligibility is determined by the concerned Channelizing Agency (CA/SCA)."
    )
    history_id: Optional[int] = Field(
        None, description="Set only when this run was auto-saved to a logged-in "
        "user's personal-use history."
    )


# ---------------------------------------------------------------------------
# Reverse-flow: "describe your business idea" free-text suggestion
# ---------------------------------------------------------------------------

class IdeaSuggestionRequest(BaseModel):
    business_idea_description: str = Field(..., min_length=5, max_length=1000)
    available_margin_capital: Optional[float] = Field(
        None, gt=0, description="If already known, refines the scheme suggestion."
    )
    language: Optional[str] = Field("en", description="Language for the explanation text (en/hi/kn/te).")


class IdeaSuggestionResponse(BaseModel):
    detected_business_category: BusinessCategory
    detected_business_category_other: Optional[str] = None
    matched_keywords: List[str]
    suggested_starting_margin_capital: float
    confidence: ConfidenceLevel
    explanation: str
    likely_scheme_hint: str


# ---------------------------------------------------------------------------
# Auth — personal-use login only. Open-use never touches these endpoints.
# ---------------------------------------------------------------------------

class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1)
    phone_or_email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)


class LoginRequest(BaseModel):
    phone_or_email: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    phone_or_email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------------------------------------------------------------------------
# Saved history — personal-use only
# ---------------------------------------------------------------------------

class HistoryEntrySummary(BaseModel):
    id: int
    business_name: Optional[str] = None
    created_at: str
    village: str
    district: str
    business_category: str
    business_opportunity_score: int
    selected_scheme: SchemeName


class HistoryEntryDetail(BaseModel):
    id: int
    business_name: Optional[str] = None
    created_at: str
    request: AdvisoryRequest
    response: AdvisoryResponse
