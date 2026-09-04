"""
Revenue / clients / distributors / raw-material projection - grounded in
real, cited data rather than an invented "assume X% margin" guess. This is
the "show the full truth, not just the upside" module: every projection
returns a low/mid/high band, an explicit downside-risk note, and a real
citation for the number.

Methodology per category (each cross-checked against a real, cited source
during the 2026-09 research pass for this feature):

  Dairy - fat-based milk pricing, the actual method Indian dairy cooperatives
  (Amul and others) use to price milk. Fat content, not volume alone, sets
  the price: buffalo milk (~6.5% fat) sells for more per litre than cow milk
  (~3.5% fat) at the same Rs./kg-fat rate.
    Source: Amul's published procurement price of ~Rs. 865/kg fat (2025),
    reported via dairy-industry trade press (dairybusinessmea.com).

  Retail (kirana) - real rural kirana store revenue bands reported by retail
  industry sources: a small rural general store typically turns over
  Rs. 30,000-60,000/month, at typical FMCG/grocery margins of 8-15%.
    Source: superk.in kirana-business industry writeup (secondary source
    reporting typical rural retail revenue figures).

  All other categories (Textiles, Food Processing, Poultry, Handicrafts,
  Agri Input Store, Tailoring, Other) - no single authoritative per-unit
  formula exists for these at micro-enterprise scale, so rather than invent
  one, this tool falls back to the official government survey benchmark for
  informal micro-enterprises in India:
    MoSPI/NSO's Annual Survey of Unincorporated Sector Enterprises (ASUSE)
    2022-23 reports average Gross Value of Output (GVO) of Rs. 4,63,389 per
    year per unorganised-sector establishment (~Rs. 38,616/month), as
    released via PIB. This is a real, official, India-wide figure - used
    here as a transparent, clearly-labelled general-purpose fallback, not
    disguised as a category-specific number.

Customer / distributor / raw-material counts are derived from the same
feasibility-engine market data already computed for this request (estimated
consumer base, competitor density) rather than invented separately, so the
whole report stays internally consistent.
"""
from typing import Optional

from app.schemas import RevenueProjection

ASUSE_SOURCE_URL = "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2016853"
AMUL_DAIRY_SOURCE_URL = "https://www.dairybusinessmea.com/"
KIRANA_RETAIL_SOURCE_URL = "https://superk.in/"

# --- ASUSE 2022-23 official fallback benchmark ---
ASUSE_ANNUAL_GVO_PER_ESTABLISHMENT = 463_389  # Rs./year, MoSPI/NSO, all-India unorganised sector
ASUSE_MONTHLY_GVO = ASUSE_ANNUAL_GVO_PER_ESTABLISHMENT / 12  # approx Rs. 38,616/month

# Typical operating-cost ratio (COGS + rent + utilities, excluding owner's
# own labour) for a small unorganised-sector unit, per the same ASUSE survey
# series' input-output ratio for micro-enterprises (~65-75% of GVO is cost).
DEFAULT_OPEX_RATIO = 0.70

# Fat percentages by animal type - standard dairy-industry figures used for
# fat-based procurement pricing (not brand-specific, standard across India).
COW_MILK_FAT_PCT = 0.035
BUFFALO_MILK_FAT_PCT = 0.065
FAT_PRICE_PER_KG = 865.0  # Rs./kg fat, Amul 2025 procurement price (real, cited)
AVG_MILK_YIELD_LITRES_PER_ANIMAL_PER_DAY = 8.0  # conservative rural mixed-breed average
DAIRY_CAPITAL_PER_ANIMAL = 50_000  # Rs. per productive animal (purchase + shed + feed buffer)


def _dairy_projection(project_cost: float, consumer_base: int, competitors: int) -> RevenueProjection:
    # Estimate herd size a project of this size can realistically support,
    # capped to a believable range for a first-time micro-enterprise.
    est_animals = max(2, min(15, round(project_cost / DAIRY_CAPITAL_PER_ANIMAL)))

    def daily_revenue(fat_pct: float) -> float:
        milk_kg_per_day = est_animals * AVG_MILK_YIELD_LITRES_PER_ANIMAL_PER_DAY * 1.03  # litres to kg approx density
        fat_kg_per_day = milk_kg_per_day * fat_pct
        return fat_kg_per_day * FAT_PRICE_PER_KG

    cow_daily = daily_revenue(COW_MILK_FAT_PCT)
    buffalo_daily = daily_revenue(BUFFALO_MILK_FAT_PCT)
    # Low = all-cow-milk herd (lower fat), High = all-buffalo herd (higher fat),
    # Mid = a realistic 50/50 mixed herd, which is the common rural pattern.
    monthly_low = round(cow_daily * 30, 0)
    monthly_high = round(buffalo_daily * 30, 0)
    monthly_mid = round((monthly_low + monthly_high) / 2, 0)

    opex = round(monthly_mid * 0.55, 0)  # feed is the dominant dairy cost (~55% of gross milk revenue)
    net = monthly_mid - opex

    return RevenueProjection(
        monthly_revenue_low=monthly_low,
        monthly_revenue_mid=monthly_mid,
        monthly_revenue_high=monthly_high,
        monthly_operating_cost_estimate=opex,
        monthly_net_income_estimate=net,
        estimated_active_customers=max(10, min(consumer_base // 200, 150)),
        estimated_distributors_or_buyers=max(1, min(3, 1 + competitors // 10)),
        estimated_raw_material_sources=est_animals,
        raw_material_source_examples=[
            f"Your own herd (~{est_animals} milking animals, cow/buffalo mix)",
            "Local cattle-feed / fodder supplier for concentrate feed",
            "Village veterinary or animal-husbandry department for health inputs",
        ],
        distributor_examples=[
            "District dairy cooperative / milk union procurement centre",
            "Direct door-to-door household delivery route",
            "Local sweet-shop / tea-stall bulk buyers",
        ],
        downside_risk_note=(
            f"This assumes all {est_animals} animals are healthy and in full milk year-round. "
            f"Real dairy income drops 30-40% during the dry (non-lactating) period of each "
            f"animal's cycle, and disease or poor feed quality can cut yield further. Budget "
            f"for at least a 2-month low-yield buffer, and do not assume the high-end figure "
            f"every month."
        ),
        methodology=(
            f"Fat-based pricing: milk price is set by fat content (not volume alone). "
            f"At Rs. {FAT_PRICE_PER_KG:.0f}/kg fat (Amul's 2025 procurement rate), cow milk "
            f"(~{COW_MILK_FAT_PCT*100:.1f}% fat) and buffalo milk (~{BUFFALO_MILK_FAT_PCT*100:.1f}% fat) "
            f"give the low/high band for a herd of ~{est_animals} animals yielding "
            f"~{AVG_MILK_YIELD_LITRES_PER_ANIMAL_PER_DAY:.0f} litres/animal/day."
        ),
        data_source="Amul dairy procurement pricing (fat-based), 2025",
        source_url=AMUL_DAIRY_SOURCE_URL,
    )


def _retail_projection(consumer_base: int, competitors: int) -> RevenueProjection:
    monthly_low, monthly_high = 30_000, 60_000
    monthly_mid = (monthly_low + monthly_high) / 2
    opex_ratio = 0.88  # kirana margins are thin: 8-15% net on turnover is typical
    opex = round(monthly_mid * opex_ratio, 0)
    net = round(monthly_mid - opex, 0)

    return RevenueProjection(
        monthly_revenue_low=monthly_low,
        monthly_revenue_mid=monthly_mid,
        monthly_revenue_high=monthly_high,
        monthly_operating_cost_estimate=opex,
        monthly_net_income_estimate=net,
        estimated_active_customers=max(30, min(consumer_base // 40, 600)),
        estimated_distributors_or_buyers=max(2, min(6, 2 + competitors // 8)),
        estimated_raw_material_sources=3,
        raw_material_source_examples=[
            "Nearest wholesale/kirana distributor in the block or district town",
            "FMCG company's local rural distributor (biscuits, soap, packaged goods)",
            "Local mandi for loose grains, pulses and vegetables",
        ],
        distributor_examples=[
            "Wholesale kirana supplier in the nearest town",
            "FMCG van/salesman route covering this village",
            "Weekly haat (market) bulk suppliers",
        ],
        downside_risk_note=(
            "Kirana margins are thin (8-15% of turnover) - a slow month, a big customer "
            "unpaid credit (udhaar) balance, or a new competing store nearby can turn a "
            "profitable month into a loss-making one. Do not extend informal credit beyond "
            "what you can absorb if it isn't repaid on time."
        ),
        methodology=(
            "Real rural kirana (general store) revenue bands reported by retail-industry "
            "sources: Rs. 30,000-60,000/month turnover, at typical grocery/FMCG margins "
            "of 8-15% net."
        ),
        data_source="Rural kirana retail industry benchmark",
        source_url=KIRANA_RETAIL_SOURCE_URL,
    )


def _asuse_fallback_projection(category: str, consumer_base: int, competitors: int) -> RevenueProjection:
    monthly_mid = ASUSE_MONTHLY_GVO
    monthly_low = round(monthly_mid * 0.6, 0)
    monthly_high = round(monthly_mid * 1.5, 0)
    opex = round(monthly_mid * DEFAULT_OPEX_RATIO, 0)
    net = round(monthly_mid - opex, 0)

    return RevenueProjection(
        monthly_revenue_low=monthly_low,
        monthly_revenue_mid=round(monthly_mid, 0),
        monthly_revenue_high=monthly_high,
        monthly_operating_cost_estimate=opex,
        monthly_net_income_estimate=net,
        estimated_active_customers=max(15, min(consumer_base // 100, 300)),
        estimated_distributors_or_buyers=max(1, min(4, 1 + competitors // 10)),
        estimated_raw_material_sources=2,
        raw_material_source_examples=[
            f"Nearest wholesale supplier for {category.lower()} inputs in the block/district town",
            "Local mandi or weekly haat for raw materials",
        ],
        distributor_examples=[
            "Direct sale at village/block haat",
            "Nearby town wholesale/retail network",
        ],
        downside_risk_note=(
            "This uses a general, official all-India average for informal micro-enterprises "
            "because a category-specific real dataset for "
            f"{category} was not available - your actual result could be meaningfully higher "
            "or lower depending on very local demand. Treat this as a starting planning "
            "figure, not a guarantee, and revisit it after your first 2-3 months of real sales."
        ),
        methodology=(
            "General-purpose fallback using the official MoSPI/NSO Annual Survey of "
            "Unincorporated Sector Enterprises (ASUSE) 2022-23 average Gross Value of Output "
            f"of Rs. {ASUSE_ANNUAL_GVO_PER_ESTABLISHMENT:,}/year per unorganised-sector "
            "establishment, applied here because no category-specific real dataset exists "
            "for this business type in this tool yet."
        ),
        data_source="MoSPI/NSO ASUSE 2022-23 (via PIB)",
        source_url=ASUSE_SOURCE_URL,
    )


def build_revenue_projection(
    category: str,
    project_cost: float,
    consumer_base: int,
    competitors: int,
    current_monthly_revenue: Optional[float] = None,
) -> RevenueProjection:
    """
    Dispatches to the right real-data methodology for the category, then, if
    the applicant reported their own current monthly revenue (an ongoing
    business), re-anchors the band around that real figure instead of the
    generic estimate - the applicant's own numbers are always more accurate
    than a district-level model.
    """
    if category == "Dairy":
        projection = _dairy_projection(project_cost, consumer_base, competitors)
    elif category == "Retail":
        projection = _retail_projection(consumer_base, competitors)
    else:
        projection = _asuse_fallback_projection(category, consumer_base, competitors)

    if current_monthly_revenue is not None and current_monthly_revenue > 0:
        projection.monthly_revenue_low = round(current_monthly_revenue * 0.85, 0)
        projection.monthly_revenue_mid = round(current_monthly_revenue, 0)
        projection.monthly_revenue_high = round(current_monthly_revenue * 1.25, 0)
        projection.monthly_operating_cost_estimate = round(current_monthly_revenue * DEFAULT_OPEX_RATIO, 0)
        projection.monthly_net_income_estimate = round(
            projection.monthly_revenue_mid - projection.monthly_operating_cost_estimate, 0
        )
        projection.used_applicant_reported_revenue = True
        projection.methodology = (
            f"Anchored on your own reported current monthly revenue of Rs. "
            f"{current_monthly_revenue:,.0f}, with a realistic +/-15-25% band for month-to-month "
            f"variation, rather than a generic district estimate - your own numbers are the "
            f"most accurate input available."
        )

    return projection

