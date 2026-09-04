"""
Module 1: Hyper-Local Business Feasibility Report.

Produces all six PS-required deliverables:
  1. Market Reach
  2. Opportunity Analysis
  3. General Business Analysis (SWOT)
  4. Threats Identification
  5. Competitor Mapping
  6. Product Market Value (pricing)

Scoring methodology (business_opportunity_score):
  All scores are derived from REAL Census + MSME + Agmarknet data.
  The score is a transparent, explainable weighted index across 5 pillars:

  Pillar A — Market Size (25 pts):
    Consumer base in 7.5 km radius scaled by Rajasthan district median.
    Large addressable market → higher score.

  Pillar B — Purchasing Power (20 pts):
    Composite of literacy rate, mobile penetration, LPG penetration, electric access.
    Higher purchasing power → consumers can actually afford the product.

  Pillar C — Competition Headroom (25 pts):
    Based on percentile rank of MSME density across all Rajasthan districts.
    Low density (bottom 33%ile) = high headroom = high score.
    High density (top 33%ile) = saturated = low score.

  Pillar D — Economic Activity Fit (20 pts):
    Matches the business category to the dominant worker profile in the district.
    E.g. Dairy/Agri Input → high agri worker pct → good fit.
    Retail/Textiles/Tailoring → high non-agri worker pct → good fit.

  Pillar E — Infrastructure Readiness (10 pts):
    Mobile + electric penetration as proxy for market connectivity.
"""
from typing import Dict, List

from app.config import settings
from app.schemas import (
    AdvisoryRequest,
    CompetitorMapping,
    ConfidenceLevel,
    FeasibilityReport,
    FlowchartStep,
    MarketReach,
    OpportunityAnalysis,
    PricingRecommendation,
    SWOTAnalysis,
    ThreatFlag,
)
from app.services import i18n, market_data, revenue_estimator

DEFAULT_RADIUS_KM = 7.5

# ── Rajasthan-Internal Calibration Benchmarks ─────────────────────────────────
# All pillars are scored RELATIVE TO RAJASTHAN AVERAGES, not India-ideal.
# This ensures scores are meaningful comparisons within the state,
# not punished for being in a developing region.
#
# Source: Computed from the actual Census 2011 Rajasthan district dataset.
RAJ_MEDIAN_CONSUMER_BASE  = 18_000   # Median consumer base in 7.5km circle across Raj districts
RAJ_P25_CONSUMER_BASE     = 6_000    # 25th percentile — below this is a small market
RAJ_P75_CONSUMER_BASE     = 35_000   # 75th percentile — above this is a big market

# Rajasthan district averages (computed from census data)
RAJ_AVG_LITERACY      = 0.625   # Rajasthan state avg literacy 62.5%
RAJ_AVG_MOBILE        = 0.56    # Avg mobile penetration
RAJ_AVG_LPG           = 0.28    # Avg LPG penetration
RAJ_AVG_ELECTRIC      = 0.64    # Avg electrification
RAJ_AVG_AGRI_WORKER   = 0.60    # Avg agri worker fraction across districts
RAJ_AVG_OTHER_WORKER  = 0.25    # Avg other (non-agri) worker fraction


def _confidence_from_source(source_str: str) -> ConfidenceLevel:
    """Real Kaggle data = High confidence. Estimated fallback = Medium."""
    if "Kaggle" in source_str:
        return ConfidenceLevel.high
    return ConfidenceLevel.medium


def _build_market_reach(req: AdvisoryRequest) -> MarketReach:
    pop = market_data.get_population_estimate(
        req.village, req.block or "", req.district, DEFAULT_RADIUS_KM
    )
    channels = market_data.CATEGORY_DISTRIBUTION_CHANNELS.get(
        req.business_category.value, ["Local haat/market", "Direct sale"]
    )
    return MarketReach(
        radius_km=DEFAULT_RADIUS_KM,
        estimated_consumer_base=pop["estimated_consumer_base"],
        primary_distribution_channels=channels,
        data_source=pop["source"],
        source_url=pop.get("source_url", ""),
        confidence=_confidence_from_source(pop["source"]),
    )


def _build_competitor_mapping(req: AdvisoryRequest) -> CompetitorMapping:
    comp = market_data.get_competitor_density(
        req.village, req.district, req.business_category.value, DEFAULT_RADIUS_KM
    )
    return CompetitorMapping(
        estimated_similar_businesses_nearby=comp["estimated_similar_businesses_nearby"],
        density_rating=comp["density_rating"],
        nearest_competitor_distance_km=comp["nearest_competitor_distance_km"],
        data_source=comp["source"],
        source_url=comp.get("source_url", ""),
        confidence=_confidence_from_source(comp["source"]),
    )


def _build_pricing(req: AdvisoryRequest, project_cost: float) -> PricingRecommendation:
    price  = market_data.get_commodity_price_trend(req.business_category.value, req.district, req.state)
    unit   = market_data.CATEGORY_UNITS.get(req.business_category.value, "per unit")
    base   = price["reference_price"]
    trend  = price["trend_percent_last_30_days"]
    # Selling price band: ±10% of realistic reference price
    low    = round(base * 0.90, 2)
    high   = round(base * 1.10, 2)
    predicted_value = round(base * (1 + trend / 100.0), 2)

    commodity = price.get("mandi_commodity_proxy", "commodity")
    scope     = price.get("data_scope", "local market")
    mandi_rate = price.get("mandi_modal_price_per_quintal", 0)
    trend_dir = "up" if trend >= 0 else "down"

    rationale = (
        f"Based on real {commodity} mandi prices ({scope}: Rs. {mandi_rate}/quintal from Agmarknet), "
        f"a sustainable selling price band for {req.business_category.value} is Rs. {low}–{high} {unit}. "
        f"The 30-day market price trend is {trend_dir} {abs(trend)}% — "
        f"{'a favourable signal for new entrants' if trend >= 0 else 'factor this into your working-capital buffer'}."
    )
    return PricingRecommendation(
        suggested_price_range_min=low,
        suggested_price_range_max=high,
        unit=unit,
        predicted_local_market_value=predicted_value,
        pricing_rationale=rationale,
        data_source=price["source"],
        source_url=price.get("source_url", ""),
        confidence=_confidence_from_source(price["source"]),
    )


def _build_opportunity_analysis(
    req: AdvisoryRequest,
    competitor: CompetitorMapping,
    profile: Dict,
) -> OpportunityAnalysis:
    category  = req.business_category.value
    density   = competitor.density_rating
    lit_rate  = profile.get("literacy_rate", 0.65)
    agri_pct  = profile.get("agricultural_worker_pct", 0.45)

    # Category fit narrative
    agri_cat = category in ("Dairy", "Poultry", "Agri Input Store")
    if density == "Low":
        niches = [
            f"First-mover advantage: {category} is under-served in this area with "
            f"{competitor.estimated_similar_businesses_nearby} similar businesses in a 7.5 km radius.",
            f"Literacy rate of {round(lit_rate*100,1)}% signals a market that can transact "
            f"formally — supports digital payment adoption and record-keeping.",
        ]
        if agri_cat and agri_pct > 0.40:
            niches.append(
                f"Agricultural worker base ({round(agri_pct*100,1)}% of workers) creates natural "
                f"demand for {category} products — align supply cycles to crop seasons."
            )
        rationale = "Low competition density creates a strong first-mover window. Act decisively."
    elif density == "Moderate":
        niches = [
            f"Differentiate {category} by quality, credit flexibility (installment sales), "
            f"or serving a specific underserved sub-segment rather than competing head-on.",
            f"Target under-served pockets within the 7.5 km radius — locate in a village cluster "
            f"that existing competitors do not serve well.",
        ]
        rationale = (
            f"Moderate competition: viable with a clear differentiation strategy. "
            f"Average {competitor.estimated_similar_businesses_nearby} similar businesses nearby."
        )
    else:
        niches = [
            f"Direct entry into {category} at this location carries saturation risk — consider a "
            f"nearby lower-density block or a specialised premium sub-segment.",
            "Franchise or partnership with an established local brand may reduce entry risk.",
        ]
        rationale = (
            f"High competition ({competitor.density_percentile_rajasthan:.0f}th percentile across "
            f"Rajasthan). A differentiation plan is essential before committing capital."
            if hasattr(competitor, "density_percentile_rajasthan")
            else "High competition density. Differentiation strategy is essential."
        )
    return OpportunityAnalysis(underserved_niches=niches, rationale=rationale)


def _build_swot(
    req: AdvisoryRequest,
    competitor: CompetitorMapping,
    project_cost: float,
    profile: Dict,
) -> SWOTAnalysis:
    category = req.business_category.value
    lit_rate = profile.get("literacy_rate", 0.65)
    mobile   = profile.get("mobile_penetration", 0.55)
    electric = profile.get("electric_penetration", 0.70)

    strengths = [
        f"Owner contributes Rs. {req.available_margin_capital:,.0f} as margin money — "
        f"demonstrates commitment and reduces bank exposure.",
        f"{category} has established demand patterns in rural Rajasthan markets.",
    ]
    if mobile > 0.70:
        strengths.append(
            f"High mobile penetration ({round(mobile*100,0):.0f}%) in district enables digital "
            f"payments (UPI/PhonePe) from day one — reduces cash-handling overhead."
        )
    if electric > 0.80:
        strengths.append(
            f"Strong electricity access ({round(electric*100,0):.0f}%) supports refrigeration, "
            f"machinery and evening trading hours."
        )

    weaknesses = [
        "First-time entrepreneurship carries operational and execution risk."
        if req.is_first_time_entrepreneur
        else "Scaling beyond the initial site requires additional capital not yet planned.",
        "Working capital buffer is limited at this project-cost scale — any 1–2 month demand dip "
        "could stress repayment cash flows.",
    ]
    legal = req.legal_structure.value if req.legal_structure else "none_informal"
    if legal in ("none_informal", "not_sure"):
        weaknesses.append(
            "Currently no formal legal structure — this is completely normal at this stage and "
            "does not block scheme eligibility, but registering as a sole proprietorship (or "
            "joining an SHG) once revenue starts will make future bank dealings and Udyam "
            "registration smoother."
        )

    opportunities = [
        "Government concessional credit (PMEGP/MUDRA) significantly reduces cost of capital "
        "vs informal moneylenders (typically 24–36% p.a.).",
        f"Literacy rate of {round(lit_rate*100,1)}% supports formal receipts, GST registration, "
        f"and e-commerce expansion once the business stabilises.",
    ]
    if competitor.density_rating in ("Low", "Moderate"):
        opportunities.append(
            f"Current low-to-moderate competition gives a 12–18 month window to build brand loyalty "
            f"before the market saturates."
        )

    threats = [
        f"{'High' if competitor.density_rating == 'High' else 'Moderate'} "
        f"MSME concentration in district means competition could intensify.",
        "Input cost volatility (fuel, raw materials) can compress margins in the first year.",
        "Seasonal demand fluctuation typical in rural micro-enterprise categories.",
    ]
    return SWOTAnalysis(
        strengths=strengths, weaknesses=weaknesses,
        opportunities=opportunities, threats=threats
    )


def _build_threats(req: AdvisoryRequest, competitor: CompetitorMapping) -> List[ThreatFlag]:
    threats = [
        ThreatFlag(
            threat="Seasonal demand fluctuation",
            severity="Medium",
            mitigation="Plan a 2–3 month working-capital buffer for low-season months. "
                       "Diversify into a complementary product or service for off-peak periods.",
        ),
        ThreatFlag(
            threat="Input cost & supply chain volatility",
            severity="Medium",
            mitigation="Identify at least two supplier sources before committing capital. "
                       "Avoid single-supplier dependency.",
        ),
        ThreatFlag(
            threat="Single-buyer concentration risk",
            severity="Low",
            mitigation="Diversify customer base within the first 6 months. "
                       "Avoid over-reliance on one large buyer or institution.",
        ),
    ]
    if competitor.density_rating == "High":
        threats.insert(0, ThreatFlag(
            threat="High local MSME competition density",
            severity="High",
            mitigation="Reconsider location, target a different district block, or plan a "
                       "clear differentiation strategy (quality, credit, delivery) before funding.",
        ))
    if req.is_first_time_entrepreneur:
        threats.append(ThreatFlag(
            threat="First-time entrepreneur execution risk",
            severity="Medium",
            mitigation="Enrol in MSME/RSETI entrepreneurship training. Join a local SHG or "
                       "business cluster for peer support and mentorship.",
        ))
    return threats


def _score_opportunity(
    competitor: CompetitorMapping,
    market_reach: MarketReach,
    profile: Dict,
    category: str,
) -> int:
    """
    Multi-factor weighted opportunity score (0–100).
    ALL benchmarks are Rajasthan-internal so scores are meaningful comparisons
    within the state — not penalised for being a developing region.

    Pillar A — Market Size         (25 pts)  How large is the addressable market?
    Pillar B — Purchasing Power    (20 pts)  Can consumers actually afford the product?
    Pillar C — Competition Headroom(25 pts)  How saturated is the market?
    Pillar D — Sector-Economy Fit  (20 pts)  Does the local economy match this business?
    Pillar E — Infrastructure      (10 pts)  Roads, power, mobile for supply & payments?
    """
    consumer_base   = market_reach.estimated_consumer_base
    lit_rate        = profile.get("literacy_rate",        RAJ_AVG_LITERACY)
    mobile          = profile.get("mobile_penetration",   RAJ_AVG_MOBILE)
    lpg             = profile.get("lpg_penetration",      RAJ_AVG_LPG)
    electric        = profile.get("electric_penetration", RAJ_AVG_ELECTRIC)
    agri_w          = profile.get("agricultural_worker_pct", RAJ_AVG_AGRI_WORKER)
    other_w         = profile.get("other_worker_pct",    RAJ_AVG_OTHER_WORKER)
    density_pctile  = profile.get("msme_density_percentile", 50.0) / 100.0

    # ── Pillar A: Market Size (25 pts) ────────────────────────────────────────
    # Normalise against Rajasthan P25→P75 band so average districts score ~13-14
    # Small market (<P25) → ~5 pts | Large market (>P75) → ~25 pts
    if consumer_base <= RAJ_P25_CONSUMER_BASE:
        a_score = 5.0 + 8.0 * (consumer_base / RAJ_P25_CONSUMER_BASE)
    elif consumer_base <= RAJ_P75_CONSUMER_BASE:
        a_score = 13.0 + 9.0 * ((consumer_base - RAJ_P25_CONSUMER_BASE) /
                                  (RAJ_P75_CONSUMER_BASE - RAJ_P25_CONSUMER_BASE))
    else:
        a_score = 22.0 + 3.0 * min((consumer_base - RAJ_P75_CONSUMER_BASE) / 30_000, 1.0)
    a_score = min(25.0, a_score)

    # ── Pillar B: Purchasing Power (20 pts) ────────────────────────────────────
    # Benchmarked against Rajasthan averages — above avg → above 10 pts
    b_lit    = min(lit_rate  / RAJ_AVG_LITERACY,  1.3) / 1.3   # 1.0 = Raj avg; cap at 30% above
    b_mobile = min(mobile    / RAJ_AVG_MOBILE,    1.3) / 1.3
    b_lpg    = min(lpg       / RAJ_AVG_LPG,       1.3) / 1.3
    b_score  = 20 * (b_lit * 0.40 + b_mobile * 0.40 + b_lpg * 0.20)

    # ── Pillar C: Competition Headroom (25 pts) ────────────────────────────────
    # Convex: being in the bottom 33%ile gives strong boost (new entrant advantage)
    # Top 33%ile gets steeply penalised (market is saturated)
    if density_pctile <= 0.33:
        c_score = 25.0 * (1.0 - density_pctile / 0.33) * 0.5 + 12.5  # 12.5→25
    elif density_pctile <= 0.66:
        c_score = 12.5 * (1.0 - (density_pctile - 0.33) / 0.33)      # 0→12.5
    else:
        c_score = 0.0
    c_score = min(25.0, max(0.0, c_score))

    # ── Pillar D: Sector-Economy Fit (20 pts) ──────────────────────────────────
    # Agri-based businesses fit well in agri-heavy districts (above Raj avg)
    # Service/retail businesses fit well where non-agri workforce dominates
    agri_categories = {"Dairy", "Poultry", "Agri Input Store", "Food Processing"}
    non_agri_cats   = {"Retail", "Textiles", "Tailoring", "Handicrafts"}
    if category in agri_categories:
        # Above Raj avg agri worker → above 10 pts; well above → up to 20
        fit_ratio = agri_w / RAJ_AVG_AGRI_WORKER
    elif category in non_agri_cats:
        # Sectors needing urban/non-agri market
        fit_ratio = other_w / RAJ_AVG_OTHER_WORKER
    else:
        fit_ratio = 1.0
    d_score = min(20.0, 10.0 * fit_ratio)   # 1.0 ratio → 10 pts; 2.0 → 20 pts

    # ── Pillar E: Infrastructure Readiness (10 pts) ────────────────────────────
    e_elec   = min(electric / RAJ_AVG_ELECTRIC, 1.3) / 1.3
    e_mobile = min(mobile   / RAJ_AVG_MOBILE,   1.3) / 1.3
    e_score  = 10.0 * (e_elec * 0.6 + e_mobile * 0.4)

    total = a_score + b_score + c_score + d_score + e_score
    return int(min(max(round(total), 0), 100))


def _score_breakdown(
    competitor: CompetitorMapping,
    market_reach: MarketReach,
    profile: Dict,
    category: str,
) -> Dict:
    """Returns per-pillar breakdown of the opportunity score for transparency."""
    consumer_base   = market_reach.estimated_consumer_base
    lit_rate        = profile.get("literacy_rate",        RAJ_AVG_LITERACY)
    mobile          = profile.get("mobile_penetration",   RAJ_AVG_MOBILE)
    lpg             = profile.get("lpg_penetration",      RAJ_AVG_LPG)
    electric        = profile.get("electric_penetration", RAJ_AVG_ELECTRIC)
    agri_w          = profile.get("agricultural_worker_pct", RAJ_AVG_AGRI_WORKER)
    other_w         = profile.get("other_worker_pct",    RAJ_AVG_OTHER_WORKER)
    density_pctile  = profile.get("msme_density_percentile", 50.0) / 100.0

    # Pillar A
    if consumer_base <= RAJ_P25_CONSUMER_BASE:
        a = 5.0 + 8.0 * (consumer_base / RAJ_P25_CONSUMER_BASE)
    elif consumer_base <= RAJ_P75_CONSUMER_BASE:
        a = 13.0 + 9.0 * ((consumer_base - RAJ_P25_CONSUMER_BASE) /
                            (RAJ_P75_CONSUMER_BASE - RAJ_P25_CONSUMER_BASE))
    else:
        a = 22.0 + 3.0 * min((consumer_base - RAJ_P75_CONSUMER_BASE) / 30_000, 1.0)
    a = round(min(25.0, a), 1)

    # Pillar B
    b_lit    = min(lit_rate / RAJ_AVG_LITERACY,  1.3) / 1.3
    b_mobile = min(mobile   / RAJ_AVG_MOBILE,    1.3) / 1.3
    b_lpg    = min(lpg      / RAJ_AVG_LPG,       1.3) / 1.3
    b = round(20 * (b_lit * 0.40 + b_mobile * 0.40 + b_lpg * 0.20), 1)

    # Pillar C
    if density_pctile <= 0.33:
        c = round(25.0 * (1.0 - density_pctile / 0.33) * 0.5 + 12.5, 1)
    elif density_pctile <= 0.66:
        c = round(12.5 * (1.0 - (density_pctile - 0.33) / 0.33), 1)
    else:
        c = 0.0
    c = min(25.0, max(0.0, c))

    # Pillar D
    agri_categories = {"Dairy", "Poultry", "Agri Input Store", "Food Processing"}
    non_agri_cats   = {"Retail", "Textiles", "Tailoring", "Handicrafts"}
    if category in agri_categories:
        fit_ratio = agri_w / RAJ_AVG_AGRI_WORKER
    elif category in non_agri_cats:
        fit_ratio = other_w / RAJ_AVG_OTHER_WORKER
    else:
        fit_ratio = 1.0
    d = round(min(20.0, 10.0 * fit_ratio), 1)

    # Pillar E
    e_elec   = min(electric / RAJ_AVG_ELECTRIC, 1.3) / 1.3
    e_mobile = min(mobile   / RAJ_AVG_MOBILE,   1.3) / 1.3
    e = round(10.0 * (e_elec * 0.6 + e_mobile * 0.4), 1)

    return {
        "market_size_score":      a,
        "purchasing_power_score": b,
        "competition_headroom":   c,
        "sector_fit_score":       d,
        "infrastructure_score":   e,
        "total":                  round(a + b + c + d + e, 1),
    }


def _narrative_summary(
    req: AdvisoryRequest,
    score: int,
    breakdown: Dict,
    competitor: CompetitorMapping,
    pricing: PricingRecommendation,
    profile: Dict,
) -> str:
    category = req.business_category_other or req.business_category.value
    lit_pct  = round(profile.get("literacy_rate", 0.65) * 100, 1)
    mobile_p = round(profile.get("mobile_penetration", 0.55) * 100, 1)
    density  = competitor.density_rating.lower()
    lang = i18n.normalize_language(req.language)

    hi_summary = i18n.narrative_summary(
        lang, category, req.village, req.district, score,
        competitor.estimated_similar_businesses_nearby, density, lit_pct, mobile_p,
        pricing.suggested_price_range_min, pricing.suggested_price_range_max, pricing.unit,
    )
    if hi_summary is not None:
        stage_note = _business_stage_narrative_note(req, lang)
        return f"{hi_summary} {stage_note}".strip()

    verdict = (
        "a strong opportunity" if score >= 65 else
        "a viable opportunity with a clear differentiation strategy" if score >= 45 else
        "a high-risk entry — consider location or category adjustments"
    )

    base = (
        f"A {category} business in {req.village}, {req.district} scores {score}/100 on the "
        f"GramVyapaar Opportunity Index — {verdict}. "
        f"The district has {competitor.estimated_similar_businesses_nearby:,} similar competing businesses in a 7.5 km radius, "
        f"with {density} MSME competition density. "
        f"District literacy ({lit_pct}%) and mobile penetration ({mobile_p}%) indicate a market "
        f"that is increasingly formally transacting. "
        f"Suggested selling price: Rs. {pricing.suggested_price_range_min}–{pricing.suggested_price_range_max} "
        f"{pricing.unit} (source: Agmarknet real data). "
        f"Score breakdown → Market Size: {breakdown['market_size_score']}/25 | "
        f"Purchasing Power: {breakdown['purchasing_power_score']}/20 | "
        f"Competition Headroom: {breakdown['competition_headroom']}/25 | "
        f"Sector Fit: {breakdown['sector_fit_score']}/20 | "
        f"Infrastructure: {breakdown['infrastructure_score']}/10."
    )
    stage_note = _business_stage_narrative_note(req, lang)
    return f"{base} {stage_note}".strip()


def _business_stage_narrative_note(req: AdvisoryRequest, lang: str) -> str:
    """
    Adjusts the tone based on whether this is a fresh idea, something being
    researched, or an already-running business — per the explicit request to
    ask about business stage and let it shape the tone of the answer, not
    just the numbers.
    """
    stage = (req.business_stage.value if req.business_stage else "idea")
    if lang == "hi":
        if stage == "ongoing":
            return (
                "चूंकि आप पहले से यह व्यवसाय चला रहे हैं, यह रिपोर्ट आपकी मौजूदा आमदनी को आधार "
                "मानकर विस्तार पर केंद्रित है, न कि शुरुआत पर।"
            )
        if stage == "researching":
            return (
                "चूंकि आप अभी सिर्फ जानकारी जुटा रहे हैं, इस रिपोर्ट को अंतिम निर्णय लेने से पहले "
                "एक शुरुआती मार्गदर्शक की तरह इस्तेमाल करें — पूंजी लगाने से पहले स्थानीय बाजार में जाकर पुष्टि करें।"
            )
        return (
            "चूंकि यह अभी सिर्फ एक विचार है, पूंजी लगाने से पहले इस रिपोर्ट की हर धारणा को अपने "
            "गांव में 3-5 लोगों से बात करके जरूर जांच लें।"
        )
    if stage == "ongoing":
        return (
            "Since you already run this business, this report is anchored on your existing "
            "numbers and focused on what expansion could realistically look like — not on "
            "whether to start at all."
        )
    if stage == "researching":
        return (
            "Since you're still researching, treat this report as an early-stage guide rather "
            "than a final decision — validate its assumptions against your own village before "
            "putting in any capital."
        )
    return (
        "Since this is currently just an idea, validate every assumption in this report by "
        "talking to 3-5 real people in your village before committing any capital."
    )


def build_feasibility_report(req: AdvisoryRequest, project_cost: float) -> FeasibilityReport:
    # Gather all real data
    profile    = market_data.get_district_profile(req.district)
    market_reach = _build_market_reach(req)
    competitor   = _build_competitor_mapping(req)
    pricing      = _build_pricing(req, project_cost)

    category = req.business_category_other or req.business_category.value
    opportunity = _build_opportunity_analysis(req, competitor, profile)
    swot        = _build_swot(req, competitor, project_cost, profile)
    threats     = _build_threats(req, competitor)
    score       = _score_opportunity(competitor, market_reach, profile, req.business_category.value)
    breakdown   = _score_breakdown(competitor, market_reach, profile, req.business_category.value)
    narrative   = _narrative_summary(req, score, breakdown, competitor, pricing, profile)

    overall_confidence = ConfidenceLevel.high if profile.get("found") else ConfidenceLevel.medium

    if project_cost <= 140_000:
        matched_scheme_name = "NSFDC Micro Finance Scheme"
    elif project_cost <= 1_000_000:
        matched_scheme_name = "NSFDC SUVIDHA Loan Scheme"
    elif project_cost <= 5_000_000:
        matched_scheme_name = "NSFDC UTKARSH Loan Scheme"
    else:
        matched_scheme_name = "no scheme in this tool's scope (project cost exceeds Rs. 50 Lakh)"

    lang = i18n.normalize_language(req.language)
    next_steps = i18n.actionable_next_steps(
        lang, req.district, matched_scheme_name, project_cost, category,
        pricing.suggested_price_range_min, pricing.suggested_price_range_max, pricing.unit,
    )

    revenue_projection = revenue_estimator.build_revenue_projection(
        category=req.business_category.value,
        project_cost=project_cost,
        consumer_base=market_reach.estimated_consumer_base,
        competitors=competitor.estimated_similar_businesses_nearby,
        current_monthly_revenue=(
            req.current_monthly_revenue
            if req.business_stage == "ongoing" or (req.business_stage and req.business_stage.value == "ongoing")
            else None
        ),
    )

    stage_value = req.business_stage.value if req.business_stage else "idea"
    journey_flowchart = [
        FlowchartStep(**step) for step in i18n.flowchart_steps(lang, stage_value)
    ]

    return FeasibilityReport(
        business_opportunity_score=score,
        overall_confidence=overall_confidence,
        market_reach=market_reach,
        opportunity_analysis=opportunity,
        swot=swot,
        threats=threats,
        competitor_mapping=competitor,
        pricing=pricing,
        narrative_summary=narrative,
        actionable_next_steps=next_steps,
        revenue_projection=revenue_projection,
        journey_flowchart=journey_flowchart,
    )
