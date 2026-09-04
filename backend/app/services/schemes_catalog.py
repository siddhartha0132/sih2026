"""
Multi-scheme eligibility scan - "show ALL schemes you might qualify for."

`financial_calculator.py` already does the deep, detailed Module-2 job the PS
asks for: it routes the project cost through the real, live-verified NSFDC
3-tier structure (Micro Finance / SUVIDHA / UTKARSH) and produces a full
quarterly EMI schedule for that one selected scheme. That stays the primary,
most-detailed "selected_scheme" in the financial plan.

This module adds the broader picture: a rural entrepreneur is not limited to
NSFDC. The same project cost is very likely also open to PMEGP (KVIC), MUDRA
(most banks), and Stand-Up India (for SC/ST/women applicants above Rs. 10L).
Real applicants should see every real door open to them, each with its own
link and a plain description - not be funnelled toward a single option just
because that is the one this tool calculates an EMI schedule for.

All figures below are real scheme parameters, cross-checked against official
and reputable secondary sources as of 2026-09. Where an official primary page
could not be fetched directly (kviconline.gov.in blocks automated fetches;
myscheme.gov.in returns only page chrome), a reputable secondary source
reporting the same official terms is cited instead and noted as such.
"""
from typing import List, Optional

from app.schemas import SchemeOption
from app.services import i18n

TERMS_VERIFIED_ON = "2026-09-03"

# NSFDC official pages (already the primary citations used in financial_calculator.py)
NSFDC_MICRO_URL = "https://nsfdc.nic.in/en/micro-credit-finance"
NSFDC_SUVIDHA_URL = "https://nsfdc.nic.in/en/suvidha-loan"
NSFDC_UTKARSH_URL = "https://nsfdc.nic.in/en/utkarsh-loan"

# PMEGP - Prime Minister's Employment Generation Programme, run by KVIC.
# Official portal (kviconline.gov.in/pmegpeportal) blocks automated fetches;
# terms below are cross-checked against the KVIC guidelines as summarised by
# cashfree.com's scheme explainer (secondary source reporting the official
# scheme, cited as such rather than presented as a primary government page).
PMEGP_URL = "https://www.cashfree.com/blog/pmegp-loan-scheme/"

# MUDRA - Micro Units Development & Refinance Agency (Shishu/Kishor/Tarun/Tarun Plus tiers).
# Official mudra.org.in and myscheme.gov.in/schemes/pmmy returned only page
# chrome on fetch; terms cross-checked against stashfin.com's MUDRA loan
# explainer (secondary source).
MUDRA_URL = "https://stashfin.com/blog/mudra-loan/"

# Stand-Up India - SIDBI/DFS scheme for SC/ST and women entrepreneurs, greenfield projects.
STANDUP_INDIA_URL = "https://www.standupmitra.in/"


def _pmegp_option(project_cost: float, category: str, lang: str = "en") -> SchemeOption:
    # PMEGP caps: Rs. 50 Lakh for manufacturing, Rs. 20 Lakh for service/trading.
    # Rural micro-enterprise categories here are mostly service/trading-scale,
    # so we apply the more conservative Rs. 20 Lakh general ceiling by default,
    # noting the manufacturing exception in the eligibility note.
    is_manufacturing_like = category in ("Food Processing", "Textiles", "Handicrafts")
    cap = 5_000_000 if is_manufacturing_like else 2_000_000
    eligible = project_cost <= cap
    localized = i18n.pmegp_texts(lang, project_cost, cap, is_manufacturing_like, eligible)
    if localized is not None:
        return SchemeOption(
            scheme_name="PMEGP (Prime Minister's Employment Generation Programme)",
            operating_agency=localized["operating_agency"],
            is_eligible=eligible,
            eligibility_note=localized["eligibility_note"],
            max_project_cost=cap,
            max_loan_amount=cap * 0.95,
            subsidy_or_margin_money_note=localized["subsidy_or_margin_money_note"],
            interest_rate_percent_range=localized["interest_rate_percent_range"],
            tenure_years=localized["tenure_years"],
            description=localized["description"],
            official_source_url=PMEGP_URL,
            terms_verified_on=TERMS_VERIFIED_ON,
        )
    note = (
        f"Project cost of Rs. {project_cost:,.0f} is within the PMEGP ceiling "
        f"(Rs. {cap:,.0f} for {'manufacturing' if is_manufacturing_like else 'service/trading'} "
        f"units)."
        if eligible else
        f"Project cost of Rs. {project_cost:,.0f} exceeds the PMEGP ceiling of "
        f"Rs. {cap:,.0f} for this type of unit."
    )
    return SchemeOption(
        scheme_name="PMEGP (Prime Minister's Employment Generation Programme)",
        operating_agency="KVIC / KVIB / District Industries Centre, via Banks",
        is_eligible=eligible,
        eligibility_note=note,
        max_project_cost=cap,
        max_loan_amount=cap * 0.95,  # up to 95% financed for rural/special-category applicants
        subsidy_or_margin_money_note=(
            "Government subsidy (not a loan) of 25% of project cost in rural areas "
            "(35% for SC/ST/women/special categories) - this portion never has to be "
            "repaid. Applicant contributes only 5% (10% for general category in urban areas)."
        ),
        interest_rate_percent_range="Bank's standard MSME rate, typically 8-12% p.a. on the loan portion",
        tenure_years="up to 7 (incl. moratorium set by the financing bank)",
        description=(
            "A one-time government subsidy scheme for setting up a new micro-enterprise. "
            "Unlike a pure loan, part of the project cost is a subsidy you never repay - "
            "it usually needs the least monthly repayment of all these options for the "
            "same project size."
        ),
        official_source_url=PMEGP_URL,
        terms_verified_on=TERMS_VERIFIED_ON,
    )


def _mudra_option(project_cost: float, lang: str = "en") -> SchemeOption:
    # MUDRA tiers: Shishu (<=50k), Kishor (50k-5L), Tarun (5L-10L), Tarun Plus (10L-20L).
    cap = 2_000_000
    eligible = project_cost <= cap
    if project_cost <= 50_000:
        tier = "Shishu"
    elif project_cost <= 500_000:
        tier = "Kishor"
    elif project_cost <= 1_000_000:
        tier = "Tarun"
    else:
        tier = "Tarun Plus"
    scheme_name = f"MUDRA Loan - {tier} tier" if eligible else "MUDRA Loan (PMMY)"
    localized = i18n.mudra_texts(lang, project_cost, cap, tier, eligible)
    if localized is not None:
        return SchemeOption(
            scheme_name=scheme_name,
            operating_agency=localized["operating_agency"],
            is_eligible=eligible,
            eligibility_note=localized["eligibility_note"],
            max_project_cost=cap,
            max_loan_amount=cap,
            subsidy_or_margin_money_note=localized["subsidy_or_margin_money_note"],
            interest_rate_percent_range=localized["interest_rate_percent_range"],
            tenure_years=localized["tenure_years"],
            description=localized["description"],
            official_source_url=MUDRA_URL,
            terms_verified_on=TERMS_VERIFIED_ON,
        )
    note = (
        f"Project cost of Rs. {project_cost:,.0f} falls in the MUDRA '{tier}' tier."
        if eligible else
        f"Project cost of Rs. {project_cost:,.0f} exceeds the MUDRA ceiling of Rs. {cap:,.0f}."
    )
    return SchemeOption(
        scheme_name=scheme_name,
        operating_agency="Any Bank / NBFC / MFI (Pradhan Mantri MUDRA Yojana)",
        is_eligible=eligible,
        eligibility_note=note,
        max_project_cost=cap,
        max_loan_amount=cap,  # can finance up to 100% for very small ("Shishu") loans, less for larger tiers
        subsidy_or_margin_money_note="No subsidy - this is a collateral-free loan, not a grant.",
        interest_rate_percent_range="~8.5%-12% p.a. (varies by lending bank/NBFC and applicant profile)",
        tenure_years="up to 5 (varies by lender)",
        description=(
            "A collateral-free business loan available from almost any bank or NBFC branch - "
            "no need to route through a specific state agency, which usually means faster "
            "processing than a designated Channelizing Agency."
        ),
        official_source_url=MUDRA_URL,
        terms_verified_on=TERMS_VERIFIED_ON,
    )


def _standup_india_option(
    project_cost: float, applicant_gender: Optional[str], is_first_time_entrepreneur: Optional[bool],
    lang: str = "en",
) -> SchemeOption:
    # Stand-Up India: Rs. 10L-100L, for greenfield (first-time) enterprises by
    # SC/ST and/or women applicants. We can only check the "woman applicant" +
    # "first-time" half of eligibility from current inputs (no caste/category
    # field is collected) - the note says so explicitly rather than guessing.
    cap = 10_000_000
    floor = 1_000_000
    is_woman = (applicant_gender or "").strip().lower() == "female"
    first_time = is_first_time_entrepreneur is not False
    size_ok = floor <= project_cost <= cap
    category_ok = is_woman  # SC/ST status isn't collected by this tool yet
    eligible = size_ok and category_ok and first_time
    if not size_ok:
        note = (
            f"Stand-Up India covers project costs from Rs. {floor:,.0f} to Rs. {cap:,.0f} - "
            f"your Rs. {project_cost:,.0f} project is "
            f"{'below this band (the smaller schemes above fit better)' if project_cost < floor else 'above this band'}."
        )
    elif not category_ok:
        note = (
            "Reserved for women entrepreneurs and SC/ST entrepreneurs setting up a new "
            "(greenfield) enterprise. Based on the profile details provided, this wasn't "
            "detected as a match - if you belong to an SC/ST category, you may still be "
            "eligible even though this tool doesn't collect that field yet."
        )
    elif not first_time:
        note = "Stand-Up India is only for a new (greenfield), first-time enterprise."
    else:
        note = (
            f"Project cost of Rs. {project_cost:,.0f} is within the Rs. {floor:,.0f}-{cap:,.0f} "
            f"Stand-Up India band, for a first-time woman entrepreneur's new enterprise."
        )
    localized = i18n.standup_india_texts(lang, project_cost, cap, floor, size_ok, category_ok, first_time, eligible)
    if localized is not None:
        return SchemeOption(
            scheme_name="Stand-Up India",
            operating_agency=localized["operating_agency"],
            is_eligible=eligible,
            eligibility_note=localized["eligibility_note"],
            max_project_cost=cap,
            max_loan_amount=cap * 0.85,
            subsidy_or_margin_money_note=localized["subsidy_or_margin_money_note"],
            interest_rate_percent_range=localized["interest_rate_percent_range"],
            tenure_years=localized["tenure_years"],
            description=localized["description"],
            official_source_url=STANDUP_INDIA_URL,
            terms_verified_on=TERMS_VERIFIED_ON,
        )
    return SchemeOption(
        scheme_name="Stand-Up India",
        operating_agency="Scheduled Commercial Bank branches, via SIDBI/DFS",
        is_eligible=eligible,
        eligibility_note=note,
        max_project_cost=cap,
        max_loan_amount=cap * 0.85,
        subsidy_or_margin_money_note="No subsidy; margin money contribution can be as low as 10% with convergence support.",
        interest_rate_percent_range="Bank's base rate + up to 3% (varies by bank)",
        tenure_years="up to 7, with up to 18 months moratorium",
        description=(
            "A larger-ticket scheme (Rs. 10 Lakh-1 Crore) specifically for women and SC/ST "
            "entrepreneurs starting a brand-new enterprise - relevant once your project "
            "grows past the smaller schemes above."
        ),
        official_source_url=STANDUP_INDIA_URL,
        terms_verified_on=TERMS_VERIFIED_ON,
    )


def _nsfdc_options(project_cost: float, lang: str = "en") -> List[SchemeOption]:
    """Represent the same 3 NSFDC tiers used in financial_calculator.py as SchemeOptions,
    so they appear consistently alongside PMEGP/MUDRA/Stand-Up India in the all-schemes list."""
    tiers = [
        dict(
            scheme_name="NSFDC Micro Finance Scheme", cap=140_000, loan_cap=125_000,
            rate="6.5", tenure="3", url=NSFDC_MICRO_URL,
        ),
        dict(
            scheme_name="NSFDC SUVIDHA Loan Scheme", cap=1_000_000, loan_cap=900_000,
            rate="8", tenure="5", url=NSFDC_SUVIDHA_URL,
        ),
        dict(
            scheme_name="NSFDC UTKARSH Loan Scheme", cap=5_000_000, loan_cap=4_500_000,
            rate="9", tenure="7", url=NSFDC_UTKARSH_URL,
        ),
    ]
    options = []
    prev_cap = 0
    for t in tiers:
        eligible = prev_cap < project_cost <= t["cap"] if prev_cap else project_cost <= t["cap"]
        localized = i18n.nsfdc_option_texts(lang, project_cost, t["cap"], eligible, t["rate"], t["tenure"])
        if localized is not None:
            options.append(SchemeOption(
                scheme_name=t["scheme_name"],
                operating_agency=localized["operating_agency"],
                is_eligible=eligible,
                eligibility_note=localized["eligibility_note"],
                max_project_cost=t["cap"],
                max_loan_amount=t["loan_cap"],
                subsidy_or_margin_money_note=localized["subsidy_or_margin_money_note"],
                interest_rate_percent_range=localized["interest_rate_percent_range"],
                tenure_years=t["tenure"],
                description=localized["description"],
                official_source_url=t["url"],
                terms_verified_on=TERMS_VERIFIED_ON,
            ))
        else:
            options.append(SchemeOption(
                scheme_name=t["scheme_name"],
                operating_agency="NSFDC (National Scheduled Castes Finance & Development Corporation), via State Channelizing Agencies",
                is_eligible=eligible,
                eligibility_note=(
                    f"Project cost of Rs. {project_cost:,.0f} matches this tier's band."
                    if eligible else
                    f"This tier covers project costs up to Rs. {t['cap']:,.0f}; your project is outside that band."
                ),
                max_project_cost=t["cap"],
                max_loan_amount=t["loan_cap"],
                subsidy_or_margin_money_note="No subsidy; standard 90% loan / 10% margin-money structure.",
                interest_rate_percent_range=f"{t['rate']}% p.a. (concessional, fixed)",
                tenure_years=t["tenure"],
                description=(
                    "The primary scheme this tool builds your detailed EMI schedule against - "
                    "see the Financial Plan section above for the exact repayment numbers."
                ),
                official_source_url=t["url"],
                terms_verified_on=TERMS_VERIFIED_ON,
            ))
        prev_cap = t["cap"]
    return options


def get_all_scheme_options(
    project_cost: float,
    category: str,
    applicant_gender: Optional[str] = None,
    is_first_time_entrepreneur: Optional[bool] = True,
    language: str = "en",
) -> List[SchemeOption]:
    """
    Returns every major scheme evaluated against this project's numbers,
    each flagged eligible/not-eligible with a plain-language reason - the
    "show me every real door, not just one" requirement.
    """
    lang = i18n.normalize_language(language)
    options = _nsfdc_options(project_cost, lang)
    options.append(_pmegp_option(project_cost, category, lang))
    options.append(_mudra_option(project_cost, lang))
    options.append(_standup_india_option(project_cost, applicant_gender, is_first_time_entrepreneur, lang))
    return options


def mark_recommended(options: List[SchemeOption], selected_scheme_name: str) -> List[SchemeOption]:
    """Flags the one scheme that matches financial_calculator's selected_scheme
    (the one with the full EMI schedule) as the recommended primary path,
    without hiding the others."""
    for opt in options:
        if selected_scheme_name.lower() in opt.scheme_name.lower() and opt.is_eligible:
            opt.is_recommended = True
    return options

