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
from app.services import i18n

# Keyword sets per category, in English and common Hindi/Hinglish terms a
# rural applicant might actually type. Order matters only for tie-breaking.
CATEGORY_KEYWORDS: Dict[BusinessCategory, List[str]] = {
    BusinessCategory.dairy: [
        "milk", "doodh", "dairy", "cow", "gaay", "buffalo", "bhains", "ghee", "curd", "dahi", "paneer",
        # Devanagari (Hindi script) — a Hindi-language user typing natively, not just
        # romanized Hinglish, must match too.
        "दूध", "डेयरी", "गाय", "भैंस", "भेंस", "घी", "दही", "पनीर",
    ],
    BusinessCategory.retail: [
        "kirana", "shop", "dukan", "store", "grocery", "general store", "provisions", "supermarket",
        "किराना", "दुकान", "परचून", "जनरल स्टोर",
    ],
    BusinessCategory.textiles: [
        "cloth", "saree", "sari", "fabric", "kapda", "weaving", "loom", "textile", "garment shop",
        "कपड़ा", "साड़ी", "बुनाई", "करघा", "वस्त्र",
    ],
    BusinessCategory.food_processing: [
        "pickle", "achar", "papad", "snack", "bakery", "namkeen", "spices", "masala", "food processing",
        "jam", "juice", "sweets", "mithai",
        "अचार", "पापड़", "नमकीन", "मसाला", "मिठाई", "बेकरी",
    ],
    BusinessCategory.poultry: [
        "chicken", "poultry", "murgi", "egg", "anda", "hatchery", "broiler",
        "मुर्गी", "मुर्गा", "अंडा", "पोल्ट्री",
    ],
    BusinessCategory.handicrafts: [
        "handicraft", "handmade", "pottery", "matka", "craft", "embroidery", "basket", "bamboo",
        "wood carving", "artisan",
        "हस्तशिल्प", "मिट्टी के बर्तन", "मटका", "कढ़ाई", "टोकरी", "बांस",
    ],
    BusinessCategory.agri_input_store: [
        "seed", "beej", "fertilizer", "khad", "pesticide", "agri input", "farm input", "agriculture shop",
        "बीज", "खाद", "कीटनाशक", "उर्वरक", "खेती की दुकान",
    ],
    BusinessCategory.tailoring: [
        "tailor", "tailoring", "stitching", "silai", "boutique", "sewing", "darzi",
        "सिलाई", "दर्जी", "बुटीक",
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


def _likely_scheme_hint(margin_capital: float, lang: str = "en") -> str:
    project_cost = margin_capital / 0.10
    if project_cost <= 140_000:
        tier_key, en = "micro", "likely the NSFDC Micro Finance Scheme (project cost under Rs. 1.40 Lakh)"
    elif project_cost <= 1_000_000:
        tier_key, en = "suvidha", "likely the NSFDC SUVIDHA Loan Scheme (project cost Rs. 1.40-10 Lakh)"
    elif project_cost <= 5_000_000:
        tier_key, en = "utkarsh", "likely the NSFDC UTKARSH Loan Scheme (project cost Rs. 10-50 Lakh), or PMEGP/MUDRA"
    else:
        tier_key, en = "above", "likely PMEGP, MUDRA, or Stand-Up India (project cost above the NSFDC Rs. 50 Lakh ceiling)"
    return i18n.likely_scheme_hint(lang, tier_key) or en


def suggest_from_idea(description: str, available_margin_capital: float = None, language: str = "en") -> IdeaSuggestionResponse:
    lang = i18n.normalize_language(language)
    text = description.lower()
    # Score by keyword *specificity* (total matched character length), not raw
    # match count. A generic word like "shop" or "store" appears in almost any
    # retail-ish description and would otherwise out-rank a more specific,
    # longer keyword like "cloth" or "tailor" whenever both match once - e.g.
    # "clothes shop" used to tie Retail("shop") vs Textiles("cloth") at 1
    # match each, and Retail won on dict-insertion order alone. Weighting by
    # matched keyword length fixes that: "cloth" (5 chars) outweighs "shop"
    # (4 chars), so the more specific category wins.
    scores: List[Tuple[BusinessCategory, int, int, List[str]]] = []
    for category, keywords in CATEGORY_KEYWORDS.items():
        matched = [kw for kw in keywords if re.search(re.escape(kw.lower()), text)]
        if matched:
            specificity = sum(len(kw) for kw in matched)
            scores.append((category, specificity, len(matched), matched))

    if not scores:
        margin = available_margin_capital or CATEGORY_STARTING_MARGIN[BusinessCategory.other]
        explanation = i18n.idea_suggestion_no_match(lang) or (
            "We couldn't confidently match your idea to one of our standard categories from "
            "the words used - we've set it as 'Other' so you can describe it yourself. Feel "
            "free to pick the closest category from the list instead if one fits better."
        )
        return IdeaSuggestionResponse(
            detected_business_category=BusinessCategory.other,
            detected_business_category_other=description[:80],
            matched_keywords=[],
            suggested_starting_margin_capital=margin,
            confidence=ConfidenceLevel.low,
            explanation=explanation,
            likely_scheme_hint=_likely_scheme_hint(margin, lang),
        )

    scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
    best_category, _specificity, match_count, matched_keywords = scores[0]
    margin = available_margin_capital or CATEGORY_STARTING_MARGIN[best_category]
    confidence = ConfidenceLevel.high if match_count >= 2 else ConfidenceLevel.medium

    category_display = i18n.category_label(lang, best_category.value)
    localized_explanation = i18n.idea_suggestion_matched(lang, matched_keywords, category_display, margin)
    explanation = localized_explanation or (
        f"Based on the words '{', '.join(matched_keywords)}' in your description, this looks "
        f"like a {best_category.value} business. If you already have some savings to put in, "
        f"enter that instead - otherwise Rs. {margin:,.0f} is a realistic amount to start "
        f"exploring with for a {best_category.value.lower()} business of this scale."
    )
    return IdeaSuggestionResponse(
        detected_business_category=best_category,
        detected_business_category_other=None,
        matched_keywords=matched_keywords,
        suggested_starting_margin_capital=margin,
        confidence=confidence,
        explanation=explanation,
        likely_scheme_hint=_likely_scheme_hint(margin, lang),
    )

