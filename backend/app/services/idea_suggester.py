"""
Reverse-flow: "describe your business idea in your own words" -> suggest a
business category, a plausible starting margin-capital figure, and a likely
scheme, so an applicant who doesn't know the formal category names can still
get started. This is a keyword-matching classifier, not an LLM call - kept
fully deterministic and auditable like the rest of the financial engine, and
transparent about being a best-effort guess rather than a certainty.
"""
import re
from typing import Dict, List, Tuple

from app.schemas import BusinessCategory, ConfidenceLevel, IdeaSuggestionResponse

# Keyword sets per category, in English and common Hindi/Hinglish terms a
# rural applicant might actually type. Order matters only for tie-breaking.
CATEGORY_KEYWORDS: Dict[BusinessCategory, List[str]] = {
    BusinessCategory.dairy: [
        "milk", "doodh", "dairy", "cow", "gaay", "buffalo", "bhains", "ghee", "curd", "dahi", "paneer",
    ],
    BusinessCategory.retail: [
        "kirana", "shop", "dukan", "store", "grocery", "general store", "provisions", "supermarket",
    ],
    BusinessCategory.textiles: [
        "cloth", "saree", "sari", "fabric", "kapda", "weaving", "loom", "textile", "garment shop",
    ],
    BusinessCategory.food_processing: [
        "pickle", "achar", "papad", "snack", "bakery", "namkeen", "spices", "masala", "food processing",
        "jam", "juice", "sweets", "mithai",
    ],
    BusinessCategory.poultry: [
        "chicken", "poultry", "murgi", "egg", "anda", "hatchery", "broiler",
    ],
    BusinessCategory.handicrafts: [
        "handicraft", "handmade", "pottery", "matka", "craft", "embroidery", "basket", "bamboo",
        "wood carving", "artisan",
    ],
    BusinessCategory.agri_input_store: [
        "seed", "beej", "fertilizer", "khad", "pesticide", "agri input", "farm input", "agriculture shop",
    ],
    BusinessCategory.tailoring: [
        "tailor", "tailoring", "stitching", "silai", "boutique", "sewing", "darzi",
    ],
}

# Realistic starting margin-capital suggestion (Rs.) per category - anchored
# to the low end of what a first-time rural entrepreneur in that category
# typically needs as their own 10% contribution, consistent with the
# category-specific project sizes elsewhere in this tool (e.g. dairy herd
# capital in revenue_estimator.py).
CATEGORY_STARTING_MARGIN: Dict[BusinessCategory, float] = {
    BusinessCategory.dairy: 40_000,
    BusinessCategory.retail: 50_000,
    BusinessCategory.textiles: 60_000,
    BusinessCategory.food_processing: 45_000,
    BusinessCategory.poultry: 35_000,
    BusinessCategory.handicrafts: 25_000,
    BusinessCategory.agri_input_store: 70_000,
    BusinessCategory.tailoring: 20_000,
    BusinessCategory.other: 50_000,
}


def _likely_scheme_hint(margin_capital: float) -> str:
    project_cost = margin_capital / 0.10
    if project_cost <= 140_000:
        return "likely the NSFDC Micro Finance Scheme (project cost under Rs. 1.40 Lakh)"
    if project_cost <= 1_000_000:
        return "likely the NSFDC SUVIDHA Loan Scheme (project cost Rs. 1.40-10 Lakh)"
    if project_cost <= 5_000_000:
        return "likely the NSFDC UTKARSH Loan Scheme (project cost Rs. 10-50 Lakh), or PMEGP/MUDRA"
    return "likely PMEGP, MUDRA, or Stand-Up India (project cost above the NSFDC Rs. 50 Lakh ceiling)"


def suggest_from_idea(description: str, available_margin_capital: float = None) -> IdeaSuggestionResponse:
    text = description.lower()
    scores: List[Tuple[BusinessCategory, int, List[str]]] = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = [kw for kw in keywords if re.search(re.escape(kw.lower()), text)]
        if matched:
            scores.append((category, len(matched), matched))

    if not scores:
        margin = available_margin_capital or CATEGORY_STARTING_MARGIN[BusinessCategory.other]
        return IdeaSuggestionResponse(
            detected_business_category=BusinessCategory.other,
            detected_business_category_other=description[:80],
            matched_keywords=[],
            suggested_starting_margin_capital=margin,
            confidence=ConfidenceLevel.low,
            explanation=(
                "We couldn't confidently match your idea to one of our standard categories from "
                "the words used - we've set it as 'Other' so you can describe it yourself. Feel "
                "free to pick the closest category from the list instead if one fits better."
            ),
            likely_scheme_hint=_likely_scheme_hint(margin),
        )

    scores.sort(key=lambda x: x[1], reverse=True)
    best_category, match_count, matched_keywords = scores[0]
    margin = available_margin_capital or CATEGORY_STARTING_MARGIN[best_category]
    confidence = ConfidenceLevel.high if match_count >= 2 else ConfidenceLevel.medium

    return IdeaSuggestionResponse(
        detected_business_category=best_category,
        detected_business_category_other=None,
        matched_keywords=matched_keywords,
        suggested_starting_margin_capital=margin,
        confidence=confidence,
        explanation=(
            f"Based on the words '{', '.join(matched_keywords)}' in your description, this looks "
            f"like a {best_category.value} business. If you already have some savings to put in, "
            f"enter that instead - otherwise Rs. {margin:,.0f} is a realistic amount to start "
            f"exploring with for a {best_category.value.lower()} business of this scale."
        ),
        likely_scheme_hint=_likely_scheme_hint(margin),
    )

