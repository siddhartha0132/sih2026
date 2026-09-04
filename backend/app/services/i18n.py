"""
Language support for the AI's narrative text.

The report's narrative (narrative_summary, next steps, scheme explanation,
opportunity analysis, SWOT, threats, pricing rationale, revenue-projection
text, flowchart, disclaimer) is generated from Python string templates, not
an LLM call - so rather than bolt on an external translation API (none is
configured in this project, and a live translation call would be one more
thing that can silently fail during a demo), each supported language gets
its own parallel template. English, Hindi, Kannada and Telugu are fully
supported; any other `language` code currently falls back to English with
no error, so the UI/API never breaks for an unsupported code.

Hindi/Kannada/Telugu text below intentionally keeps a handful of universally
understood English/financial terms (like "UPI", scheme names such as
"SUVIDHA"/"PMEGP", "GST") exactly the way real rural government and bank
communication does in these languages - a fully "purist" translation of
such terms would actually be less understandable to the target audience,
not more. Everything else - every sentence structure, connective, and
descriptive phrase - is written in the target language.

Free-text the applicant typed themselves (business_idea_description,
business_category_other) is never machine-translated here - there is no
translation API in this project, so a Hindi/Kannada/Telugu speaker who
types their idea in English will see that phrase verbatim inside an
otherwise localized sentence. That is a known, disclosed limitation, not a
bug: translating a user's own free-text words would require an external
NLP service this offline-friendly tool intentionally does not depend on.
"""
import re
from typing import Dict, List, Optional

SUPPORTED_LANGUAGES = ["en", "hi", "kn", "te"]

LANGUAGE_NAMES = {"en": "English", "hi": "हिंदी", "kn": "ಕನ್ನಡ", "te": "తెలుగు"}


def normalize_language(language: str) -> str:
    lang = (language or "en").strip().lower()
    return lang if lang in SUPPORTED_LANGUAGES else "en"


# ── Category display names ────────────────────────────────────────────────
# Only used for KNOWN category enum values / the generic "small" fallback -
# never for free-text the applicant typed (see module docstring).
CATEGORY_NAMES: Dict[str, Dict[str, str]] = {
    "en": {
        "Dairy": "Dairy", "Retail": "Retail", "Textiles": "Textiles",
        "Food Processing": "Food Processing", "Poultry": "Poultry",
        "Handicrafts": "Handicrafts", "Agri Input Store": "Agri Input Store",
        "Tailoring": "Tailoring", "Other": "Other", "small": "small",
    },
    "hi": {
        "Dairy": "डेयरी", "Retail": "रिटेल/किराना", "Textiles": "वस्त्र",
        "Food Processing": "खाद्य प्रसंस्करण", "Poultry": "पोल्ट्री",
        "Handicrafts": "हस्तशिल्प", "Agri Input Store": "कृषि इनपुट स्टोर",
        "Tailoring": "सिलाई", "Other": "अन्य", "small": "छोटा",
    },
    "kn": {
        "Dairy": "ಡೈರಿ", "Retail": "ಚಿಲ್ಲರೆ ವ್ಯಾಪಾರ", "Textiles": "ಜವಳಿ",
        "Food Processing": "ಆಹಾರ ಸಂಸ್ಕರಣೆ", "Poultry": "ಕೋಳಿ ಸಾಕಣೆ",
        "Handicrafts": "ಕರಕುಶಲ ವಸ್ತುಗಳು", "Agri Input Store": "ಕೃಷಿ ಪರಿಕರ ಅಂಗಡಿ",
        "Tailoring": "ಟೈಲರಿಂಗ್", "Other": "ಇತರೆ", "small": "ಚಿಕ್ಕ",
    },
    "te": {
        "Dairy": "పాడి పరిశ్రమ", "Retail": "రిటైల్", "Textiles": "వస్త్రాలు",
        "Food Processing": "ఆహార ప్రాసెసింగ్", "Poultry": "కోళ్ల పెంపకం",
        "Handicrafts": "చేతివృత్తులు", "Agri Input Store": "వ్యవసాయ ఇన్‌పుట్ దుకాణం",
        "Tailoring": "టైలరింగ్", "Other": "ఇతర", "small": "చిన్న",
    },
}


DENSITY_LABELS: Dict[str, Dict[str, str]] = {
    "en": {"low": "low", "moderate": "moderate", "high": "high"},
    "hi": {"low": "कम", "moderate": "मध्यम", "high": "उच्च"},
    "kn": {"low": "ಕಡಿಮೆ", "moderate": "ಮಧ್ಯಮ", "high": "ಹೆಚ್ಚಿನ"},
    "te": {"low": "తక్కువ", "moderate": "మధ్యస్థ", "high": "అధిక"},
}


def density_label(lang: str, density_lower: str) -> str:
    return DENSITY_LABELS.get(lang, DENSITY_LABELS["en"]).get(density_lower, density_lower)


def category_label(lang: str, category_value: str) -> str:
    """Translate a KNOWN category enum value (or 'small'). Unknown/free-text
    strings are returned unchanged, since they are the applicant's own words."""
    return CATEGORY_NAMES.get(lang, {}).get(category_value, category_value)


# ── Units (pricing) ────────────────────────────────────────────────────────
CATEGORY_UNITS: Dict[str, Dict[str, str]] = {
    "en": {
        "Dairy": "per litre", "Retail": "per unit", "Textiles": "per metre",
        "Food Processing": "per kg", "Poultry": "per kg (live weight)",
        "Handicrafts": "per piece", "Agri Input Store": "per unit",
        "Tailoring": "per garment", "Other": "per unit",
    },
    "hi": {
        "Dairy": "प्रति लीटर", "Retail": "प्रति यूनिट", "Textiles": "प्रति मीटर",
        "Food Processing": "प्रति किग्रा", "Poultry": "प्रति किग्रा (जीवित वजन)",
        "Handicrafts": "प्रति नग", "Agri Input Store": "प्रति यूनिट",
        "Tailoring": "प्रति परिधान", "Other": "प्रति यूनिट",
    },
    "kn": {
        "Dairy": "ಪ್ರತಿ ಲೀಟರ್", "Retail": "ಪ್ರತಿ ಯುನಿಟ್", "Textiles": "ಪ್ರತಿ ಮೀಟರ್",
        "Food Processing": "ಪ್ರತಿ ಕೆಜಿ", "Poultry": "ಪ್ರತಿ ಕೆಜಿ (ಜೀವಂತ ತೂಕ)",
        "Handicrafts": "ಪ್ರತಿ ತುಂಡು", "Agri Input Store": "ಪ್ರತಿ ಯುನಿಟ್",
        "Tailoring": "ಪ್ರತಿ ಉಡುಪು", "Other": "ಪ್ರತಿ ಯುನಿಟ್",
    },
    "te": {
        "Dairy": "లీటరుకు", "Retail": "యూనిట్‌కు", "Textiles": "మీటరుకు",
        "Food Processing": "కిలోకు", "Poultry": "కిలోకు (సజీవ బరువు)",
        "Handicrafts": "ముక్కకు", "Agri Input Store": "యూనిట్‌కు",
        "Tailoring": "దుస్తుకు", "Other": "యూనిట్‌కు",
    },
}


def category_unit(lang: str, category_value: str) -> str:
    return CATEGORY_UNITS.get(lang, {}).get(category_value, CATEGORY_UNITS["en"].get(category_value, "per unit"))


# ── Distribution channels (Market Reach) ──────────────────────────────────
DISTRIBUTION_CHANNELS: Dict[str, Dict[str, List[str]]] = {
    "en": {
        "Dairy": ["District dairy cooperative / milk union", "Direct door-to-door delivery", "Local haat & weekly market"],
        "Retail": ["Village kirana storefront", "Weekly haat / mandal", "Local kirana wholesale network"],
        "Textiles": ["Block-level cloth market", "Weekly haat stall", "Festival-season bulk orders"],
        "Food Processing": ["Local kirana stores", "Weekly haat", "Nearby town wholesale mandis"],
        "Poultry": ["Direct farm-gate sale", "Local meat/poultry market", "Nearby town chicken traders"],
        "Handicrafts": ["Haat / mela (seasonal fairs)", "SHG marketing networks", "District / state emporium"],
        "Agri Input Store": ["Farmer-direct storefront", "Village-level demonstration & promotion", "Seasonal kharif/rabi drives"],
        "Tailoring": ["Walk-in orders (local)", "School uniform contracts", "Festival & wedding-season bulk"],
        "Other": ["Local haat/market", "Direct sale"],
    },
    "hi": {
        "Dairy": ["जिला डेयरी सहकारी समिति / मिल्क यूनियन", "प्रत्यक्ष घर-घर डिलीवरी", "स्थानीय हाट व साप्ताहिक बाज़ार"],
        "Retail": ["गांव की किराना दुकान", "साप्ताहिक हाट / मंडल", "स्थानीय किराना थोक नेटवर्क"],
        "Textiles": ["ब्लॉक स्तर का कपड़ा बाज़ार", "साप्ताहिक हाट स्टॉल", "त्योहारी सीज़न के थोक ऑर्डर"],
        "Food Processing": ["स्थानीय किराना दुकानें", "साप्ताहिक हाट", "नज़दीकी कस्बे की थोक मंडियां"],
        "Poultry": ["सीधे फार्म-गेट बिक्री", "स्थानीय मांस/पोल्ट्री बाज़ार", "नज़दीकी कस्बे के चिकन व्यापारी"],
        "Handicrafts": ["हाट / मेला (मौसमी मेले)", "SHG विपणन नेटवर्क", "जिला / राज्य एम्पोरियम"],
        "Agri Input Store": ["किसानों को सीधे बिक्री दुकान", "गांव स्तर पर प्रदर्शन व प्रचार", "मौसमी खरीफ/रबी अभियान"],
        "Tailoring": ["सीधे आने वाले ग्राहकों के ऑर्डर (स्थानीय)", "स्कूल यूनिफॉर्म अनुबंध", "त्योहार व शादी सीज़न के थोक ऑर्डर"],
        "Other": ["स्थानीय हाट/बाज़ार", "प्रत्यक्ष बिक्री"],
    },
    "kn": {
        "Dairy": ["ಜಿಲ್ಲಾ ಡೈರಿ ಸಹಕಾರ ಸಂಘ / ಮಿಲ್ಕ್ ಯೂನಿಯನ್", "ನೇರ ಮನೆ-ಮನೆ ವಿತರಣೆ", "ಸ್ಥಳೀಯ ಸಂತೆ ಮತ್ತು ವಾರದ ಮಾರುಕಟ್ಟೆ"],
        "Retail": ["ಗ್ರಾಮದ ಕಿರಾಣಿ ಅಂಗಡಿ", "ವಾರದ ಸಂತೆ / ಮಂಡಲ", "ಸ್ಥಳೀಯ ಕಿರಾಣಿ ಸಗಟು ಜಾಲ"],
        "Textiles": ["ಬ್ಲಾಕ್ ಮಟ್ಟದ ಬಟ್ಟೆ ಮಾರುಕಟ್ಟೆ", "ವಾರದ ಸಂತೆ ಮಳಿಗೆ", "ಹಬ್ಬದ ಸೀಸನ್ ಸಗಟು ಆರ್ಡರ್‌ಗಳು"],
        "Food Processing": ["ಸ್ಥಳೀಯ ಕಿರಾಣಿ ಅಂಗಡಿಗಳು", "ವಾರದ ಸಂತೆ", "ಹತ್ತಿರದ ಪಟ್ಟಣದ ಸಗಟು ಮಂಡಿಗಳು"],
        "Poultry": ["ನೇರ ಫಾರ್ಮ್-ಗೇಟ್ ಮಾರಾಟ", "ಸ್ಥಳೀಯ ಮಾಂಸ/ಕೋಳಿ ಮಾರುಕಟ್ಟೆ", "ಹತ್ತಿರದ ಪಟ್ಟಣದ ಕೋಳಿ ವ್ಯಾಪಾರಿಗಳು"],
        "Handicrafts": ["ಸಂತೆ / ಜಾತ್ರೆ (ಋತುಮಾನದ ಮೇಳಗಳು)", "SHG ಮಾರುಕಟ್ಟೆ ಜಾಲಗಳು", "ಜಿಲ್ಲಾ / ರಾಜ್ಯ ಎಂಪೋರಿಯಂ"],
        "Agri Input Store": ["ರೈತರಿಗೆ ನೇರ ಮಾರಾಟ ಮಳಿಗೆ", "ಗ್ರಾಮ ಮಟ್ಟದ ಪ್ರದರ್ಶನ ಮತ್ತು ಪ್ರಚಾರ", "ಋತುಮಾನದ ಖಾರಿಫ್/ರಬಿ ಅಭಿಯಾನಗಳು"],
        "Tailoring": ["ನೇರ ಗ್ರಾಹಕರ ಆರ್ಡರ್‌ಗಳು (ಸ್ಥಳೀಯ)", "ಶಾಲಾ ಸಮವಸ್ತ್ರ ಒಪ್ಪಂದಗಳು", "ಹಬ್ಬ ಮತ್ತು ಮದುವೆ ಸೀಸನ್ ಸಗಟು"],
        "Other": ["ಸ್ಥಳೀಯ ಸಂತೆ/ಮಾರುಕಟ್ಟೆ", "ನೇರ ಮಾರಾಟ"],
    },
    "te": {
        "Dairy": ["జిల్లా పాడి సహకార సంఘం / మిల్క్ యూనియన్", "నేరుగా ఇంటింటికి డెలివరీ", "స్థానిక సంత & వారపు మార్కెట్"],
        "Retail": ["గ్రామంలోని కిరాణా దుకాణం", "వారపు సంత / మండలం", "స్థానిక కిరాణా టోకు నెట్‌వర్క్"],
        "Textiles": ["బ్లాక్ స్థాయి వస్త్ర మార్కెట్", "వారపు సంత స్టాల్", "పండుగ సీజన్ టోకు ఆర్డర్లు"],
        "Food Processing": ["స్థానిక కిరాణా దుకాణాలు", "వారపు సంత", "సమీప పట్టణ టోకు మండీలు"],
        "Poultry": ["నేరుగా ఫారం-గేట్ అమ్మకం", "స్థానిక మాంసం/కోళ్ల మార్కెట్", "సమీప పట్టణ కోడి వ్యాపారులు"],
        "Handicrafts": ["సంత / జాతర (సీజనల్ ఫెయిర్‌లు)", "SHG మార్కెటింగ్ నెట్‌వర్క్‌లు", "జిల్లా / రాష్ట్ర ఎంపోరియం"],
        "Agri Input Store": ["రైతులకు నేరుగా విక్రయ దుకాణం", "గ్రామ స్థాయి ప్రదర్శన & ప్రచారం", "సీజనల్ ఖరీఫ్/రబీ డ్రైవ్‌లు"],
        "Tailoring": ["నేరుగా వచ్చే ఆర్డర్లు (స్థానిక)", "పాఠశాల యూనిఫాం ఒప్పందాలు", "పండుగ & పెళ్లిళ్ల సీజన్ టోకు ఆర్డర్లు"],
        "Other": ["స్థానిక సంత/మార్కెట్", "ప్రత్యక్ష అమ్మకం"],
    },
}


def distribution_channels(lang: str, category_value: str) -> List[str]:
    table = DISTRIBUTION_CHANNELS.get(lang, DISTRIBUTION_CHANNELS["en"])
    return table.get(category_value, DISTRIBUTION_CHANNELS["en"].get(category_value, ["Local haat/market", "Direct sale"]))


DISCLAIMER = {
    "en": (
        "This report is an AI-generated advisory tool to aid decision-making. "
        "It does not constitute an official loan sanction or government approval. "
        "Final eligibility is determined by the concerned Channelizing Agency (CA/SCA)."
    ),
    "hi": (
        "यह रिपोर्ट निर्णय लेने में मदद के लिए एक AI-आधारित सलाहकार उपकरण है। "
        "यह किसी आधिकारिक लोन स्वीकृति या सरकारी अनुमोदन के बराबर नहीं है। "
        "अंतिम पात्रता संबंधित चैनलाइज़िंग एजेंसी (CA/SCA) द्वारा तय की जाएगी।"
    ),
    "kn": (
        "ಈ ವರದಿಯು ನಿರ್ಧಾರ ತೆಗೆದುಕೊಳ್ಳಲು ಸಹಾಯ ಮಾಡುವ AI-ಆಧಾರಿತ ಸಲಹಾ ಸಾಧನವಾಗಿದೆ. "
        "ಇದು ಯಾವುದೇ ಅಧಿಕೃತ ಸಾಲ ಮಂಜೂರಾತಿ ಅಥವಾ ಸರ್ಕಾರಿ ಅನುಮೋದನೆಗೆ ಸಮನಾಗಿಲ್ಲ. "
        "ಅಂತಿಮ ಅರ್ಹತೆಯನ್ನು ಸಂಬಂಧಿತ ಚಾನೆಲೈಸಿಂಗ್ ಏಜೆನ್ಸಿ (CA/SCA) ನಿರ್ಧರಿಸುತ್ತದೆ."
    ),
    "te": (
        "ఈ నివేదిక నిర్ణయం తీసుకోవడంలో సహాయపడే AI-ఆధారిత సలహా సాధనం. "
        "ఇది అధికారిక రుణ మంజూరు లేదా ప్రభుత్వ ఆమోదానికి సమానం కాదు. "
        "తుది అర్హతను సంబంధిత చానెలైజింగ్ ఏజెన్సీ (CA/SCA) నిర్ణయిస్తుంది."
    ),
}


def scheme_explanation(
    lang: str, project_cost: float, band_desc_en: str, band_desc_hi: str,
    scheme_value: str, rate: float, tenure_years: int, moratorium_months: int,
    verified_on: str, band_desc_kn: str = None, band_desc_te: str = None,
) -> str:
    if lang == "hi":
        return (
            f"आपकी परियोजना लागत Rs. {project_cost:,.0f} है, जो {band_desc_hi} में आती है, "
            f"इसलिए आप {scheme_value} के लिए पात्र हैं - ब्याज दर {rate}% प्रति वर्ष, "
            f"चुकौती अवधि {tenure_years} वर्ष (जिसमें {moratorium_months} महीने की मोहलत/मोरेटोरियम शामिल है)। "
            f"ये शर्तें NSFDC की आधिकारिक वेबसाइट से {verified_on} को सत्यापित की गई हैं - "
            f"स्रोत लिंक इसी योजना के साथ दिया गया है।"
        )
    if lang == "kn":
        return (
            f"ನಿಮ್ಮ ಯೋಜನಾ ವೆಚ್ಚ Rs. {project_cost:,.0f} ಆಗಿದ್ದು, ಇದು {band_desc_kn or band_desc_en} ವ್ಯಾಪ್ತಿಯಲ್ಲಿ ಬರುತ್ತದೆ, "
            f"ಆದ್ದರಿಂದ ನೀವು {scheme_value} ಗೆ ಅರ್ಹರಾಗಿದ್ದೀರಿ - ಬಡ್ಡಿ ದರ ವಾರ್ಷಿಕ {rate}%, "
            f"ಮರುಪಾವತಿ ಅವಧಿ {tenure_years} ವರ್ಷಗಳು ({moratorium_months} ತಿಂಗಳ ಮೊರಟೋರಿಯಂ ಸೇರಿ). "
            f"ಈ ನಿಯಮಗಳನ್ನು NSFDC ಯ ಅಧಿಕೃತ ವೆಬ್‌ಸೈಟ್‌ನಿಂದ {verified_on} ರಂದು ಪರಿಶೀಲಿಸಲಾಗಿದೆ - "
            f"ಮೂಲ ಲಿಂಕ್ ಈ ಯೋಜನೆಯೊಂದಿಗೆ ನೀಡಲಾಗಿದೆ."
        )
    if lang == "te":
        return (
            f"మీ ప్రాజెక్ట్ వ్యయం Rs. {project_cost:,.0f}, ఇది {band_desc_te or band_desc_en} పరిధిలోకి వస్తుంది, "
            f"కాబట్టి మీరు {scheme_value} కు అర్హులు - వడ్డీ రేటు వార్షికంగా {rate}%, "
            f"తిరిగి చెల్లింపు వ్యవధి {tenure_years} సంవత్సరాలు ({moratorium_months} నెలల మారటోరియంతో సహా). "
            f"ఈ నిబంధనలు NSFDC అధికారిక వెబ్‌సైట్ నుండి {verified_on} నాడు ధృవీకరించబడ్డాయి - "
            f"మూల లింక్ ఈ పథకంతో పాటు ఇవ్వబడింది."
        )
    return (
        f"Your project cost of Rs. {project_cost:,.0f} falls {band_desc_en}, "
        f"so you qualify for the {scheme_value} at {rate}% p.a. interest, repayable over "
        f"{tenure_years} years including a {moratorium_months}-month moratorium. "
        f"Terms verified directly against NSFDC's official scheme page on {verified_on} "
        f"- see the source link with this plan."
    )


def not_eligible_explanation(lang: str) -> str:
    if lang == "hi":
        return (
            "गणना की गई परियोजना लागत Rs. 50,00,000 की सीमा से अधिक होने के कारण कोई भी NSFDC "
            "योजना स्वतः नहीं चुनी जा सकी। नीचे दी गई 'अन्य योजनाएं' सूची देखें - इतनी बड़ी "
            "परियोजना के लिए PMEGP, MUDRA या स्टैंड-अप इंडिया अभी भी उपयुक्त हो सकती हैं।"
        )
    if lang == "kn":
        return (
            "ಲೆಕ್ಕಹಾಕಿದ ಯೋಜನಾ ವೆಚ್ಚವು Rs. 50,00,000 ಮಿತಿಯನ್ನು ಮೀರಿರುವುದರಿಂದ ಯಾವುದೇ NSFDC "
            "ಯೋಜನೆಯನ್ನು ಸ್ವಯಂಚಾಲಿತವಾಗಿ ಆಯ್ಕೆ ಮಾಡಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ಕೆಳಗಿನ 'ಇತರ ಯೋಜನೆಗಳ' ಪಟ್ಟಿಯನ್ನು "
            "ನೋಡಿ - ಇಷ್ಟು ದೊಡ್ಡ ಯೋಜನೆಗೆ PMEGP, MUDRA ಅಥವಾ ಸ್ಟ್ಯಾಂಡ್-ಅಪ್ ಇಂಡಿಯಾ ಇನ್ನೂ ಸೂಕ್ತವಾಗಬಹುದು."
        )
    if lang == "te":
        return (
            "లెక్కించిన ప్రాజెక్ట్ వ్యయం Rs. 50,00,000 పరిమితిని మించినందున ఏ NSFDC "
            "పథకాన్ని స్వయంచాలకంగా ఎంచుకోలేకపోయాము. దిగువన ఉన్న 'ఇతర పథకాలు' జాబితాను చూడండి - "
            "ఇంత పెద్ద ప్రాజెక్టుకు PMEGP, MUDRA లేదా స్టాండ్-అప్ ఇండియా ఇంకా సరిపోవచ్చు."
        )
    return (
        "No NSFDC scheme could be auto-selected because the calculated project "
        "cost exceeds the Rs. 50,00,000 ceiling covered by Micro Finance, "
        "SUVIDHA, and UTKARSH. Check the 'other schemes' list below - PMEGP, "
        "MUDRA or Stand-Up India may still cover a project of this size."
    )


def narrative_summary(
    lang: str, category: str, village: str, district: str, score: int,
    competitors_nearby: int, density: str, lit_pct: float, mobile_pct: float,
    price_min: float, price_max: float, unit: str,
) -> Optional[str]:
    if lang == "hi":
        verdict = (
            "एक मजबूत अवसर" if score >= 65 else
            "स्पष्ट रणनीति के साथ एक व्यवहार्य अवसर" if score >= 45 else
            "उच्च-जोखिम वाला प्रवेश - स्थान या श्रेणी में बदलाव पर विचार करें"
        )
        return (
            f"{village}, {district} में एक {category} व्यवसाय को GramVyapaar अवसर सूचकांक पर "
            f"{score}/100 अंक मिले हैं - यह {verdict} है। "
            f"इस क्षेत्र में 7.5 किमी के दायरे में {competitors_nearby:,} समान प्रतिस्पर्धी व्यवसाय हैं, "
            f"जिनका घनत्व '{density_label(lang, density)}' है। "
            f"जिले की साक्षरता दर ({lit_pct}%) और मोबाइल पहुंच ({mobile_pct}%) दिखाती हैं कि यह बाजार "
            f"धीरे-धीरे औपचारिक लेन-देन की ओर बढ़ रहा है। "
            f"सुझाई गई बिक्री कीमत: Rs. {price_min}-{price_max} {unit} (स्रोत: Agmarknet वास्तविक डेटा)।"
        )
    if lang == "kn":
        verdict = (
            "ಒಂದು ಪ್ರಬಲ ಅವಕಾಶ" if score >= 65 else
            "ಸ್ಪಷ್ಟ ತಂತ್ರದೊಂದಿಗೆ ಸಾಧ್ಯವಾಗುವ ಅವಕಾಶ" if score >= 45 else
            "ಹೆಚ್ಚು-ಅಪಾಯದ ಪ್ರವೇಶ - ಸ್ಥಳ ಅಥವಾ ವರ್ಗವನ್ನು ಬದಲಾಯಿಸುವುದನ್ನು ಪರಿಗಣಿಸಿ"
        )
        return (
            f"{village}, {district} ನಲ್ಲಿ ಒಂದು {category} ವ್ಯಾಪಾರವು GramVyapaar ಅವಕಾಶ ಸೂಚ್ಯಂಕದಲ್ಲಿ "
            f"{score}/100 ಅಂಕಗಳನ್ನು ಗಳಿಸಿದೆ - ಇದು {verdict} ಆಗಿದೆ. "
            f"ಈ ಪ್ರದೇಶದಲ್ಲಿ 7.5 ಕಿ.ಮೀ ವ್ಯಾಪ್ತಿಯಲ್ಲಿ {competitors_nearby:,} ಇದೇ ರೀತಿಯ ಸ್ಪರ್ಧಾತ್ಮಕ "
            f"ವ್ಯಾಪಾರಗಳಿವೆ, ಅವುಗಳ ಸಾಂದ್ರತೆ '{density_label(lang, density)}' ಆಗಿದೆ. "
            f"ಜಿಲ್ಲೆಯ ಸಾಕ್ಷರತಾ ಪ್ರಮಾಣ ({lit_pct}%) ಮತ್ತು ಮೊಬೈಲ್ ವ್ಯಾಪ್ತಿ ({mobile_pct}%) ಈ ಮಾರುಕಟ್ಟೆ "
            f"ಕ್ರಮೇಣ ಔಪಚಾರಿಕ ವಹಿವಾಟಿನತ್ತ ಸಾಗುತ್ತಿದೆ ಎಂದು ತೋರಿಸುತ್ತದೆ. "
            f"ಶಿಫಾರಸು ಮಾಡಿದ ಮಾರಾಟ ಬೆಲೆ: Rs. {price_min}-{price_max} {unit} (ಮೂಲ: Agmarknet ನಿಜವಾದ ಡೇಟಾ)."
        )
    if lang == "te":
        verdict = (
            "ఒక బలమైన అవకాశం" if score >= 65 else
            "స్పష్టమైన వ్యూహంతో సాధ్యమయ్యే అవకాశం" if score >= 45 else
            "అధిక-రిస్క్ ప్రవేశం - స్థానం లేదా వర్గాన్ని మార్చుకోవడం పరిగణించండి"
        )
        return (
            f"{village}, {district} లో ఒక {category} వ్యాపారం GramVyapaar అవకాశ సూచీలో "
            f"{score}/100 స్కోరు సాధించింది - ఇది {verdict}. "
            f"ఈ ప్రాంతంలో 7.5 కి.మీ పరిధిలో {competitors_nearby:,} ఇలాంటి పోటీ వ్యాపారాలు ఉన్నాయి, "
            f"వాటి సాంద్రత '{density_label(lang, density)}'గా ఉంది. "
            f"జిల్లా అక్షరాస్యత రేటు ({lit_pct}%) మరియు మొబైల్ వ్యాప్తి ({mobile_pct}%) ఈ మార్కెట్ "
            f"క్రమంగా అధికారిక లావాదేవీల వైపు మళ్లుతోందని చూపిస్తున్నాయి. "
            f"సూచించిన అమ్మకపు ధర: Rs. {price_min}-{price_max} {unit} (మూలం: Agmarknet నిజమైన డేటా)."
        )
    return None  # caller keeps its existing detailed English builder


NEXT_STEPS_HEADER = {
    "en": "Actionable next steps",
    "hi": "अगले जरूरी कदम",
    "kn": "ಮುಂದಿನ ಅಗತ್ಯ ಹೆಜ್ಜೆಗಳು",
    "te": "తదుపరి అవసరమైన చర్యలు",
}


def actionable_next_steps(lang: str, district: str, matched_scheme_name: str, project_cost: float,
                           category: str, price_min: float, price_max: float, unit: str) -> List[str]:
    if lang == "hi":
        return [
            f"{district} में अपने नज़दीकी कॉमन सर्विस सेंटर (CSC) या RSETI कार्यालय में यह रिपोर्ट लेकर जाएं।",
            "तैयार रखें: आधार कार्ड, पैन कार्ड, पता प्रमाण, और मार्जिन मनी का बैंक स्टेटमेंट।",
            f"{matched_scheme_name} के तहत आवेदन करें - परियोजना लागत Rs. {project_cost:,.0f}। "
            f"सटीक शर्तों और आधिकारिक स्रोत लिंक के लिए ऊपर वित्तीय योजना अनुभाग देखें।",
            f"अपनी कीमत की धारणा (Rs. {price_min}-{price_max} {unit}) की पुष्टि के लिए 3-5 स्थानीय "
            f"{category} व्यवसायों से बात करें।",
            "एक बार व्यवसाय शुरू होने पर उद्यम पोर्टल (udyamregistration.gov.in) पर पंजीकरण करें - "
            "इससे प्राथमिकता ऋण और सरकारी योजना लाभ मिलते हैं।",
        ]
    if lang == "kn":
        return [
            f"{district} ನಲ್ಲಿರುವ ನಿಮ್ಮ ಹತ್ತಿರದ ಕಾಮನ್ ಸರ್ವಿಸ್ ಸೆಂಟರ್ (CSC) ಅಥವಾ RSETI ಕಚೇರಿಗೆ ಈ ವರದಿಯೊಂದಿಗೆ ಭೇಟಿ ನೀಡಿ.",
            "ಸಿದ್ಧವಿಟ್ಟುಕೊಳ್ಳಿ: ಆಧಾರ್ ಕಾರ್ಡ್, ಪ್ಯಾನ್ ಕಾರ್ಡ್, ವಿಳಾಸ ಪುರಾವೆ, ಮತ್ತು ಮಾರ್ಜಿನ್ ಹಣದ ಬ್ಯಾಂಕ್ ಸ್ಟೇಟ್‌ಮೆಂಟ್.",
            f"{matched_scheme_name} ಅಡಿಯಲ್ಲಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ - ಯೋಜನಾ ವೆಚ್ಚ Rs. {project_cost:,.0f}. "
            f"ನಿಖರ ನಿಯಮಗಳು ಮತ್ತು ಅಧಿಕೃತ ಮೂಲ ಲಿಂಕ್‌ಗಾಗಿ ಮೇಲಿನ ಆರ್ಥಿಕ ಯೋಜನೆ ವಿಭಾಗವನ್ನು ನೋಡಿ.",
            f"ನಿಮ್ಮ ಬೆಲೆಯ ಊಹೆಯನ್ನು (Rs. {price_min}-{price_max} {unit}) ದೃಢಪಡಿಸಲು 3-5 ಸ್ಥಳೀಯ "
            f"{category} ವ್ಯಾಪಾರಿಗಳೊಂದಿಗೆ ಮಾತನಾಡಿ.",
            "ವ್ಯಾಪಾರ ಆರಂಭವಾದ ನಂತರ ಉದ್ಯಮ್ ಪೋರ್ಟಲ್‌ನಲ್ಲಿ (udyamregistration.gov.in) ನೋಂದಾಯಿಸಿ - "
            "ಇದು ಆದ್ಯತೆಯ ಸಾಲ ಮತ್ತು ಸರ್ಕಾರಿ ಯೋಜನೆಯ ಪ್ರಯೋಜನಗಳನ್ನು ನೀಡುತ್ತದೆ.",
        ]
    if lang == "te":
        return [
            f"{district} లో మీ సమీప కామన్ సర్వీస్ సెంటర్ (CSC) లేదా RSETI కార్యాలయానికి ఈ నివేదికతో వెళ్లండి.",
            "సిద్ధంగా ఉంచుకోండి: ఆధార్ కార్డు, పాన్ కార్డు, చిరునామా రుజువు, మరియు మార్జిన్ మనీ బ్యాంక్ స్టేట్‌మెంట్.",
            f"{matched_scheme_name} కింద దరఖాస్తు చేయండి - ప్రాజెక్ట్ వ్యయం Rs. {project_cost:,.0f}. "
            f"ఖచ్చితమైన నిబంధనలు మరియు అధికారిక మూలం లింక్ కోసం పైన ఉన్న ఆర్థిక ప్రణాళిక విభాగం చూడండి.",
            f"మీ ధర అంచనాను (Rs. {price_min}-{price_max} {unit}) ధృవీకరించుకోవడానికి 3-5 స్థానిక "
            f"{category} వ్యాపారులతో మాట్లాడండి.",
            "వ్యాపారం మొదలైన తర్వాత ఉద్యమ్ పోర్టల్‌లో (udyamregistration.gov.in) నమోదు చేసుకోండి - "
            "ఇది ప్రాధాన్యత రుణం మరియు ప్రభుత్వ పథక ప్రయోజనాలను అందిస్తుంది.",
        ]
    return [
        f"Visit the nearest Common Service Centre (CSC) or RSETI office in {district} with this report.",
        "Prepare: Aadhaar, PAN, address proof, and margin-money bank statement.",
        f"Apply under the {matched_scheme_name} - project cost Rs. {project_cost:,.0f}. "
        f"See the Financial Plan section above for the exact terms and official source link.",
        f"Talk to 3-5 local {category.lower()} businesses to validate the Rs. "
        f"{price_min}-{price_max} {unit} price assumption before finalising your business plan.",
        "Register on the Udyam Portal (udyamregistration.gov.in) once operational - "
        "it unlocks priority lending and government scheme benefits.",
    ]


def flowchart_steps(lang: str, business_stage: str) -> List[Dict]:
    """
    A simple linear journey flowchart - deliberately a flowchart, not a data
    chart with axes, since it is far easier for a first-time, low-financial-
    literacy audience to follow a sequence of boxes than to read a graph.
    """
    if lang == "hi":
        if business_stage == "ongoing":
            steps = [
                ("अभी की स्थिति", "अपने मौजूदा व्यवसाय की वर्तमान आमदनी और ग्राहकों को समझें।"),
                ("योजना जांचें", "इस रिपोर्ट से देखें कि विस्तार के लिए कौन सी सरकारी योजना सही है।"),
                ("आवेदन करें", "जरूरी कागज़ात के साथ चुनी गई योजना के लिए आवेदन करें।"),
                ("लोन मिलना", "मंज़ूरी के बाद लोन राशि और मोहलत अवधि शुरू होती है।"),
                ("विस्तार करें", "नई पूंजी से उत्पादन/स्टॉक/ग्राहक आधार बढ़ाएं।"),
                ("चुकौती और वृद्धि", "समय पर किस्तें चुकाएं और आमदनी को दोबारा व्यवसाय में लगाएं।"),
            ]
        else:
            steps = [
                ("विचार", "अपना व्यवसाय विचार और उपलब्ध पूंजी तय करें।"),
                ("जांच करें", "इस रिपोर्ट से बाजार, प्रतिस्पर्धा और कीमत को समझें।"),
                ("योजना चुनें", "अपनी परियोजना लागत के अनुसार सही सरकारी योजना चुनें।"),
                ("आवेदन करें", "आधार, पैन और मार्जिन मनी के प्रमाण के साथ आवेदन करें।"),
                ("लोन मिलना", "स्वीकृति के बाद लोन राशि मिलती है, मोहलत अवधि शुरू होती है।"),
                ("शुरू करें और बढ़ें", "व्यवसाय शुरू करें, किस्तें चुकाएं, धीरे-धीरे बढ़ाएं।"),
            ]
    elif lang == "kn":
        if business_stage == "ongoing":
            steps = [
                ("ಈಗಿನ ಸ್ಥಿತಿ", "ನಿಮ್ಮ ಪ್ರಸ್ತುತ ವ್ಯಾಪಾರದ ನಿಜವಾದ ಆದಾಯ ಮತ್ತು ಗ್ರಾಹಕರನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ."),
                ("ಯೋಜನೆ ಪರಿಶೀಲಿಸಿ", "ವಿಸ್ತರಣೆಗೆ ಯಾವ ಸರ್ಕಾರಿ ಯೋಜನೆ ಸೂಕ್ತವೆಂದು ಈ ವರದಿಯಿಂದ ನೋಡಿ."),
                ("ಅರ್ಜಿ ಸಲ್ಲಿಸಿ", "ಅಗತ್ಯ ದಾಖಲೆಗಳೊಂದಿಗೆ ಆಯ್ಕೆಮಾಡಿದ ಯೋಜನೆಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ."),
                ("ಸಾಲ ಮಂಜೂರು", "ಅನುಮೋದನೆಯ ನಂತರ ಸಾಲದ ಮೊತ್ತ ಮತ್ತು ಮೊರಟೋರಿಯಂ ಅವಧಿ ಆರಂಭವಾಗುತ್ತದೆ."),
                ("ವಿಸ್ತರಿಸಿ", "ಹೊಸ ಬಂಡವಾಳದಿಂದ ಉತ್ಪಾದನೆ/ಸ್ಟಾಕ್/ಗ್ರಾಹಕರ ವ್ಯಾಪ್ತಿಯನ್ನು ಹೆಚ್ಚಿಸಿ."),
                ("ಮರುಪಾವತಿ ಮತ್ತು ಬೆಳವಣಿಗೆ", "ಸಮಯಕ್ಕೆ ಕಂತುಗಳನ್ನು ಪಾವತಿಸಿ ಮತ್ತು ಆದಾಯವನ್ನು ಮತ್ತೆ ವ್ಯಾಪಾರದಲ್ಲಿ ತೊಡಗಿಸಿ."),
            ]
        else:
            steps = [
                ("ಆಲೋಚನೆ", "ನಿಮ್ಮ ವ್ಯಾಪಾರ ಆಲೋಚನೆ ಮತ್ತು ಲಭ್ಯವಿರುವ ಬಂಡವಾಳವನ್ನು ನಿರ್ಧರಿಸಿ."),
                ("ಪರಿಶೀಲಿಸಿ", "ಮಾರುಕಟ್ಟೆ, ಸ್ಪರ್ಧೆ ಮತ್ತು ಬೆಲೆಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಈ ವರದಿಯನ್ನು ಬಳಸಿ."),
                ("ಯೋಜನೆ ಆಯ್ಕೆಮಾಡಿ", "ನಿಮ್ಮ ಯೋಜನಾ ವೆಚ್ಚಕ್ಕೆ ಸರಿಹೊಂದುವ ಸರ್ಕಾರಿ ಯೋಜನೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ."),
                ("ಅರ್ಜಿ ಸಲ್ಲಿಸಿ", "ಆಧಾರ್, ಪ್ಯಾನ್ ಮತ್ತು ಮಾರ್ಜಿನ್ ಹಣದ ಪುರಾವೆಯೊಂದಿಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ."),
                ("ಸಾಲ ಮಂಜೂರು", "ಅನುಮೋದನೆಯ ನಂತರ ಸಾಲದ ಮೊತ್ತ ಸಿಗುತ್ತದೆ, ಮೊರಟೋರಿಯಂ ಅವಧಿ ಆರಂಭವಾಗುತ್ತದೆ."),
                ("ಆರಂಭಿಸಿ ಮತ್ತು ಬೆಳೆಸಿ", "ವ್ಯಾಪಾರ ಆರಂಭಿಸಿ, ಕಂತುಗಳನ್ನು ಪಾವತಿಸಿ, ಕ್ರಮೇಣ ಬೆಳೆಸಿ."),
            ]
    elif lang == "te":
        if business_stage == "ongoing":
            steps = [
                ("ప్రస్తుత స్థితి", "మీ ప్రస్తుత వ్యాపారం యొక్క నిజమైన ఆదాయం మరియు కస్టమర్లను అర్థం చేసుకోండి."),
                ("ప్రణాళిక తనిఖీ చేయండి", "విస్తరణకు ఏ ప్రభుత్వ పథకం సరిపోతుందో ఈ నివేదిక నుండి చూడండి."),
                ("దరఖాస్తు చేయండి", "అవసరమైన పత్రాలతో ఎంపిక చేసిన పథకానికి దరఖాస్తు చేయండి."),
                ("రుణం మంజూరు", "ఆమోదం తర్వాత రుణ మొత్తం మరియు మారటోరియం వ్యవధి ప్రారంభమవుతుంది."),
                ("విస్తరించండి", "కొత్త మూలధనంతో ఉత్పత్తి/స్టాక్/కస్టమర్ పరిధిని పెంచుకోండి."),
                ("తిరిగి చెల్లింపు & వృద్ధి", "సకాలంలో వాయిదాలు చెల్లించండి మరియు ఆదాయాన్ని తిరిగి వ్యాపారంలో పెట్టుబడి పెట్టండి."),
            ]
        else:
            steps = [
                ("ఆలోచన", "మీ వ్యాపార ఆలోచన మరియు అందుబాటులో ఉన్న మూలధనాన్ని నిర్ణయించండి."),
                ("సాధ్యాసాధ్యాలు తనిఖీ చేయండి", "మార్కెట్, పోటీ మరియు ధరను అర్థం చేసుకోవడానికి ఈ నివేదికను ఉపయోగించండి."),
                ("పథకాన్ని ఎంచుకోండి", "మీ ప్రాజెక్ట్ వ్యయానికి సరిపోయే ప్రభుత్వ పథకాన్ని ఎంచుకోండి."),
                ("దరఖాస్తు చేయండి", "ఆధార్, పాన్ మరియు మార్జిన్ మనీ రుజువుతో దరఖాస్తు చేయండి."),
                ("రుణం మంజూరు", "ఆమోదం తర్వాత రుణ మొత్తం లభిస్తుంది, మారటోరియం వ్యవధి ప్రారంభమవుతుంది."),
                ("ప్రారంభించండి & వృద్ధి చెందండి", "వ్యాపారం ప్రారంభించండి, వాయిదాలు చెల్లించండి, క్రమంగా వృద్ధి చెందండి."),
            ]
    else:
        if business_stage == "ongoing":
            steps = [
                ("Where you are now", "Understand your current business's real income and customers."),
                ("Check the plan", "Use this report to see which government scheme fits growth."),
                ("Apply", "Apply for the matched scheme with the required documents."),
                ("Loan disbursed", "After approval, the loan amount and moratorium period begin."),
                ("Expand", "Use the new capital to grow stock, production, or customer reach."),
                ("Repay & grow", "Pay instalments on time and reinvest income back into the business."),
            ]
        else:
            steps = [
                ("Idea", "Decide your business idea and how much capital you can put in."),
                ("Check feasibility", "Use this report to understand the market, competition, and pricing."),
                ("Pick a scheme", "Match your project cost to the right government scheme."),
                ("Apply", "Apply with Aadhaar, PAN, and proof of your margin-money contribution."),
                ("Loan disbursed", "Once approved, you get the loan and moratorium period starts."),
                ("Start & grow", "Start the business, repay on schedule, and grow gradually."),
            ]
    return [
        {"step_number": i + 1, "title": t, "description": d}
        for i, (t, d) in enumerate(steps)
    ]


def business_stage_narrative_note(lang: str, stage: str) -> str:
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
    if lang == "kn":
        if stage == "ongoing":
            return (
                "ನೀವು ಈಗಾಗಲೇ ಈ ವ್ಯಾಪಾರವನ್ನು ನಡೆಸುತ್ತಿರುವುದರಿಂದ, ಈ ವರದಿಯು ನಿಮ್ಮ ಪ್ರಸ್ತುತ "
                "ಆದಾಯದ ಆಧಾರದ ಮೇಲೆ ವಿಸ್ತರಣೆಯ ಮೇಲೆ ಕೇಂದ್ರೀಕರಿಸಿದೆ, ಆರಂಭದ ಮೇಲಲ್ಲ."
            )
        if stage == "researching":
            return (
                "ನೀವು ಇನ್ನೂ ಮಾಹಿತಿ ಸಂಗ್ರಹಿಸುತ್ತಿರುವುದರಿಂದ, ಅಂತಿಮ ನಿರ್ಧಾರ ತೆಗೆದುಕೊಳ್ಳುವ ಮೊದಲು "
                "ಈ ವರದಿಯನ್ನು ಆರಂಭಿಕ ಮಾರ್ಗದರ್ಶಿಯಾಗಿ ಬಳಸಿ — ಬಂಡವಾಳ ಹೂಡುವ ಮೊದಲು ಸ್ಥಳೀಯ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ."
            )
        return (
            "ಇದು ಇನ್ನೂ ಕೇವಲ ಒಂದು ಆಲೋಚನೆಯಾಗಿರುವುದರಿಂದ, ಬಂಡವಾಳ ಹೂಡುವ ಮೊದಲು ಈ ವರದಿಯ ಪ್ರತಿ "
            "ಊಹೆಯನ್ನು ನಿಮ್ಮ ಗ್ರಾಮದಲ್ಲಿ 3-5 ಜನರೊಂದಿಗೆ ಮಾತನಾಡಿ ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ."
        )
    if lang == "te":
        if stage == "ongoing":
            return (
                "మీరు ఇప్పటికే ఈ వ్యాపారాన్ని నడుపుతున్నందున, ఈ నివేదిక మీ ప్రస్తుత "
                "ఆదాయాన్ని ఆధారంగా చేసుకుని విస్తరణపై దృష్టి పెడుతుంది, ప్రారంభంపై కాదు."
            )
        if stage == "researching":
            return (
                "మీరు ఇంకా సమాచారం సేకరిస్తున్నందున, తుది నిర్ణయం తీసుకునే ముందు "
                "ఈ నివేదికను ప్రారంభ మార్గదర్శిగా ఉపయోగించండి — మూలధనం పెట్టే ముందు స్థానిక మార్కెట్‌లో ధృవీకరించుకోండి."
            )
        return (
            "ఇది ఇంకా కేవలం ఒక ఆలోచన మాత్రమే కాబట్టి, మూలధనం పెట్టే ముందు ఈ నివేదికలోని ప్రతి "
            "అంచనాను మీ గ్రామంలో 3-5 మందితో మాట్లాడి తప్పకుండా ధృవీకరించుకోండి."
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


# ── Opportunity analysis (Market Reach → niches + rationale) ──────────────
def opportunity_analysis(
    lang: str, category: str, density: str, competitors_nearby: int,
    lit_pct: float, agri_pct: float, agri_cat: bool, density_percentile: Optional[float],
):
    """Returns (niches: List[str], rationale: str)."""
    if lang == "hi":
        if density == "Low":
            niches = [
                f"पहले प्रवेश का लाभ: इस क्षेत्र में {category} की सेवा अभी कम है — 7.5 किमी के दायरे में केवल "
                f"{competitors_nearby} समान व्यवसाय हैं।",
                f"{round(lit_pct,1)}% साक्षरता दर दिखाती है कि यहां औपचारिक लेन-देन संभव है — डिजिटल भुगतान "
                f"और रिकॉर्ड-कीपिंग अपनाना आसान होगा।",
            ]
            if agri_cat and agri_pct > 0.40:
                niches.append(
                    f"कृषि श्रमिक आधार ({round(agri_pct*100,1)}% श्रमिक) {category} उत्पादों की स्वाभाविक "
                    f"मांग बनाता है — आपूर्ति चक्र को फसल के मौसम के अनुसार रखें।"
                )
            rationale = "कम प्रतिस्पर्धा घनत्व एक मजबूत पहले-प्रवेश की खिड़की बनाता है। निर्णायक रूप से आगे बढ़ें।"
        elif density == "Moderate":
            niches = [
                f"गुणवत्ता, किस्तों में भुगतान की सुविधा, या किसी खास कम-सेवा वाले वर्ग को लक्षित करके "
                f"{category} में सीधे मुकाबले से बचें और अलग पहचान बनाएं।",
                "7.5 किमी के दायरे में उन गांव समूहों को लक्षित करें जहां मौजूदा प्रतिस्पर्धी अच्छी सेवा नहीं देते।",
            ]
            rationale = (
                f"मध्यम प्रतिस्पर्धा: स्पष्ट रणनीति के साथ व्यवहार्य है। आस-पास औसतन "
                f"{competitors_nearby} समान व्यवसाय हैं।"
            )
        else:
            niches = [
                f"इस स्थान पर सीधे {category} में प्रवेश जोखिम भरा है — पास के कम-घनत्व वाले ब्लॉक या किसी "
                f"विशेष प्रीमियम उप-वर्ग पर विचार करें।",
                "किसी स्थापित स्थानीय ब्रांड के साथ फ्रैंचाइज़ी या साझेदारी प्रवेश जोखिम कम कर सकती है।",
            ]
            rationale = "उच्च प्रतिस्पर्धा घनत्व। पूंजी लगाने से पहले अलग पहचान बनाने की रणनीति आवश्यक है।"
        return niches, rationale
    if lang == "kn":
        if density == "Low":
            niches = [
                f"ಮೊದಲ-ಪ್ರವೇಶ ಪ್ರಯೋಜನ: ಈ ಪ್ರದೇಶದಲ್ಲಿ {category} ಸೇವೆ ಕಡಿಮೆ ಇದೆ — 7.5 ಕಿ.ಮೀ ವ್ಯಾಪ್ತಿಯಲ್ಲಿ ಕೇವಲ "
                f"{competitors_nearby} ಇದೇ ರೀತಿಯ ವ್ಯಾಪಾರಗಳಿವೆ.",
                f"{round(lit_pct,1)}% ಸಾಕ್ಷರತಾ ಪ್ರಮಾಣ ಇಲ್ಲಿ ಔಪಚಾರಿಕ ವಹಿವಾಟು ಸಾಧ್ಯ ಎಂದು ತೋರಿಸುತ್ತದೆ — ಡಿಜಿಟಲ್ "
                f"ಪಾವತಿ ಮತ್ತು ದಾಖಲೆ ನಿರ್ವಹಣೆ ಅಳವಡಿಸಿಕೊಳ್ಳುವುದು ಸುಲಭ.",
            ]
            if agri_cat and agri_pct > 0.40:
                niches.append(
                    f"ಕೃಷಿ ಕಾರ್ಮಿಕ ಆಧಾರ ({round(agri_pct*100,1)}% ಕಾರ್ಮಿಕರು) {category} ಉತ್ಪನ್ನಗಳಿಗೆ "
                    f"ಸ್ವಾಭಾವಿಕ ಬೇಡಿಕೆಯನ್ನು ಸೃಷ್ಟಿಸುತ್ತದೆ — ಪೂರೈಕೆ ಚಕ್ರವನ್ನು ಬೆಳೆ ಋತುಗಳಿಗೆ ಹೊಂದಿಸಿ."
                )
            rationale = "ಕಡಿಮೆ ಸ್ಪರ್ಧಾ ಸಾಂದ್ರತೆಯು ಬಲವಾದ ಮೊದಲ-ಪ್ರವೇಶ ಅವಕಾಶವನ್ನು ಸೃಷ್ಟಿಸುತ್ತದೆ. ನಿರ್ಣಾಯಕವಾಗಿ ಮುಂದುವರಿಯಿರಿ."
        elif density == "Moderate":
            niches = [
                f"ಗುಣಮಟ್ಟ, ಕಂತುಗಳ ಪಾವತಿ ಸೌಲಭ್ಯ, ಅಥವಾ ನಿರ್ದಿಷ್ಟ ಕಡಿಮೆ-ಸೇವೆಯ ವಿಭಾಗವನ್ನು ಗುರಿಯಾಗಿಸಿಕೊಂಡು "
                f"{category} ನಲ್ಲಿ ನೇರ ಸ್ಪರ್ಧೆಯಿಂದ ಪ್ರತ್ಯೇಕವಾಗಿ ನಿಲ್ಲಿ.",
                "7.5 ಕಿ.ಮೀ ವ್ಯಾಪ್ತಿಯಲ್ಲಿ ಪ್ರಸ್ತುತ ಸ್ಪರ್ಧಿಗಳು ಚೆನ್ನಾಗಿ ಸೇವೆ ಸಲ್ಲಿಸದ ಗ್ರಾಮ ಗುಂಪುಗಳನ್ನು ಗುರಿಯಾಗಿಸಿ.",
            ]
            rationale = (
                f"ಮಧ್ಯಮ ಸ್ಪರ್ಧೆ: ಸ್ಪಷ್ಟ ತಂತ್ರದೊಂದಿಗೆ ಸಾಧ್ಯ. ಸುತ್ತಮುತ್ತ ಸರಾಸರಿ "
                f"{competitors_nearby} ಇದೇ ರೀತಿಯ ವ್ಯಾಪಾರಗಳಿವೆ."
            )
        else:
            niches = [
                f"ಈ ಸ್ಥಳದಲ್ಲಿ ನೇರವಾಗಿ {category} ಪ್ರವೇಶಿಸುವುದು ಅಪಾಯಕಾರಿ — ಹತ್ತಿರದ ಕಡಿಮೆ-ಸಾಂದ್ರತೆಯ "
                f"ಬ್ಲಾಕ್ ಅಥವಾ ವಿಶೇಷ ಪ್ರೀಮಿಯಂ ಉಪ-ವಿಭಾಗವನ್ನು ಪರಿಗಣಿಸಿ.",
                "ಸ್ಥಾಪಿತ ಸ್ಥಳೀಯ ಬ್ರ್ಯಾಂಡ್‌ನೊಂದಿಗೆ ಫ್ರ್ಯಾಂಚೈಸಿ ಅಥವಾ ಪಾಲುದಾರಿಕೆ ಪ್ರವೇಶ ಅಪಾಯವನ್ನು ಕಡಿಮೆ ಮಾಡಬಹುದು.",
            ]
            rationale = "ಹೆಚ್ಚಿನ ಸ್ಪರ್ಧಾ ಸಾಂದ್ರತೆ. ಬಂಡವಾಳ ಹೂಡುವ ಮೊದಲು ವಿಭಿನ್ನತೆಯ ತಂತ್ರ ಅಗತ್ಯ."
        return niches, rationale
    if lang == "te":
        if density == "Low":
            niches = [
                f"మొదటి-ప్రవేశ ప్రయోజనం: ఈ ప్రాంతంలో {category} సేవ తక్కువగా ఉంది — 7.5 కి.మీ పరిధిలో కేవలం "
                f"{competitors_nearby} ఇలాంటి వ్యాపారాలు ఉన్నాయి.",
                f"{round(lit_pct,1)}% అక్షరాస్యత రేటు ఇక్కడ అధికారిక లావాదేవీలు సాధ్యమని చూపిస్తుంది — డిజిటల్ "
                f"చెల్లింపులు మరియు రికార్డ్ నిర్వహణను అందిపుచ్చుకోవడం సులభం.",
            ]
            if agri_cat and agri_pct > 0.40:
                niches.append(
                    f"వ్యవసాయ కార్మిక ఆధారం ({round(agri_pct*100,1)}% కార్మికులు) {category} ఉత్పత్తులకు "
                    f"సహజ డిమాండ్‌ను సృష్టిస్తుంది — సరఫరా చక్రాన్ని పంట సీజన్లకు అనుగుణంగా ఉంచండి."
                )
            rationale = "తక్కువ పోటీ సాంద్రత బలమైన మొదటి-ప్రవేశ అవకాశాన్ని సృష్టిస్తుంది. నిర్ణయాత్మకంగా ముందుకు సాగండి."
        elif density == "Moderate":
            niches = [
                f"నాణ్యత, వాయిదాల చెల్లింపు సౌలభ్యం, లేదా నిర్దిష్ట తక్కువ-సేవా విభాగాన్ని లక్ష్యంగా చేసుకుని "
                f"{category} లో నేరుగా పోటీ నుండి తప్పించుకోండి.",
                "7.5 కి.మీ పరిధిలో ప్రస్తుత పోటీదారులు సరిగ్గా సేవ చేయని గ్రామ సమూహాలను లక్ష్యంగా చేసుకోండి.",
            ]
            rationale = (
                f"మధ్యస్థ పోటీ: స్పష్టమైన వ్యూహంతో సాధ్యమే. చుట్టుపక్కల సగటున "
                f"{competitors_nearby} ఇలాంటి వ్యాపారాలు ఉన్నాయి."
            )
        else:
            niches = [
                f"ఈ ప్రదేశంలో నేరుగా {category} లోకి ప్రవేశించడం రిస్క్‌తో కూడుకున్నది — సమీపంలోని తక్కువ-సాంద్రత "
                f"బ్లాక్ లేదా ప్రత్యేక ప్రీమియం ఉప-విభాగాన్ని పరిగణించండి.",
                "స్థాపిత స్థానిక బ్రాండ్‌తో ఫ్రాంచైజీ లేదా భాగస్వామ్యం ప్రవేశ రిస్క్‌ను తగ్గించవచ్చు.",
            ]
            rationale = "అధిక పోటీ సాంద్రత. మూలధనం పెట్టే ముందు భేదాత్మక వ్యూహం అవసరం."
        return niches, rationale
    # English (falls through to caller's existing English builder if desired)
    return None, None


def swot(
    lang: str, category: str, margin_capital: float, first_time: bool,
    legal_informal: bool, mobile_pct: float, electric_pct: float, lit_pct: float,
    density_rating: str,
):
    """Returns dict with strengths/weaknesses/opportunities/threats lists, or None for English."""
    if lang == "hi":
        strengths = [
            f"मालिक ने Rs. {margin_capital:,.0f} मार्जिन मनी के रूप में योगदान दिया है — यह प्रतिबद्धता दिखाता है "
            f"और बैंक का जोखिम कम करता है।",
            f"{category} की ग्रामीण राजस्थान बाजारों में स्थापित मांग है।",
        ]
        if mobile_pct > 70:
            strengths.append(
                f"जिले में उच्च मोबाइल पहुंच ({round(mobile_pct,0):.0f}%) पहले दिन से डिजिटल भुगतान "
                f"(UPI/PhonePe) संभव बनाती है — नकद संभालने का बोझ कम होता है।"
            )
        if electric_pct > 80:
            strengths.append(
                f"मजबूत बिजली पहुंच ({round(electric_pct,0):.0f}%) रेफ्रिजरेशन, मशीनरी और शाम के व्यापार "
                f"घंटों को सहारा देती है।"
            )
        weaknesses = [
            "पहली बार उद्यमिता में परिचालन और क्रियान्वयन जोखिम होता है।"
            if first_time else "प्रारंभिक स्थान से आगे बढ़ने के लिए अतिरिक्त पूंजी की आवश्यकता होगी जिसकी अभी योजना नहीं है।",
            "इस परियोजना-लागत स्तर पर कार्यशील पूंजी बफर सीमित है — 1-2 महीने की मांग में गिरावट भी "
            "चुकौती नकदी प्रवाह पर दबाव डाल सकती है।",
        ]
        if legal_informal:
            weaknesses.append(
                "फिलहाल कोई औपचारिक कानूनी ढांचा नहीं है — इस चरण में यह पूरी तरह सामान्य है और योजना पात्रता "
                "में बाधा नहीं डालता, लेकिन आमदनी शुरू होने पर एकल स्वामित्व (या SHG में शामिल होना) पंजीकृत "
                "करने से भविष्य में बैंक व्यवहार और उद्यम पंजीकरण आसान होगा।"
            )
        opportunities = [
            "सरकारी रियायती ऋण (PMEGP/MUDRA) अनौपचारिक साहूकारों (आमतौर पर 24-36% प्रति वर्ष) की तुलना में "
            "पूंजी लागत को काफी कम करता है।",
            f"{round(lit_pct,1)}% साक्षरता दर व्यवसाय स्थिर होने पर औपचारिक रसीदें, GST पंजीकरण, और "
            f"ई-कॉमर्स विस्तार को सहारा देती है।",
        ]
        if density_rating in ("Low", "Moderate"):
            opportunities.append(
                "बाजार संतृप्त होने से पहले ब्रांड वफादारी बनाने के लिए वर्तमान कम-से-मध्यम प्रतिस्पर्धा "
                "12-18 महीने की खिड़की देती है।"
            )
        threats = [
            f"{'उच्च' if density_rating == 'High' else 'मध्यम'} जिले में MSME सघनता का मतलब है कि "
            f"प्रतिस्पर्धा और बढ़ सकती है।",
            "इनपुट लागत में उतार-चढ़ाव (ईंधन, कच्चा माल) पहले साल में मार्जिन को कम कर सकता है।",
            "ग्रामीण सूक्ष्म-उद्यम श्रेणियों में मौसमी मांग में उतार-चढ़ाव सामान्य है।",
        ]
        return {"strengths": strengths, "weaknesses": weaknesses, "opportunities": opportunities, "threats": threats}
    if lang == "kn":
        strengths = [
            f"ಮಾಲೀಕರು Rs. {margin_capital:,.0f} ಅನ್ನು ಮಾರ್ಜಿನ್ ಹಣವಾಗಿ ಕೊಡುಗೆ ನೀಡಿದ್ದಾರೆ — ಇದು ಬದ್ಧತೆಯನ್ನು "
            f"ತೋರಿಸುತ್ತದೆ ಮತ್ತು ಬ್ಯಾಂಕಿನ ಅಪಾಯವನ್ನು ಕಡಿಮೆ ಮಾಡುತ್ತದೆ.",
            f"{category} ಗ್ರಾಮೀಣ ರಾಜಸ್ಥಾನ ಮಾರುಕಟ್ಟೆಗಳಲ್ಲಿ ಸ್ಥಾಪಿತ ಬೇಡಿಕೆಯನ್ನು ಹೊಂದಿದೆ.",
        ]
        if mobile_pct > 70:
            strengths.append(
                f"ಜಿಲ್ಲೆಯಲ್ಲಿ ಹೆಚ್ಚಿನ ಮೊಬೈಲ್ ವ್ಯಾಪ್ತಿ ({round(mobile_pct,0):.0f}%) ಮೊದಲ ದಿನದಿಂದಲೇ ಡಿಜಿಟಲ್ "
                f"ಪಾವತಿಗಳನ್ನು (UPI/PhonePe) ಸಾಧ್ಯವಾಗಿಸುತ್ತದೆ — ನಗದು ನಿರ್ವಹಣೆಯ ಹೊರೆ ಕಡಿಮೆಯಾಗುತ್ತದೆ."
            )
        if electric_pct > 80:
            strengths.append(
                f"ಬಲವಾದ ವಿದ್ಯುತ್ ಪ್ರವೇಶ ({round(electric_pct,0):.0f}%) ರೆಫ್ರಿಜರೇಶನ್, ಯಂತ್ರೋಪಕರಣ ಮತ್ತು "
                f"ಸಂಜೆಯ ವ್ಯಾಪಾರ ಸಮಯವನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ."
            )
        weaknesses = [
            "ಮೊದಲ ಬಾರಿಗೆ ಉದ್ಯಮಶೀಲತೆಯು ಕಾರ್ಯಾಚರಣೆ ಮತ್ತು ಅನುಷ್ಠಾನದ ಅಪಾಯವನ್ನು ಹೊಂದಿದೆ."
            if first_time else "ಆರಂಭಿಕ ಸ್ಥಳವನ್ನು ಮೀರಿ ವಿಸ್ತರಿಸಲು ಇನ್ನೂ ಯೋಜಿಸದ ಹೆಚ್ಚುವರಿ ಬಂಡವಾಳ ಬೇಕಾಗುತ್ತದೆ.",
            "ಈ ಯೋಜನಾ-ವೆಚ್ಚ ಮಟ್ಟದಲ್ಲಿ ಕಾರ್ಯಾಚರಣಾ ಬಂಡವಾಳ ಬಫರ್ ಸೀಮಿತವಾಗಿದೆ — 1-2 ತಿಂಗಳ ಬೇಡಿಕೆ ಕುಸಿತವೂ "
            "ಮರುಪಾವತಿ ನಗದು ಹರಿವಿನ ಮೇಲೆ ಒತ್ತಡ ಹೇರಬಹುದು.",
        ]
        if legal_informal:
            weaknesses.append(
                "ಪ್ರಸ್ತುತ ಯಾವುದೇ ಔಪಚಾರಿಕ ಕಾನೂನು ರಚನೆ ಇಲ್ಲ — ಈ ಹಂತದಲ್ಲಿ ಇದು ಸಂಪೂರ್ಣವಾಗಿ ಸಾಮಾನ್ಯ ಮತ್ತು "
                "ಯೋಜನೆ ಅರ್ಹತೆಗೆ ಅಡ್ಡಿಯಾಗುವುದಿಲ್ಲ, ಆದರೆ ಆದಾಯ ಪ್ರಾರಂಭವಾದ ನಂತರ ಏಕಮಾಲೀಕತ್ವ (ಅಥವಾ SHG "
                "ಸೇರುವುದು) ನೋಂದಾಯಿಸುವುದರಿಂದ ಭವಿಷ್ಯದ ಬ್ಯಾಂಕ್ ವ್ಯವಹಾರ ಮತ್ತು ಉದ್ಯಮ್ ನೋಂದಣಿ ಸುಲಭವಾಗುತ್ತದೆ."
            )
        opportunities = [
            "ಸರ್ಕಾರಿ ರಿಯಾಯಿತಿ ಸಾಲ (PMEGP/MUDRA) ಅನೌಪಚಾರಿಕ ಸಾಲದಾತರಿಗಿಂತ (ಸಾಮಾನ್ಯವಾಗಿ ವಾರ್ಷಿಕ 24-36%) "
            "ಬಂಡವಾಳ ವೆಚ್ಚವನ್ನು ಗಣನೀಯವಾಗಿ ಕಡಿಮೆ ಮಾಡುತ್ತದೆ.",
            f"{round(lit_pct,1)}% ಸಾಕ್ಷರತಾ ಪ್ರಮಾಣವು ವ್ಯಾಪಾರ ಸ್ಥಿರಗೊಂಡ ನಂತರ ಔಪಚಾರಿಕ ರಸೀದಿಗಳು, GST "
            f"ನೋಂದಣಿ, ಮತ್ತು ಇ-ಕಾಮರ್ಸ್ ವಿಸ್ತರಣೆಯನ್ನು ಬೆಂಬಲಿಸುತ್ತದೆ.",
        ]
        if density_rating in ("Low", "Moderate"):
            opportunities.append(
                "ಮಾರುಕಟ್ಟೆ ಸ್ಯಾಚುರೇಟ್ ಆಗುವ ಮೊದಲು ಬ್ರ್ಯಾಂಡ್ ನಿಷ್ಠೆಯನ್ನು ನಿರ್ಮಿಸಲು ಪ್ರಸ್ತುತ ಕಡಿಮೆ-ಮಧ್ಯಮ "
                "ಸ್ಪರ್ಧೆಯು 12-18 ತಿಂಗಳ ಅವಕಾಶವನ್ನು ನೀಡುತ್ತದೆ."
            )
        threats = [
            f"ಜಿಲ್ಲೆಯಲ್ಲಿ {'ಹೆಚ್ಚಿನ' if density_rating == 'High' else 'ಮಧ್ಯಮ'} MSME ಸಾಂದ್ರತೆಯು ಸ್ಪರ್ಧೆ "
            f"ಇನ್ನಷ್ಟು ತೀವ್ರಗೊಳ್ಳಬಹುದು ಎಂದರ್ಥ.",
            "ಇನ್‌ಪುಟ್ ವೆಚ್ಚದ ಏರಿಳಿತ (ಇಂಧನ, ಕಚ್ಚಾ ವಸ್ತುಗಳು) ಮೊದಲ ವರ್ಷದಲ್ಲಿ ಲಾಭಾಂಶವನ್ನು ಕುಗ್ಗಿಸಬಹುದು.",
            "ಗ್ರಾಮೀಣ ಸೂಕ್ಷ್ಮ-ಉದ್ಯಮ ವರ್ಗಗಳಲ್ಲಿ ಋತುಮಾನದ ಬೇಡಿಕೆ ಏರಿಳಿತ ಸಾಮಾನ್ಯವಾಗಿದೆ.",
        ]
        return {"strengths": strengths, "weaknesses": weaknesses, "opportunities": opportunities, "threats": threats}
    if lang == "te":
        strengths = [
            f"యజమాని Rs. {margin_capital:,.0f} ను మార్జిన్ మనీగా అందించారు — ఇది నిబద్ధతను చూపిస్తుంది "
            f"మరియు బ్యాంకు రిస్క్‌ను తగ్గిస్తుంది.",
            f"{category} గ్రామీణ రాజస్థాన్ మార్కెట్లలో స్థిరపడిన డిమాండ్‌ను కలిగి ఉంది.",
        ]
        if mobile_pct > 70:
            strengths.append(
                f"జిల్లాలో అధిక మొబైల్ వ్యాప్తి ({round(mobile_pct,0):.0f}%) మొదటి రోజు నుండే డిజిటల్ "
                f"చెల్లింపులను (UPI/PhonePe) సాధ్యం చేస్తుంది — నగదు నిర్వహణ భారం తగ్గుతుంది."
            )
        if electric_pct > 80:
            strengths.append(
                f"బలమైన విద్యుత్ లభ్యత ({round(electric_pct,0):.0f}%) రిఫ్రిజిరేషన్, యంత్రాలు మరియు "
                f"సాయంత్రం వ్యాపార గంటలకు మద్దతు ఇస్తుంది."
            )
        weaknesses = [
            "మొదటిసారి వ్యవస్థాపకత్వం నిర్వహణ మరియు అమలు రిస్క్‌ను కలిగి ఉంటుంది."
            if first_time else "ప్రారంభ ప్రదేశం దాటి విస్తరించడానికి ఇంకా ప్రణాళిక చేయని అదనపు మూలధనం అవసరం.",
            "ఈ ప్రాజెక్ట్-వ్యయ స్థాయిలో వర్కింగ్ క్యాపిటల్ బఫర్ పరిమితంగా ఉంది — 1-2 నెలల డిమాండ్ తగ్గుదల కూడా "
            "తిరిగి చెల్లింపు నగదు ప్రవాహంపై ఒత్తిడి తేవచ్చు.",
        ]
        if legal_informal:
            weaknesses.append(
                "ప్రస్తుతం ఎలాంటి అధికారిక చట్టపరమైన నిర్మాణం లేదు — ఈ దశలో ఇది పూర్తిగా సాధారణం మరియు పథక "
                "అర్హతను అడ్డుకోదు, కానీ ఆదాయం ప్రారంభమైన తర్వాత సోల్ ప్రొప్రైటర్‌షిప్ (లేదా SHGలో చేరడం) "
                "నమోదు చేసుకోవడం భవిష్యత్ బ్యాంక్ లావాదేవీలు మరియు ఉద్యమ్ నమోదును సులభతరం చేస్తుంది."
            )
        opportunities = [
            "ప్రభుత్వ రాయితీ రుణం (PMEGP/MUDRA) అనధికారిక వడ్డీ వ్యాపారుల కంటే (సాధారణంగా వార్షికంగా 24-36%) "
            "మూలధన వ్యయాన్ని గణనీయంగా తగ్గిస్తుంది.",
            f"{round(lit_pct,1)}% అక్షరాస్యత రేటు వ్యాపారం స్థిరపడిన తర్వాత అధికారిక రసీదులు, GST "
            f"నమోదు, మరియు ఇ-కామర్స్ విస్తరణకు తోడ్పడుతుంది.",
        ]
        if density_rating in ("Low", "Moderate"):
            opportunities.append(
                "మార్కెట్ సంతృప్తం కావడానికి ముందు బ్రాండ్ విధేయతను నిర్మించుకోవడానికి ప్రస్తుత తక్కువ-నుండి-మధ్యస్థ "
                "పోటీ 12-18 నెలల అవకాశాన్ని ఇస్తుంది."
            )
        threats = [
            f"జిల్లాలో {'అధిక' if density_rating == 'High' else 'మధ్యస్థ'} MSME సాంద్రత అంటే పోటీ "
            f"మరింత తీవ్రమయ్యే అవకాశం ఉంది.",
            "ఇన్‌పుట్ వ్యయ హెచ్చుతగ్గులు (ఇంధనం, ముడి పదార్థాలు) మొదటి సంవత్సరంలో మార్జిన్‌లను తగ్గించవచ్చు.",
            "గ్రామీణ సూక్ష్మ-పరిశ్రమ వర్గాలలో సీజనల్ డిమాండ్ హెచ్చుతగ్గులు సాధారణం.",
        ]
        return {"strengths": strengths, "weaknesses": weaknesses, "opportunities": opportunities, "threats": threats}
    return None


def threats(lang: str, density_high: bool, first_time: bool):
    """Returns list of (threat_name, severity, mitigation) tuples, or None for English."""
    if lang == "hi":
        items = [
            ("मौसमी मांग में उतार-चढ़ाव", "मध्यम",
             "कम-सीज़न महीनों के लिए 2-3 महीने का कार्यशील पूंजी बफर रखें। ऑफ-पीक अवधि के लिए किसी "
             "पूरक उत्पाद या सेवा में विविधता लाएं।"),
            ("इनपुट लागत व आपूर्ति श्रृंखला में उतार-चढ़ाव", "मध्यम",
             "पूंजी लगाने से पहले कम से कम दो आपूर्तिकर्ता स्रोत तय करें। एक ही आपूर्तिकर्ता पर निर्भरता से बचें।"),
            ("एकल-खरीदार सघनता जोखिम", "कम",
             "पहले 6 महीनों में ग्राहक आधार में विविधता लाएं। किसी एक बड़े खरीदार या संस्था पर अत्यधिक निर्भरता से बचें।"),
        ]
        if density_high:
            items.insert(0, (
                "उच्च स्थानीय MSME प्रतिस्पर्धा घनत्व", "उच्च",
                "स्थान पर पुनर्विचार करें, किसी दूसरे जिला ब्लॉक को लक्षित करें, या फंडिंग से पहले स्पष्ट "
                "अलग पहचान रणनीति (गुणवत्ता, क्रेडिट, डिलीवरी) बनाएं।",
            ))
        if first_time:
            items.append((
                "पहली बार उद्यमी क्रियान्वयन जोखिम", "मध्यम",
                "MSME/RSETI उद्यमिता प्रशिक्षण में दाखिला लें। साथियों के सहयोग और मार्गदर्शन के लिए स्थानीय "
                "SHG या व्यवसाय समूह से जुड़ें।",
            ))
        return items
    if lang == "kn":
        items = [
            ("ಋತುಮಾನದ ಬೇಡಿಕೆ ಏರಿಳಿತ", "ಮಧ್ಯಮ",
             "ಕಡಿಮೆ-ಋತುವಿನ ತಿಂಗಳುಗಳಿಗೆ 2-3 ತಿಂಗಳ ಕಾರ್ಯಾಚರಣಾ ಬಂಡವಾಳ ಬಫರ್ ಯೋಜಿಸಿ. ಆಫ್-ಪೀಕ್ "
             "ಅವಧಿಗಳಿಗೆ ಪೂರಕ ಉತ್ಪನ್ನ ಅಥವಾ ಸೇವೆಯನ್ನು ವೈವಿಧ್ಯಗೊಳಿಸಿ."),
            ("ಇನ್‌ಪುಟ್ ವೆಚ್ಚ ಮತ್ತು ಪೂರೈಕೆ ಸರಪಳಿ ಏರಿಳಿತ", "ಮಧ್ಯಮ",
             "ಬಂಡವಾಳ ಹೂಡುವ ಮೊದಲು ಕನಿಷ್ಠ ಎರಡು ಪೂರೈಕೆದಾರ ಮೂಲಗಳನ್ನು ಗುರುತಿಸಿ. ಒಂದೇ-ಪೂರೈಕೆದಾರ "
             "ಅವಲಂಬನೆಯನ್ನು ತಪ್ಪಿಸಿ."),
            ("ಏಕ-ಖರೀದಿದಾರ ಸಾಂದ್ರತೆಯ ಅಪಾಯ", "ಕಡಿಮೆ",
             "ಮೊದಲ 6 ತಿಂಗಳಲ್ಲಿ ಗ್ರಾಹಕರ ಆಧಾರವನ್ನು ವೈವಿಧ್ಯಗೊಳಿಸಿ. ಒಂದೇ ದೊಡ್ಡ ಖರೀದಿದಾರ ಅಥವಾ "
             "ಸಂಸ್ಥೆಯ ಮೇಲೆ ಅತಿಯಾದ ಅವಲಂಬನೆಯನ್ನು ತಪ್ಪಿಸಿ."),
        ]
        if density_high:
            items.insert(0, (
                "ಹೆಚ್ಚಿನ ಸ್ಥಳೀಯ MSME ಸ್ಪರ್ಧಾ ಸಾಂದ್ರತೆ", "ಹೆಚ್ಚಿನ",
                "ಸ್ಥಳವನ್ನು ಮರುಪರಿಶೀಲಿಸಿ, ಬೇರೆ ಜಿಲ್ಲಾ ಬ್ಲಾಕ್ ಗುರಿಯಾಗಿಸಿ, ಅಥವಾ ಹಣ ಪಡೆಯುವ ಮೊದಲು ಸ್ಪಷ್ಟ "
                "ವಿಭಿನ್ನತೆಯ ತಂತ್ರವನ್ನು (ಗುಣಮಟ್ಟ, ಕ್ರೆಡಿಟ್, ವಿತರಣೆ) ಯೋಜಿಸಿ.",
            ))
        if first_time:
            items.append((
                "ಮೊದಲ ಬಾರಿಗೆ ಉದ್ಯಮಿಯ ಅನುಷ್ಠಾನ ಅಪಾಯ", "ಮಧ್ಯಮ",
                "MSME/RSETI ಉದ್ಯಮಶೀಲತಾ ತರಬೇತಿಗೆ ಸೇರಿ. ಸಹವರ್ತಿ ಬೆಂಬಲ ಮತ್ತು ಮಾರ್ಗದರ್ಶನಕ್ಕಾಗಿ ಸ್ಥಳೀಯ "
                "SHG ಅಥವಾ ವ್ಯಾಪಾರ ಗುಂಪನ್ನು ಸೇರಿ.",
            ))
        return items
    if lang == "te":
        items = [
            ("సీజనల్ డిమాండ్ హెచ్చుతగ్గులు", "మధ్యస్థం",
             "తక్కువ-సీజన్ నెలలకు 2-3 నెలల వర్కింగ్ క్యాపిటల్ బఫర్‌ను ప్రణాళిక చేయండి. ఆఫ్-పీక్ "
             "కాలాలకు అనుబంధ ఉత్పత్తి లేదా సేవను వైవిధ్యపరచండి."),
            ("ఇన్‌పుట్ వ్యయం & సరఫరా గొలుసు హెచ్చుతగ్గులు", "మధ్యస్థం",
             "మూలధనం పెట్టే ముందు కనీసం రెండు సరఫరాదారు మూలాలను గుర్తించండి. ఒకే-సరఫరాదారుపై "
             "ఆధారపడటాన్ని నివారించండి."),
            ("ఏక-కొనుగోలుదారు కేంద్రీకరణ రిస్క్", "తక్కువ",
             "మొదటి 6 నెలల్లో కస్టమర్ ఆధారాన్ని వైవిధ్యపరచండి. ఒకే పెద్ద కొనుగోలుదారు లేదా "
             "సంస్థపై అధికంగా ఆధారపడటాన్ని నివారించండి."),
        ]
        if density_high:
            items.insert(0, (
                "అధిక స్థానిక MSME పోటీ సాంద్రత", "అధికం",
                "స్థానాన్ని పునఃపరిశీలించండి, వేరే జిల్లా బ్లాక్‌ను లక్ష్యంగా చేసుకోండి, లేదా నిధులు పొందే ముందు "
                "స్పష్టమైన భేదాత్మక వ్యూహాన్ని (నాణ్యత, క్రెడిట్, డెలివరీ) ప్రణాళిక చేయండి.",
            ))
        if first_time:
            items.append((
                "మొదటిసారి వ్యవస్థాపకుడి అమలు రిస్క్", "మధ్యస్థం",
                "MSME/RSETI వ్యవస్థాపకత్వ శిక్షణలో చేరండి. తోటివారి మద్దతు మరియు మార్గదర్శకత్వం కోసం "
                "స్థానిక SHG లేదా వ్యాపార సమూహంలో చేరండి.",
            ))
        return items
    return None


# ── Pricing rationale ──────────────────────────────────────────────────────
# Commodity names used as mandi-price proxies (market_data.CATEGORY_PRICE_PROXY) —
# these are real commodity names shown inside the pricing rationale sentence and
# must be translated, not interpolated verbatim in English.
_COMMODITY_NAMES: Dict[str, Dict[str, str]] = {
    "Wheat":   {"hi": "गेहूं", "kn": "ಗೋಧಿ", "te": "గోధుమ"},
    "Tomato":  {"hi": "टमाटर", "kn": "ಟೊಮ್ಯಾಟೊ", "te": "టమాటా"},
    "Onion":   {"hi": "प्याज़", "kn": "ಈರುಳ್ಳಿ", "te": "ఉల్లిపాయ"},
    "Potato":  {"hi": "आलू", "kn": "ಆಲೂಗಡ್ಡೆ", "te": "బంగాళదుంప"},
}

_DISTRICT_WORD = {"hi": "ज़िला", "kn": "ಜಿಲ್ಲೆ", "te": "జిల్లా"}
_STATE_WORD = {"hi": "राज्य", "kn": "ರಾಜ್ಯ", "te": "రాష్ట్రం"}
_ESTIMATED_WORD = {"hi": "अनुमानित", "kn": "ಅಂದಾಜು", "te": "అంచనా"}
_RAJASTHAN_NAME = {"hi": "राजस्थान", "kn": "ರಾಜಸ್ಥಾನ", "te": "రాజస్థాన్"}


def _localized_commodity(lang: str, commodity: str) -> str:
    return _COMMODITY_NAMES.get(commodity, {}).get(lang, commodity)


def _localized_data_scope(lang: str, scope: str) -> str:
    """market_data.get_commodity_price_trend() only ever produces one of three
    shapes for `scope`: "<District> district", "Rajasthan state", or "estimated"."""
    if scope == "estimated":
        return _ESTIMATED_WORD.get(lang, scope)
    if scope.lower() == "rajasthan state":
        return f"{_RAJASTHAN_NAME.get(lang, 'Rajasthan')} {_STATE_WORD.get(lang, 'state')}"
    match = re.match(r"^(.*)\s+district$", scope, flags=re.IGNORECASE)
    if match:
        return f"{match.group(1)} {_DISTRICT_WORD.get(lang, 'district')}"
    return scope


def pricing_rationale(
    lang: str, commodity: str, scope: str, mandi_rate: float, category_display: str,
    low: float, high: float, unit: str, trend_dir_up: bool, trend_abs: float,
) -> Optional[str]:
    if lang in ("hi", "kn", "te"):
        commodity = _localized_commodity(lang, commodity)
        scope = _localized_data_scope(lang, scope)
    if lang == "hi":
        trend_word = "ऊपर" if trend_dir_up else "नीचे"
        signal = "नए प्रवेशकों के लिए एक अनुकूल संकेत है" if trend_dir_up else "इसे अपने कार्यशील पूंजी बफर में शामिल करें"
        return (
            f"वास्तविक {commodity} मंडी कीमतों ({scope}: Rs. {mandi_rate}/क्विंटल, Agmarknet से) के आधार पर, "
            f"{category_display} के लिए एक टिकाऊ बिक्री कीमत सीमा Rs. {low}–{high} {unit} है। "
            f"पिछले 30 दिनों का बाज़ार कीमत रुझान {trend_word} {abs(trend_abs)}% है — {signal}।"
        )
    if lang == "kn":
        trend_word = "ಏರಿಕೆ" if trend_dir_up else "ಇಳಿಕೆ"
        signal = "ಹೊಸ ಪ್ರವೇಶಕರಿಗೆ ಅನುಕೂಲಕರ ಸಂಕೇತ" if trend_dir_up else "ಇದನ್ನು ನಿಮ್ಮ ಕಾರ್ಯಾಚರಣಾ ಬಂಡವಾಳ ಬಫರ್‌ನಲ್ಲಿ ಪರಿಗಣಿಸಿ"
        return (
            f"ನಿಜವಾದ {commodity} ಮಂಡಿ ಬೆಲೆಗಳ ({scope}: Rs. {mandi_rate}/ಕ್ವಿಂಟಲ್, Agmarknet ನಿಂದ) ಆಧಾರದ ಮೇಲೆ, "
            f"{category_display} ಗೆ ಸುಸ್ಥಿರ ಮಾರಾಟ ಬೆಲೆ ವ್ಯಾಪ್ತಿ Rs. {low}–{high} {unit} ಆಗಿದೆ. "
            f"ಕಳೆದ 30 ದಿನಗಳ ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ಪ್ರವೃತ್ತಿ {trend_word} {abs(trend_abs)}% ಆಗಿದೆ — {signal}."
        )
    if lang == "te":
        trend_word = "పైకి" if trend_dir_up else "కిందికి"
        signal = "కొత్త ప్రవేశకులకు అనుకూలమైన సంకేతం" if trend_dir_up else "దీన్ని మీ వర్కింగ్ క్యాపిటల్ బఫర్‌లో పరిగణించండి"
        return (
            f"వాస్తవ {commodity} మండి ధరల ({scope}: Rs. {mandi_rate}/క్వింటాల్, Agmarknet నుండి) ఆధారంగా, "
            f"{category_display} కు స్థిరమైన అమ్మకపు ధర శ్రేణి Rs. {low}–{high} {unit}. "
            f"గత 30 రోజుల మార్కెట్ ధర ధోరణి {trend_word} {abs(trend_abs)}%గా ఉంది — {signal}."
        )
    return None


# ── Revenue estimator text ─────────────────────────────────────────────────
def revenue_dairy_texts(lang: str, est_animals: int, fat_price: float, cow_fat_pct: float,
                         buffalo_fat_pct: float, yield_per_animal: float):
    if lang == "hi":
        return {
            "raw_material_examples": [
                f"आपका अपना झुंड (~{est_animals} दुधारू पशु, गाय/भैंस मिश्रित)",
                "पशु आहार / चारा आपूर्तिकर्ता (सांद्रित आहार के लिए)",
                "पशु चिकित्सा या पशुपालन विभाग (स्वास्थ्य संबंधी इनपुट के लिए)",
            ],
            "distributor_examples": [
                "जिला डेयरी सहकारी समिति / मिल्क यूनियन खरीद केंद्र",
                "प्रत्यक्ष घर-घर डिलीवरी मार्ग",
                "स्थानीय मिठाई की दुकान / चाय स्टॉल के थोक खरीदार",
            ],
            "downside_risk_note": (
                f"यह मानता है कि सभी {est_animals} पशु स्वस्थ हैं और साल भर पूरा दूध देते हैं। असल में "
                f"हर पशु के चक्र में सूखे (गैर-दुग्ध) काल के दौरान डेयरी आय 30-40% तक गिर जाती है, और बीमारी "
                f"या खराब आहार से उपज और कम हो सकती है। कम से कम 2 महीने के कम-उपज बफर का बजट रखें, और "
                f"हर महीने उच्चतम आंकड़े को न मानें।"
            ),
            "methodology": (
                f"फैट-आधारित मूल्य निर्धारण: दूध की कीमत फैट सामग्री से तय होती है (केवल मात्रा से नहीं)। "
                f"Rs. {fat_price:.0f}/किग्रा फैट (अमूल की 2025 खरीद दर) पर, गाय का दूध (~{cow_fat_pct*100:.1f}% फैट) "
                f"और भैंस का दूध (~{buffalo_fat_pct*100:.1f}% फैट) ~{est_animals} पशुओं के झुंड के लिए, जो "
                f"~{yield_per_animal:.0f} लीटर/पशु/दिन देते हैं, कम/अधिक सीमा तय करते हैं।"
            ),
        }
    if lang == "kn":
        return {
            "raw_material_examples": [
                f"ನಿಮ್ಮ ಸ್ವಂತ ಹಿಂಡು (~{est_animals} ಹಾಲುಣಿಸುವ ಪ್ರಾಣಿಗಳು, ಹಸು/ಎಮ್ಮೆ ಮಿಶ್ರಿತ)",
                "ಸ್ಥಳೀಯ ಜಾನುವಾರು ಆಹಾರ / ಮೇವು ಪೂರೈಕೆದಾರ (ಸಾಂದ್ರೀಕೃತ ಆಹಾರಕ್ಕಾಗಿ)",
                "ಗ್ರಾಮ ಪಶುವೈದ್ಯಕೀಯ ಅಥವಾ ಪಶುಸಂಗೋಪನಾ ಇಲಾಖೆ (ಆರೋಗ್ಯ ಇನ್‌ಪುಟ್‌ಗಳಿಗಾಗಿ)",
            ],
            "distributor_examples": [
                "ಜಿಲ್ಲಾ ಡೈರಿ ಸಹಕಾರ ಸಂಘ / ಮಿಲ್ಕ್ ಯೂನಿಯನ್ ಖರೀದಿ ಕೇಂದ್ರ",
                "ನೇರ ಮನೆ-ಮನೆ ವಿತರಣಾ ಮಾರ್ಗ",
                "ಸ್ಥಳೀಯ ಸಿಹಿ ಅಂಗಡಿ / ಟೀ ಸ್ಟಾಲ್ ಸಗಟು ಖರೀದಿದಾರರು",
            ],
            "downside_risk_note": (
                f"ಇದು {est_animals} ಪ್ರಾಣಿಗಳೂ ಆರೋಗ್ಯಕರವಾಗಿದ್ದು ವರ್ಷಪೂರ್ತಿ ಪೂರ್ಣ ಹಾಲು ನೀಡುತ್ತವೆ ಎಂದು "
                f"ಊಹಿಸುತ್ತದೆ. ವಾಸ್ತವದಲ್ಲಿ ಪ್ರತಿ ಪ್ರಾಣಿಯ ಚಕ್ರದ ಒಣ (ಹಾಲುಣಿಸದ) ಅವಧಿಯಲ್ಲಿ ಡೈರಿ ಆದಾಯ "
                f"30-40% ಕುಸಿಯುತ್ತದೆ, ಮತ್ತು ರೋಗ ಅಥವಾ ಕಳಪೆ ಆಹಾರ ಇಳುವರಿಯನ್ನು ಇನ್ನಷ್ಟು ಕಡಿಮೆ ಮಾಡಬಹುದು. "
                f"ಕನಿಷ್ಠ 2 ತಿಂಗಳ ಕಡಿಮೆ-ಇಳುವರಿ ಬಫರ್‌ಗೆ ಬಜೆಟ್ ಮಾಡಿ, ಮತ್ತು ಪ್ರತಿ ತಿಂಗಳೂ ಗರಿಷ್ಠ ಅಂಕಿ ಅಂಶ "
                f"ಸಿಗುತ್ತದೆ ಎಂದು ಊಹಿಸಬೇಡಿ."
            ),
            "methodology": (
                f"ಫ್ಯಾಟ್-ಆಧಾರಿತ ಬೆಲೆ ನಿಗದಿ: ಹಾಲಿನ ಬೆಲೆಯನ್ನು ಫ್ಯಾಟ್ ಅಂಶ ನಿರ್ಧರಿಸುತ್ತದೆ (ಪ್ರಮಾಣ ಮಾತ್ರವಲ್ಲ). "
                f"Rs. {fat_price:.0f}/ಕೆಜಿ ಫ್ಯಾಟ್ (ಅಮುಲ್‌ನ 2025 ಖರೀದಿ ದರ) ದರದಲ್ಲಿ, ಹಸುವಿನ ಹಾಲು (~{cow_fat_pct*100:.1f}% ಫ್ಯಾಟ್) "
                f"ಮತ್ತು ಎಮ್ಮೆ ಹಾಲು (~{buffalo_fat_pct*100:.1f}% ಫ್ಯಾಟ್) ~{est_animals} ಪ್ರಾಣಿಗಳ ಹಿಂಡಿಗೆ, "
                f"~{yield_per_animal:.0f} ಲೀಟರ್/ಪ್ರಾಣಿ/ದಿನ ಇಳುವರಿ ನೀಡುತ್ತಾ, ಕಡಿಮೆ/ಹೆಚ್ಚಿನ ವ್ಯಾಪ್ತಿಯನ್ನು ನೀಡುತ್ತವೆ."
            ),
        }
    if lang == "te":
        return {
            "raw_material_examples": [
                f"మీ స్వంత మంద (~{est_animals} పాలిచ్చే జంతువులు, ఆవు/గేదె మిశ్రమం)",
                "స్థానిక పశు మేత / దాణా సరఫరాదారు (సాంద్రీకృత దాణా కోసం)",
                "గ్రామ పశువైద్య లేదా పశుసంవర్ధక శాఖ (ఆరోగ్య ఇన్‌పుట్‌ల కోసం)",
            ],
            "distributor_examples": [
                "జిల్లా పాడి సహకార సంఘం / మిల్క్ యూనియన్ కొనుగోలు కేంద్రం",
                "నేరుగా ఇంటింటికి డెలివరీ మార్గం",
                "స్థానిక స్వీట్ షాప్ / టీ స్టాల్ టోకు కొనుగోలుదారులు",
            ],
            "downside_risk_note": (
                f"ఇది {est_animals} జంతువులు ఆరోగ్యంగా ఉండి ఏడాది పొడవునా పూర్తి పాలు ఇస్తాయని భావిస్తుంది. "
                f"వాస్తవానికి ప్రతి జంతువు చక్రంలో పొడి (పాలు ఇవ్వని) కాలంలో పాడి ఆదాయం 30-40% వరకు తగ్గుతుంది, "
                f"మరియు వ్యాధి లేదా నాణ్యత లేని దాణా దిగుబడిని మరింత తగ్గించవచ్చు. కనీసం 2 నెలల తక్కువ-దిగుబడి "
                f"బఫర్‌కు బడ్జెట్ వేసుకోండి, మరియు ప్రతి నెలా అత్యధిక అంకెను ఊహించుకోకండి."
            ),
            "methodology": (
                f"ఫ్యాట్-ఆధారిత ధర నిర్ణయం: పాల ధరను ఫ్యాట్ శాతం నిర్ణయిస్తుంది (కేవలం పరిమాణం కాదు). "
                f"Rs. {fat_price:.0f}/కిలో ఫ్యాట్ (అమూల్ 2025 కొనుగోలు రేటు) వద్ద, ఆవు పాలు (~{cow_fat_pct*100:.1f}% ఫ్యాట్) "
                f"మరియు గేదె పాలు (~{buffalo_fat_pct*100:.1f}% ఫ్యాట్) ~{est_animals} జంతువుల మందకు, "
                f"~{yield_per_animal:.0f} లీటర్లు/జంతువు/రోజుకు దిగుబడితో, తక్కువ/ఎక్కువ శ్రేణిని ఇస్తాయి."
            ),
        }
    return None


def revenue_retail_texts(lang: str):
    if lang == "hi":
        return {
            "raw_material_examples": [
                "ब्लॉक या जिला कस्बे में नज़दीकी थोक/किराना डिस्ट्रीब्यूटर",
                "FMCG कंपनी का स्थानीय ग्रामीण डिस्ट्रीब्यूटर (बिस्किट, साबुन, पैकेज्ड सामान)",
                "ढीले अनाज, दालों और सब्जियों के लिए स्थानीय मंडी",
            ],
            "distributor_examples": [
                "नज़दीकी कस्बे का थोक किराना आपूर्तिकर्ता",
                "इस गांव को कवर करने वाला FMCG वैन/सेल्समैन मार्ग",
                "साप्ताहिक हाट (बाज़ार) थोक आपूर्तिकर्ता",
            ],
            "downside_risk_note": (
                "किराना मार्जिन पतला होता है (टर्नओवर का 8-15%) - एक सुस्त महीना, किसी बड़े ग्राहक का बकाया "
                "उधार, या पास में कोई नई प्रतिस्पर्धी दुकान एक लाभदायक महीने को घाटे में बदल सकती है। समय पर "
                "चुकाया न जा सके उससे अधिक अनौपचारिक उधार न दें।"
            ),
            "methodology": (
                "खुदरा उद्योग स्रोतों द्वारा बताई गई वास्तविक ग्रामीण किराना (जनरल स्टोर) आय सीमा: Rs. "
                "30,000-60,000/माह टर्नओवर, सामान्य किराना/FMCG मार्जिन 8-15% के साथ।"
            ),
        }
    if lang == "kn":
        return {
            "raw_material_examples": [
                "ಬ್ಲಾಕ್ ಅಥವಾ ಜಿಲ್ಲಾ ಪಟ್ಟಣದಲ್ಲಿ ಹತ್ತಿರದ ಸಗಟು/ಕಿರಾಣಿ ವಿತರಕ",
                "FMCG ಕಂಪನಿಯ ಸ್ಥಳೀಯ ಗ್ರಾಮೀಣ ವಿತರಕ (ಬಿಸ್ಕತ್, ಸೋಪು, ಪ್ಯಾಕೇಜ್ಡ್ ಸರಕುಗಳು)",
                "ಸಡಿಲ ಧಾನ್ಯಗಳು, ಬೇಳೆಕಾಳುಗಳು ಮತ್ತು ತರಕಾರಿಗಳಿಗೆ ಸ್ಥಳೀಯ ಮಂಡಿ",
            ],
            "distributor_examples": [
                "ಹತ್ತಿರದ ಪಟ್ಟಣದ ಸಗಟು ಕಿರಾಣಿ ಪೂರೈಕೆದಾರ",
                "ಈ ಗ್ರಾಮವನ್ನು ಒಳಗೊಂಡ FMCG ವ್ಯಾನ್/ಸೇಲ್ಸ್‌ಮ್ಯಾನ್ ಮಾರ್ಗ",
                "ವಾರದ ಸಂತೆ (ಮಾರುಕಟ್ಟೆ) ಸಗಟು ಪೂರೈಕೆದಾರರು",
            ],
            "downside_risk_note": (
                "ಕಿರಾಣಿ ಲಾಭಾಂಶ ತೆಳುವಾಗಿದೆ (ವಹಿವಾಟಿನ 8-15%) - ಒಂದು ನಿಧಾನ ತಿಂಗಳು, ದೊಡ್ಡ ಗ್ರಾಹಕರ ಬಾಕಿ "
                "ಸಾಲ, ಅಥವಾ ಹತ್ತಿರದಲ್ಲಿ ಹೊಸ ಸ್ಪರ್ಧಾತ್ಮಕ ಅಂಗಡಿ ಲಾಭದಾಯಕ ತಿಂಗಳನ್ನು ನಷ್ಟಕ್ಕೆ ತಿರುಗಿಸಬಹುದು. "
                "ಸಮಯಕ್ಕೆ ಮರುಪಾವತಿಸಲಾಗದಷ್ಟು ಅನೌಪಚಾರಿಕ ಸಾಲ ನೀಡಬೇಡಿ."
            ),
            "methodology": (
                "ಚಿಲ್ಲರೆ ಉದ್ಯಮ ಮೂಲಗಳು ವರದಿ ಮಾಡಿದ ನಿಜವಾದ ಗ್ರಾಮೀಣ ಕಿರಾಣಿ (ಜನರಲ್ ಸ್ಟೋರ್) ಆದಾಯ ವ್ಯಾಪ್ತಿ: Rs. "
                "30,000-60,000/ತಿಂಗಳ ವಹಿವಾಟು, ವಿಶಿಷ್ಟ ಕಿರಾಣಿ/FMCG ಲಾಭಾಂಶ 8-15% ನೊಂದಿಗೆ."
            ),
        }
    if lang == "te":
        return {
            "raw_material_examples": [
                "బ్లాక్ లేదా జిల్లా పట్టణంలో సమీప టోకు/కిరాణా డిస్ట్రిబ్యూటర్",
                "FMCG కంపెనీ స్థానిక గ్రామీణ డిస్ట్రిబ్యూటర్ (బిస్కెట్లు, సబ్బు, ప్యాకేజ్డ్ వస్తువులు)",
                "వదులు ధాన్యాలు, పప్పులు మరియు కూరగాయల కోసం స్థానిక మండి",
            ],
            "distributor_examples": [
                "సమీప పట్టణంలోని టోకు కిరాణా సరఫరాదారు",
                "ఈ గ్రామాన్ని కవర్ చేసే FMCG వ్యాన్/సేల్స్‌మ్యాన్ మార్గం",
                "వారపు సంత (మార్కెట్) టోకు సరఫరాదారులు",
            ],
            "downside_risk_note": (
                "కిరాణా మార్జిన్లు తక్కువగా ఉంటాయి (టర్నోవర్‌లో 8-15%) - ఒక నెమ్మదైన నెల, పెద్ద కస్టమర్ "
                "బకాయి అప్పు, లేదా సమీపంలో కొత్త పోటీ దుకాణం లాభదాయకమైన నెలను నష్టంగా మార్చవచ్చు. సకాలంలో "
                "తిరిగి చెల్లించలేని దానికంటే ఎక్కువ అనధికారిక అప్పు ఇవ్వకండి."
            ),
            "methodology": (
                "రిటైల్ పరిశ్రమ మూలాలు నివేదించిన నిజమైన గ్రామీణ కిరాణా (జనరల్ స్టోర్) ఆదాయ శ్రేణి: Rs. "
                "30,000-60,000/నెల టర్నోవర్, సాధారణ కిరాణా/FMCG మార్జిన్లు 8-15%తో."
            ),
        }
    return None


def revenue_asuse_texts(lang: str, category_display: str, annual_gvo: int):
    if lang == "hi":
        return {
            "raw_material_examples": [
                f"ब्लॉक/जिला कस्बे में {category_display} इनपुट के लिए नज़दीकी थोक आपूर्तिकर्ता",
                "कच्चे माल के लिए स्थानीय मंडी या साप्ताहिक हाट",
            ],
            "distributor_examples": [
                "गांव/ब्लॉक हाट पर प्रत्यक्ष बिक्री",
                "नज़दीकी कस्बे का थोक/खुदरा नेटवर्क",
            ],
            "downside_risk_note": (
                f"यह एक सामान्य, आधिकारिक अखिल-भारतीय औसत का उपयोग करता है क्योंकि "
                f"{category_display} के लिए श्रेणी-विशिष्ट वास्तविक डेटासेट उपलब्ध नहीं था - आपका वास्तविक "
                f"परिणाम स्थानीय मांग के आधार पर काफी अधिक या कम हो सकता है। इसे एक शुरुआती योजना आंकड़ा "
                f"मानें, गारंटी नहीं, और अपनी पहली 2-3 महीने की वास्तविक बिक्री के बाद इसकी समीक्षा करें।"
            ),
            "methodology": (
                f"सामान्य-उद्देश्य फॉलबैक जो MoSPI/NSO की असंगठित क्षेत्र उद्यम वार्षिक सर्वेक्षण (ASUSE) "
                f"2022-23 के आधिकारिक औसत सकल उत्पादन मूल्य (GVO) Rs. {annual_gvo:,}/वर्ष प्रति "
                f"असंगठित-क्षेत्र प्रतिष्ठान का उपयोग करता है, क्योंकि इस व्यवसाय प्रकार के लिए इस टूल में अभी "
                f"कोई श्रेणी-विशिष्ट वास्तविक डेटासेट मौजूद नहीं है।"
            ),
        }
    if lang == "kn":
        return {
            "raw_material_examples": [
                f"ಬ್ಲಾಕ್/ಜಿಲ್ಲಾ ಪಟ್ಟಣದಲ್ಲಿ {category_display} ಇನ್‌ಪುಟ್‌ಗಳಿಗಾಗಿ ಹತ್ತಿರದ ಸಗಟು ಪೂರೈಕೆದಾರ",
                "ಕಚ್ಚಾ ವಸ್ತುಗಳಿಗಾಗಿ ಸ್ಥಳೀಯ ಮಂಡಿ ಅಥವಾ ವಾರದ ಸಂತೆ",
            ],
            "distributor_examples": [
                "ಗ್ರಾಮ/ಬ್ಲಾಕ್ ಸಂತೆಯಲ್ಲಿ ನೇರ ಮಾರಾಟ",
                "ಹತ್ತಿರದ ಪಟ್ಟಣದ ಸಗಟು/ಚಿಲ್ಲರೆ ಜಾಲ",
            ],
            "downside_risk_note": (
                f"{category_display} ಗಾಗಿ ವರ್ಗ-ನಿರ್ದಿಷ್ಟ ನಿಜವಾದ ಡೇಟಾಸೆಟ್ ಲಭ್ಯವಿಲ್ಲದ ಕಾರಣ ಇದು ಅನೌಪಚಾರಿಕ "
                f"ಸೂಕ್ಷ್ಮ-ಉದ್ಯಮಗಳಿಗೆ ಸಾಮಾನ್ಯ, ಅಧಿಕೃತ ಅಖಿಲ-ಭಾರತ ಸರಾಸರಿಯನ್ನು ಬಳಸುತ್ತದೆ - ನಿಮ್ಮ ನಿಜವಾದ "
                f"ಫಲಿತಾಂಶವು ಸ್ಥಳೀಯ ಬೇಡಿಕೆಯನ್ನು ಅವಲಂಬಿಸಿ ಗಣನೀಯವಾಗಿ ಹೆಚ್ಚು ಅಥವಾ ಕಡಿಮೆ ಇರಬಹುದು. ಇದನ್ನು "
                f"ಆರಂಭಿಕ ಯೋಜನಾ ಅಂಕಿ ಎಂದು ಪರಿಗಣಿಸಿ, ಖಾತರಿಯಲ್ಲ, ಮತ್ತು ನಿಮ್ಮ ಮೊದಲ 2-3 ತಿಂಗಳ ನಿಜವಾದ "
                f"ಮಾರಾಟದ ನಂತರ ಇದನ್ನು ಮರುಪರಿಶೀಲಿಸಿ."
            ),
            "methodology": (
                f"MoSPI/NSO ಯ ಅಸಂಘಟಿತ ವಲಯ ಉದ್ಯಮಗಳ ವಾರ್ಷಿಕ ಸಮೀಕ್ಷೆ (ASUSE) 2022-23 ರ ಅಧಿಕೃತ ಸರಾಸರಿ "
                f"ಒಟ್ಟು ಉತ್ಪಾದನಾ ಮೌಲ್ಯ (GVO) Rs. {annual_gvo:,}/ವರ್ಷ ಪ್ರತಿ ಅಸಂಘಟಿತ-ವಲಯ ಸಂಸ್ಥೆಯನ್ನು "
                f"ಬಳಸುವ ಸಾಮಾನ್ಯ-ಉದ್ದೇಶದ ಫಾಲ್‌ಬ್ಯಾಕ್, ಏಕೆಂದರೆ ಈ ವ್ಯಾಪಾರ ಪ್ರಕಾರಕ್ಕೆ ಈ ಸಾಧನದಲ್ಲಿ ಇನ್ನೂ "
                f"ಯಾವುದೇ ವರ್ಗ-ನಿರ್ದಿಷ್ಟ ನಿಜವಾದ ಡೇಟಾಸೆಟ್ ಅಸ್ತಿತ್ವದಲ್ಲಿಲ್ಲ."
            ),
        }
    if lang == "te":
        return {
            "raw_material_examples": [
                f"బ్లాక్/జిల్లా పట్టణంలో {category_display} ఇన్‌పుట్‌ల కోసం సమీప టోకు సరఫరాదారు",
                "ముడి పదార్థాల కోసం స్థానిక మండి లేదా వారపు సంత",
            ],
            "distributor_examples": [
                "గ్రామం/బ్లాక్ సంతలో ప్రత్యక్ష అమ్మకం",
                "సమీప పట్టణ టోకు/రిటైల్ నెట్‌వర్క్",
            ],
            "downside_risk_note": (
                f"{category_display} కోసం వర్గ-నిర్దిష్ట నిజమైన డేటాసెట్ అందుబాటులో లేనందున ఇది అనధికారిక "
                f"సూక్ష్మ-పరిశ్రమలకు సాధారణ, అధికారిక అఖిల-భారత సగటును ఉపయోగిస్తుంది - మీ నిజమైన ఫలితం "
                f"చాలా స్థానిక డిమాండ్‌ను బట్టి గణనీయంగా ఎక్కువ లేదా తక్కువ కావచ్చు. దీన్ని ప్రారంభ ప్రణాళిక "
                f"అంకెగా పరిగణించండి, హామీగా కాదు, మరియు మీ మొదటి 2-3 నెలల నిజమైన అమ్మకాల తర్వాత దీన్ని "
                f"సమీక్షించండి."
            ),
            "methodology": (
                f"MoSPI/NSO యొక్క అసంఘటిత రంగ సంస్థల వార్షిక సర్వే (ASUSE) 2022-23 అధికారిక సగటు "
                f"స్థూల ఉత్పత్తి విలువ (GVO) Rs. {annual_gvo:,}/సంవత్సరం ప్రతి అసంఘటిత-రంగ సంస్థను "
                f"ఉపయోగించే సాధారణ-ప్రయోజన ఫాల్‌బ్యాక్, ఎందుకంటే ఈ వ్యాపార రకానికి ఈ సాధనంలో ఇంకా "
                f"వర్గ-నిర్దిష్ట నిజమైన డేటాసెట్ లేదు."
            ),
        }
    return None


def revenue_reanchored_methodology(lang: str, current_monthly_revenue: float) -> Optional[str]:
    if lang == "hi":
        return (
            f"आपकी अपनी बताई गई वर्तमान मासिक आय Rs. {current_monthly_revenue:,.0f} पर आधारित, "
            f"महीने-दर-महीने बदलाव के लिए एक यथार्थवादी +/-15-25% सीमा के साथ, सामान्य जिला अनुमान के "
            f"बजाय - आपके अपने आंकड़े उपलब्ध सबसे सटीक इनपुट हैं।"
        )
    if lang == "kn":
        return (
            f"ನಿಮ್ಮ ಸ್ವಂತ ವರದಿ ಮಾಡಿದ ಪ್ರಸ್ತುತ ಮಾಸಿಕ ಆದಾಯ Rs. {current_monthly_revenue:,.0f} ಆಧಾರದ ಮೇಲೆ, "
            f"ತಿಂಗಳಿಂದ ತಿಂಗಳಿಗೆ ಬದಲಾವಣೆಗೆ ವಾಸ್ತವಿಕ +/-15-25% ವ್ಯಾಪ್ತಿಯೊಂದಿಗೆ, ಸಾಮಾನ್ಯ ಜಿಲ್ಲಾ ಅಂದಾಜಿನ "
            f"ಬದಲಿಗೆ - ನಿಮ್ಮ ಸ್ವಂತ ಅಂಕಿಅಂಶಗಳು ಲಭ್ಯವಿರುವ ಅತ್ಯಂತ ನಿಖರವಾದ ಇನ್‌ಪುಟ್ ಆಗಿವೆ."
        )
    if lang == "te":
        return (
            f"మీరు స్వయంగా నివేదించిన ప్రస్తుత నెలవారీ ఆదాయం Rs. {current_monthly_revenue:,.0f} ఆధారంగా, "
            f"నెలవారీ మార్పు కోసం వాస్తవిక +/-15-25% శ్రేణితో, సాధారణ జిల్లా అంచనాకు బదులుగా - మీ సొంత "
            f"సంఖ్యలే అందుబాటులో ఉన్న అత్యంత ఖచ్చితమైన ఇన్‌పుట్."
        )
    return None


# ── Scheme catalog text (schemes_catalog.py "every scheme you qualify for" list) ──
# Every field below mirrors the branch logic in schemes_catalog.py exactly, just
# translated - so an English reader and a Hindi/Kannada/Telugu reader are told the
# same eligibility facts, never a machine-untranslated leftover.

_PMEGP_AGENCY = {
    "hi": "KVIC / KVIB / ज़िला उद्योग केंद्र, बैंकों के माध्यम से",
    "kn": "KVIC / KVIB / ಜಿಲ್ಲಾ ಕೈಗಾರಿಕಾ ಕೇಂದ್ರ, ಬ್ಯಾಂಕುಗಳ ಮೂಲಕ",
    "te": "KVIC / KVIB / జిల్లా పరిశ్రమల కేంద్రం, బ్యాంకుల ద్వారా",
}
_UNIT_TYPE_WORD = {
    "hi": {"mfg": "निर्माण", "svc": "सेवा/व्यापार"},
    "kn": {"mfg": "ಉತ್ಪಾದನೆ", "svc": "ಸೇವೆ/ವ್ಯಾಪಾರ"},
    "te": {"mfg": "తయారీ", "svc": "సేవ/వ్యాపారం"},
}


def pmegp_texts(lang: str, project_cost: float, cap: float, is_manufacturing_like: bool, eligible: bool):
    if lang not in ("hi", "kn", "te"):
        return None
    unit_key = "mfg" if is_manufacturing_like else "svc"
    unit_word = _UNIT_TYPE_WORD[lang][unit_key]
    if lang == "hi":
        note = (
            f"Rs. {project_cost:,.0f} की परियोजना लागत PMEGP सीमा (इस प्रकार की इकाई — {unit_word} — के लिए "
            f"Rs. {cap:,.0f}) के भीतर है।"
            if eligible else
            f"Rs. {project_cost:,.0f} की परियोजना लागत इस प्रकार की इकाई ({unit_word}) के लिए PMEGP की "
            f"Rs. {cap:,.0f} सीमा से अधिक है।"
        )
        return dict(
            operating_agency=_PMEGP_AGENCY["hi"],
            eligibility_note=note,
            subsidy_or_margin_money_note=(
                "सरकारी सब्सिडी (ऋण नहीं) — ग्रामीण क्षेत्रों में परियोजना लागत का 25% "
                "(SC/ST/महिला/विशेष श्रेणियों के लिए 35%) — यह राशि कभी नहीं चुकानी होती। "
                "आवेदक को केवल 5% का योगदान करना होता है (शहरी क्षेत्रों में सामान्य श्रेणी के लिए 10%)।"
            ),
            interest_rate_percent_range="बैंक की मानक MSME दर, आमतौर पर 8-12% प्रति वर्ष",
            tenure_years="7 वर्ष तक (वित्तपोषण करने वाले बैंक द्वारा तय मोहलत अवधि सहित)",
            description=(
                "एक नई सूक्ष्म-इकाई स्थापित करने के लिए एकमुश्त सरकारी सब्सिडी योजना। एक सामान्य ऋण के "
                "विपरीत, परियोजना लागत का एक हिस्सा सब्सिडी है जिसे कभी नहीं चुकाना — इसलिए इतनी ही "
                "परियोजना राशि के लिए यह आमतौर पर सबसे कम मासिक किस्त बनाती है।"
            ),
        )
    if lang == "kn":
        note = (
            f"Rs. {project_cost:,.0f} ಯೋಜನಾ ವೆಚ್ಚವು PMEGP ಮಿತಿಯ (ಈ ರೀತಿಯ ಘಟಕಕ್ಕೆ — {unit_word} — "
            f"Rs. {cap:,.0f}) ಒಳಗೆ ಇದೆ."
            if eligible else
            f"Rs. {project_cost:,.0f} ಯೋಜನಾ ವೆಚ್ಚವು ಈ ರೀತಿಯ ಘಟಕಕ್ಕೆ ({unit_word}) PMEGP ಯ "
            f"Rs. {cap:,.0f} ಮಿತಿಯನ್ನು ಮೀರಿದೆ."
        )
        return dict(
            operating_agency=_PMEGP_AGENCY["kn"],
            eligibility_note=note,
            subsidy_or_margin_money_note=(
                "ಸರ್ಕಾರಿ ಸಬ್ಸಿಡಿ (ಸಾಲವಲ್ಲ) — ಗ್ರಾಮೀಣ ಪ್ರದೇಶಗಳಲ್ಲಿ ಯೋಜನಾ ವೆಚ್ಚದ 25% "
                "(SC/ST/ಮಹಿಳೆ/ವಿಶೇಷ ವರ್ಗಗಳಿಗೆ 35%) — ಈ ಭಾಗವನ್ನು ಎಂದಿಗೂ ಮರುಪಾವತಿಸಬೇಕಿಲ್ಲ. "
                "ಅರ್ಜಿದಾರರು ಕೇವಲ 5% ಕೊಡುಗೆ ನೀಡಬೇಕು (ನಗರ ಪ್ರದೇಶಗಳಲ್ಲಿ ಸಾಮಾನ್ಯ ವರ್ಗಕ್ಕೆ 10%)."
            ),
            interest_rate_percent_range="ಬ್ಯಾಂಕಿನ ಪ್ರಮಾಣಿತ MSME ದರ, ಸಾಮಾನ್ಯವಾಗಿ ವಾರ್ಷಿಕ 8-12%",
            tenure_years="7 ವರ್ಷಗಳವರೆಗೆ (ಸಾಲ ನೀಡುವ ಬ್ಯಾಂಕ್ ನಿಗದಿಪಡಿಸಿದ ಮೊರಟೋರಿಯಂ ಅವಧಿ ಸೇರಿ)",
            description=(
                "ಹೊಸ ಸೂಕ್ಷ್ಮ-ಉದ್ಯಮವನ್ನು ಸ್ಥಾಪಿಸಲು ಒಂದು ಬಾರಿಯ ಸರ್ಕಾರಿ ಸಬ್ಸಿಡಿ ಯೋಜನೆ. ಸಾಮಾನ್ಯ ಸಾಲಕ್ಕಿಂತ "
                "ಭಿನ್ನವಾಗಿ, ಯೋಜನಾ ವೆಚ್ಚದ ಒಂದು ಭಾಗ ಸಬ್ಸಿಡಿಯಾಗಿದ್ದು ಎಂದಿಗೂ ಮರುಪಾವತಿಸಬೇಕಿಲ್ಲ — ಇದೇ ಗಾತ್ರದ "
                "ಯೋಜನೆಗೆ ಇದು ಸಾಮಾನ್ಯವಾಗಿ ಅತ್ಯಂತ ಕಡಿಮೆ ಮಾಸಿಕ ಕಂತನ್ನು ಉಂಟುಮಾಡುತ್ತದೆ."
            ),
        )
    note = (
        f"Rs. {project_cost:,.0f} ప్రాజెక్ట్ వ్యయం PMEGP పరిమితి (ఈ రకమైన యూనిట్‌కు — {unit_word} — "
        f"Rs. {cap:,.0f}) లోపల ఉంది."
        if eligible else
        f"Rs. {project_cost:,.0f} ప్రాజెక్ట్ వ్యయం ఈ రకమైన యూనిట్‌కు ({unit_word}) PMEGP యొక్క "
        f"Rs. {cap:,.0f} పరిమితిని మించింది."
    )
    return dict(
        operating_agency=_PMEGP_AGENCY["te"],
        eligibility_note=note,
        subsidy_or_margin_money_note=(
            "ప్రభుత్వ సబ్సిడీ (రుణం కాదు) — గ్రామీణ ప్రాంతాల్లో ప్రాజెక్ట్ వ్యయంలో 25% "
            "(SC/ST/మహిళలు/ప్రత్యేక వర్గాలకు 35%) — ఈ మొత్తాన్ని తిరిగి చెల్లించాల్సిన అవసరం లేదు. "
            "దరఖాస్తుదారు కేవలం 5% వాటా చెల్లించాలి (పట్టణ ప్రాంతాల్లో సాధారణ వర్గానికి 10%)."
        ),
        interest_rate_percent_range="బ్యాంకు ప్రామాణిక MSME రేటు, సాధారణంగా వార్షికంగా 8-12%",
        tenure_years="7 సంవత్సరాల వరకు (రుణమిచ్చే బ్యాంకు నిర్ణయించిన మారటోరియం వ్యవధితో సహా)",
        description=(
            "కొత్త సూక్ష్మ-పరిశ్రమను స్థాపించడానికి ఒకసారి ఇచ్చే ప్రభుత్వ సబ్సిడీ పథకం. సాధారణ రుణానికి "
            "భిన్నంగా, ప్రాజెక్ట్ వ్యయంలో కొంత భాగం సబ్సిడీ, దీన్ని తిరిగి చెల్లించాల్సిన అవసరం లేదు — అందుకే "
            "ఇదే పరిమాణ ప్రాజెక్టుకు సాధారణంగా అతి తక్కువ నెలవారీ వాయిదాను కలిగిస్తుంది."
        ),
    )


_MUDRA_AGENCY = {
    "hi": "कोई भी बैंक / NBFC / MFI (प्रधानमंत्री मुद्रा योजना)",
    "kn": "ಯಾವುದೇ ಬ್ಯಾಂಕ್ / NBFC / MFI (ಪ್ರಧಾನ ಮಂತ್ರಿ ಮುದ್ರಾ ಯೋಜನೆ)",
    "te": "ఏదైనా బ్యాంకు / NBFC / MFI (ప్రధాన మంత్రి ముద్రా యోజన)",
}


def mudra_texts(lang: str, project_cost: float, cap: float, tier: str, eligible: bool):
    if lang not in ("hi", "kn", "te"):
        return None
    if lang == "hi":
        note = (
            f"Rs. {project_cost:,.0f} की परियोजना लागत MUDRA की '{tier}' श्रेणी में आती है।"
            if eligible else
            f"Rs. {project_cost:,.0f} की परियोजना लागत MUDRA की Rs. {cap:,.0f} सीमा से अधिक है।"
        )
        return dict(
            operating_agency=_MUDRA_AGENCY["hi"],
            eligibility_note=note,
            subsidy_or_margin_money_note="कोई सब्सिडी नहीं — यह बिना गारंटी वाला ऋण है, अनुदान नहीं।",
            interest_rate_percent_range="~8.5%-12% प्रति वर्ष (ऋणदाता बैंक/NBFC और आवेदक प्रोफ़ाइल पर निर्भर)",
            tenure_years="5 वर्ष तक (ऋणदाता के अनुसार भिन्न)",
            description=(
                "लगभग किसी भी बैंक या NBFC शाखा से उपलब्ध बिना गारंटी वाला व्यवसाय ऋण — किसी विशेष "
                "राज्य एजेंसी के माध्यम से जाने की ज़रूरत नहीं, जिससे आमतौर पर एक निर्धारित चैनलाइज़िंग "
                "एजेंसी की तुलना में तेज़ प्रक्रिया होती है।"
            ),
        )
    if lang == "kn":
        note = (
            f"Rs. {project_cost:,.0f} ಯೋಜನಾ ವೆಚ್ಚವು MUDRA ಯ '{tier}' ಶ್ರೇಣಿಗೆ ಸೇರುತ್ತದೆ."
            if eligible else
            f"Rs. {project_cost:,.0f} ಯೋಜನಾ ವೆಚ್ಚವು MUDRA ಯ Rs. {cap:,.0f} ಮಿತಿಯನ್ನು ಮೀರಿದೆ."
        )
        return dict(
            operating_agency=_MUDRA_AGENCY["kn"],
            eligibility_note=note,
            subsidy_or_margin_money_note="ಯಾವುದೇ ಸಬ್ಸಿಡಿ ಇಲ್ಲ — ಇದು ಆಧಾರರಹಿತ ಸಾಲ, ಅನುದಾನವಲ್ಲ.",
            interest_rate_percent_range="~8.5%-12% ವಾರ್ಷಿಕ (ಸಾಲ ನೀಡುವ ಬ್ಯಾಂಕ್/NBFC ಮತ್ತು ಅರ್ಜಿದಾರರ ಪ್ರೊಫೈಲ್ ಅನುಸಾರ ಬದಲಾಗುತ್ತದೆ)",
            tenure_years="5 ವರ್ಷಗಳವರೆಗೆ (ಸಾಲದಾತರ ಅನುಸಾರ ಬದಲಾಗುತ್ತದೆ)",
            description=(
                "ಬಹುತೇಕ ಯಾವುದೇ ಬ್ಯಾಂಕ್ ಅಥವಾ NBFC ಶಾಖೆಯಿಂದ ಲಭ್ಯವಿರುವ ಆಧಾರರಹಿತ ವ್ಯಾಪಾರ ಸಾಲ — ನಿರ್ದಿಷ್ಟ "
                "ರಾಜ್ಯ ಏಜೆನ್ಸಿಯ ಮೂಲಕ ಹೋಗುವ ಅಗತ್ಯವಿಲ್ಲ, ಇದರಿಂದ ಸಾಮಾನ್ಯವಾಗಿ ನಿಗದಿತ ಚಾನೆಲೈಸಿಂಗ್ ಏಜೆನ್ಸಿಗಿಂತ "
                "ವೇಗದ ಪ್ರಕ್ರಿಯೆ ಸಿಗುತ್ತದೆ."
            ),
        )
    note = (
        f"Rs. {project_cost:,.0f} ప్రాజెక్ట్ వ్యయం MUDRA యొక్క '{tier}' శ్రేణిలోకి వస్తుంది."
        if eligible else
        f"Rs. {project_cost:,.0f} ప్రాజెక్ట్ వ్యయం MUDRA యొక్క Rs. {cap:,.0f} పరిమితిని మించింది."
    )
    return dict(
        operating_agency=_MUDRA_AGENCY["te"],
        eligibility_note=note,
        subsidy_or_margin_money_note="సబ్సిడీ ఏమీ లేదు — ఇది హామీ లేని రుణం, గ్రాంట్ కాదు.",
        interest_rate_percent_range="~8.5%-12% వార్షికంగా (రుణమిచ్చే బ్యాంకు/NBFC మరియు దరఖాస్తుదారు ప్రొఫైల్‌ను బట్టి మారుతుంది)",
        tenure_years="5 సంవత్సరాల వరకు (రుణదాతను బట్టి మారుతుంది)",
        description=(
            "దాదాపు ఏ బ్యాంకు లేదా NBFC శాఖ నుండైనా లభించే హామీ లేని వ్యాపార రుణం — ప్రత్యేక రాష్ట్ర "
            "ఏజెన్సీ ద్వారా వెళ్ళాల్సిన అవసరం లేదు, దీనివల్ల సాధారణంగా నిర్దేశిత ఛానలైజింగ్ ఏజెన్సీ కంటే "
            "వేగవంతమైన ప్రాసెసింగ్ లభిస్తుంది."
        ),
    )


_STANDUP_AGENCY = {
    "hi": "अनुसूचित वाणिज्यिक बैंक शाखाएं, SIDBI/DFS के माध्यम से",
    "kn": "ಅನುಸೂಚಿತ ವಾಣಿಜ್ಯ ಬ್ಯಾಂಕ್ ಶಾಖೆಗಳು, SIDBI/DFS ಮೂಲಕ",
    "te": "షెడ్యూల్డ్ కమర్షియల్ బ్యాంక్ శాఖలు, SIDBI/DFS ద్వారా",
}


def standup_india_texts(
    lang: str, project_cost: float, cap: float, floor: float,
    size_ok: bool, category_ok: bool, first_time: bool, eligible: bool,
):
    if lang not in ("hi", "kn", "te"):
        return None
    if lang == "hi":
        if not size_ok:
            band_note = "इस सीमा से नीचे है (ऊपर दी गई छोटी योजनाएं बेहतर उपयुक्त हैं)" if project_cost < floor else "इस सीमा से ऊपर है"
            note = f"स्टैंड-अप इंडिया Rs. {floor:,.0f} से Rs. {cap:,.0f} तक की परियोजना लागत को कवर करता है — आपकी Rs. {project_cost:,.0f} की परियोजना {band_note}।"
        elif not category_ok:
            note = (
                "यह योजना नई (ग्रीनफील्ड) इकाई स्थापित करने वाली महिला उद्यमियों और SC/ST उद्यमियों के लिए "
                "आरक्षित है। दी गई प्रोफ़ाइल जानकारी के आधार पर यह मेल नहीं खाया — यदि आप SC/ST श्रेणी से "
                "हैं, तो भी आप पात्र हो सकते हैं, भले ही यह टूल अभी वह जानकारी एकत्र नहीं करता।"
            )
        elif not first_time:
            note = "स्टैंड-अप इंडिया केवल एक नई (ग्रीनफील्ड), पहली बार शुरू की जा रही इकाई के लिए है।"
        else:
            note = (
                f"Rs. {project_cost:,.0f} की परियोजना लागत Rs. {floor:,.0f}–{cap:,.0f} की स्टैंड-अप इंडिया "
                f"सीमा के भीतर है, एक पहली बार उद्यम शुरू कर रही महिला उद्यमी के लिए।"
            )
        return dict(
            operating_agency=_STANDUP_AGENCY["hi"],
            eligibility_note=note,
            subsidy_or_margin_money_note="कोई सब्सिडी नहीं; कन्वर्जेंस सहायता के साथ मार्जिन मनी योगदान न्यूनतम 10% तक हो सकता है।",
            interest_rate_percent_range="बैंक की आधार दर + 3% तक (बैंक के अनुसार भिन्न)",
            tenure_years="7 वर्ष तक, 18 महीने तक की मोहलत सहित",
            description=(
                "एक बड़ी राशि की योजना (Rs. 10 लाख–1 करोड़) विशेष रूप से महिलाओं और SC/ST उद्यमियों के लिए "
                "जो बिल्कुल नई इकाई शुरू कर रहे हैं — यह तब प्रासंगिक है जब आपकी परियोजना ऊपर दी गई छोटी "
                "योजनाओं से आगे बढ़ जाती है।"
            ),
        )
    if lang == "kn":
        if not size_ok:
            band_note = "ಈ ಮಿತಿಗಿಂತ ಕಡಿಮೆ (ಮೇಲಿನ ಸಣ್ಣ ಯೋಜನೆಗಳು ಉತ್ತಮ ಹೊಂದಾಣಿಕೆ)" if project_cost < floor else "ಈ ಮಿತಿಗಿಂತ ಹೆಚ್ಚು"
            note = f"ಸ್ಟ್ಯಾಂಡ್-ಅಪ್ ಇಂಡಿಯಾ Rs. {floor:,.0f} ರಿಂದ Rs. {cap:,.0f} ವರೆಗಿನ ಯೋಜನಾ ವೆಚ್ಚವನ್ನು ಒಳಗೊಳ್ಳುತ್ತದೆ — ನಿಮ್ಮ Rs. {project_cost:,.0f} ಯೋಜನೆ {band_note}."
        elif not category_ok:
            note = (
                "ಇದು ಹೊಸ (ಗ್ರೀನ್‌ಫೀಲ್ಡ್) ಉದ್ಯಮ ಸ್ಥಾಪಿಸುವ ಮಹಿಳಾ ಉದ್ಯಮಿಗಳು ಮತ್ತು SC/ST ಉದ್ಯಮಿಗಳಿಗೆ "
                "ಮೀಸಲಾಗಿದೆ. ನೀಡಿದ ಪ್ರೊಫೈಲ್ ಮಾಹಿತಿಯ ಆಧಾರದ ಮೇಲೆ ಇದು ಹೊಂದಾಣಿಕೆಯಾಗಲಿಲ್ಲ — ನೀವು SC/ST "
                "ವರ್ಗಕ್ಕೆ ಸೇರಿದ್ದರೆ, ಈ ಟೂಲ್ ಆ ಮಾಹಿತಿಯನ್ನು ಇನ್ನೂ ಸಂಗ್ರಹಿಸದಿದ್ದರೂ ನೀವು ಅರ್ಹರಾಗಿರಬಹುದು."
            )
        elif not first_time:
            note = "ಸ್ಟ್ಯಾಂಡ್-ಅಪ್ ಇಂಡಿಯಾ ಕೇವಲ ಹೊಸ (ಗ್ರೀನ್‌ಫೀಲ್ಡ್), ಮೊದಲ ಬಾರಿಗೆ ಪ್ರಾರಂಭಿಸುವ ಉದ್ಯಮಕ್ಕೆ ಮಾತ್ರ."
        else:
            note = (
                f"Rs. {project_cost:,.0f} ಯೋಜನಾ ವೆಚ್ಚವು Rs. {floor:,.0f}–{cap:,.0f} ಸ್ಟ್ಯಾಂಡ್-ಅಪ್ ಇಂಡಿಯಾ "
                f"ವ್ಯಾಪ್ತಿಯೊಳಗೆ ಇದೆ, ಮೊದಲ ಬಾರಿಗೆ ಉದ್ಯಮ ಆರಂಭಿಸುತ್ತಿರುವ ಮಹಿಳಾ ಉದ್ಯಮಿಗೆ."
            )
        return dict(
            operating_agency=_STANDUP_AGENCY["kn"],
            eligibility_note=note,
            subsidy_or_margin_money_note="ಯಾವುದೇ ಸಬ್ಸಿಡಿ ಇಲ್ಲ; ಕನ್ವರ್ಜೆನ್ಸ್ ಬೆಂಬಲದೊಂದಿಗೆ ಮಾರ್ಜಿನ್ ಮನಿ ಕೊಡುಗೆ ಕನಿಷ್ಠ 10% ಆಗಿರಬಹುದು.",
            interest_rate_percent_range="ಬ್ಯಾಂಕಿನ ಬೇಸ್ ದರ + 3% ವರೆಗೆ (ಬ್ಯಾಂಕ್ ಅನುಸಾರ ಬದಲಾಗುತ್ತದೆ)",
            tenure_years="7 ವರ್ಷಗಳವರೆಗೆ, 18 ತಿಂಗಳವರೆಗಿನ ಮೊರಟೋರಿಯಂ ಸೇರಿ",
            description=(
                "ಹೊಸದಾಗಿ ಉದ್ಯಮ ಆರಂಭಿಸುತ್ತಿರುವ ಮಹಿಳೆಯರು ಮತ್ತು SC/ST ಉದ್ಯಮಿಗಳಿಗೆ ವಿಶೇಷವಾದ ದೊಡ್ಡ ಮೊತ್ತದ "
                "ಯೋಜನೆ (Rs. 10 ಲಕ್ಷ–1 ಕೋಟಿ) — ನಿಮ್ಮ ಯೋಜನೆ ಮೇಲಿನ ಸಣ್ಣ ಯೋಜನೆಗಳನ್ನು ಮೀರಿ ಬೆಳೆದಾಗ ಇದು "
                "ಪ್ರಸ್ತುತವಾಗುತ್ತದೆ."
            ),
        )
    if not size_ok:
        band_note = "ఈ పరిమితి కంటే తక్కువ (పైన ఉన్న చిన్న పథకాలు మెరుగ్గా సరిపోతాయి)" if project_cost < floor else "ఈ పరిమితి కంటే ఎక్కువ"
        note = f"స్టాండ్-అప్ ఇండియా Rs. {floor:,.0f} నుండి Rs. {cap:,.0f} వరకు ప్రాజెక్ట్ వ్యయాన్ని కవర్ చేస్తుంది — మీ Rs. {project_cost:,.0f} ప్రాజెక్ట్ {band_note}."
    elif not category_ok:
        note = (
            "ఇది కొత్త (గ్రీన్‌ఫీల్డ్) సంస్థను స్థాపిస్తున్న మహిళా వ్యాపారవేత్తలు మరియు SC/ST వ్యాపారవేత్తల "
            "కోసం రిజర్వ్ చేయబడింది. ఇచ్చిన ప్రొఫైల్ వివరాల ఆధారంగా ఇది సరిపోలలేదు — మీరు SC/ST వర్గానికి "
            "చెందినవారైతే, ఈ టూల్ ఆ వివరాన్ని ఇంకా సేకరించకపోయినా మీరు అర్హులు కావచ్చు."
        )
    elif not first_time:
        note = "స్టాండ్-అప్ ఇండియా కేవలం కొత్త (గ్రీన్‌ఫీల్డ్), మొదటిసారి ప్రారంభించే సంస్థ కోసం మాత్రమే."
    else:
        note = (
            f"Rs. {project_cost:,.0f} ప్రాజెక్ట్ వ్యయం Rs. {floor:,.0f}–{cap:,.0f} స్టాండ్-అప్ ఇండియా "
            f"పరిధిలో ఉంది, మొదటిసారి సంస్థను ప్రారంభిస్తున్న మహిళా వ్యాపారవేత్త కోసం."
        )
    return dict(
        operating_agency=_STANDUP_AGENCY["te"],
        eligibility_note=note,
        subsidy_or_margin_money_note="సబ్సిడీ లేదు; కన్వర్జెన్స్ మద్దతుతో మార్జిన్ మనీ వాటా కనిష్టంగా 10% వరకు ఉండవచ్చు.",
        interest_rate_percent_range="బ్యాంకు బేస్ రేటు + 3% వరకు (బ్యాంకును బట్టి మారుతుంది)",
        tenure_years="7 సంవత్సరాల వరకు, 18 నెలల వరకు మారటోరియంతో సహా",
        description=(
            "కొత్తగా సంస్థను ప్రారంభిస్తున్న మహిళలు మరియు SC/ST వ్యాపారవేత్తల కోసం ప్రత్యేకమైన పెద్ద మొత్తపు "
            "పథకం (Rs. 10 లక్షలు–1 కోటి) — మీ ప్రాజెక్ట్ పైన ఉన్న చిన్న పథకాలను మించి పెరిగినప్పుడు ఇది "
            "ఉపయోగపడుతుంది."
        ),
    )


_NSFDC_AGENCY = {
    "hi": "NSFDC (राष्ट्रीय अनुसूचित जाति वित्त एवं विकास निगम), राज्य चैनलाइज़िंग एजेंसियों के माध्यम से",
    "kn": "NSFDC (ರಾಷ್ಟ್ರೀಯ ಪರಿಶಿಷ್ಟ ಜಾತಿ ಹಣಕಾಸು ಮತ್ತು ಅಭಿವೃದ್ಧಿ ನಿಗಮ), ರಾಜ್ಯ ಚಾನೆಲೈಸಿಂಗ್ ಏಜೆನ್ಸಿಗಳ ಮೂಲಕ",
    "te": "NSFDC (జాతీయ షెడ్యూల్డ్ కులాల ఆర్థిక మరియు అభివృద్ధి సంస్థ), రాష్ట్ర ఛానలైజింగ్ ఏజెన్సీల ద్వారా",
}
_NSFDC_DESCRIPTION = {
    "hi": "यह टूल जिस मुख्य योजना के लिए विस्तृत EMI शेड्यूल तैयार करता है — सटीक चुकौती आंकड़ों के लिए ऊपर दिया गया वित्तीय योजना अनुभाग देखें।",
    "kn": "ಈ ಟೂಲ್ ನಿಮ್ಮ ವಿವರವಾದ EMI ವೇಳಾಪಟ್ಟಿಯನ್ನು ರೂಪಿಸುವ ಪ್ರಾಥಮಿಕ ಯೋಜನೆ — ನಿಖರ ಮರುಪಾವತಿ ಅಂಕಿಅಂಶಗಳಿಗಾಗಿ ಮೇಲಿನ ಆರ್ಥಿಕ ಯೋಜನೆ ವಿಭಾಗವನ್ನು ನೋಡಿ.",
    "te": "ఈ టూల్ మీ వివరణాత్మక EMI షెడ్యూల్‌ను రూపొందించే ప్రధాన పథకం — ఖచ్చితమైన తిరిగి చెల్లింపు గణాంకాల కోసం పైన ఉన్న ఆర్థిక ప్రణాళిక విభాగాన్ని చూడండి.",
}
_NSFDC_MARGIN_NOTE = {
    "hi": "कोई सब्सिडी नहीं; मानक 90% ऋण / 10% मार्जिन-मनी संरचना।",
    "kn": "ಯಾವುದೇ ಸಬ್ಸಿಡಿ ಇಲ್ಲ; ಪ್ರಮಾಣಿತ 90% ಸಾಲ / 10% ಮಾರ್ಜಿನ್-ಮನಿ ರಚನೆ.",
    "te": "సబ్సిడీ లేదు; ప్రామాణిక 90% రుణం / 10% మార్జిన్-మనీ నిర్మాణం.",
}
_NSFDC_RATE_SUFFIX = {
    "hi": "% प्रति वर्ष (रियायती, स्थिर)",
    "kn": "% ವಾರ್ಷಿಕ (ರಿಯಾಯಿತಿ, ಸ್ಥಿರ)",
    "te": "% వార్షికంగా (రాయితీతో, స్థిరమైన)",
}


def nsfdc_option_texts(lang: str, project_cost: float, cap: float, eligible: bool, rate: str, tenure: str):
    if lang not in ("hi", "kn", "te"):
        return None
    if lang == "hi":
        note = (
            f"Rs. {project_cost:,.0f} की परियोजना लागत इस श्रेणी की सीमा में आती है।"
            if eligible else
            f"यह श्रेणी Rs. {cap:,.0f} तक की परियोजना लागत को कवर करती है; आपकी परियोजना इस सीमा से बाहर है।"
        )
    elif lang == "kn":
        note = (
            f"Rs. {project_cost:,.0f} ಯೋಜನಾ ವೆಚ್ಚವು ಈ ಶ್ರೇಣಿಯ ವ್ಯಾಪ್ತಿಯಲ್ಲಿ ಬರುತ್ತದೆ."
            if eligible else
            f"ಈ ಶ್ರೇಣಿಯು Rs. {cap:,.0f} ವರೆಗಿನ ಯೋಜನಾ ವೆಚ್ಚವನ್ನು ಒಳಗೊಳ್ಳುತ್ತದೆ; ನಿಮ್ಮ ಯೋಜನೆ ಈ ವ್ಯಾಪ್ತಿಯ ಹೊರಗಿದೆ."
        )
    else:
        note = (
            f"Rs. {project_cost:,.0f} ప్రాజెక్ట్ వ్యయం ఈ శ్రేణి పరిధిలోకి వస్తుంది."
            if eligible else
            f"ఈ శ్రేణి Rs. {cap:,.0f} వరకు ప్రాజెక్ట్ వ్యయాన్ని కవర్ చేస్తుంది; మీ ప్రాజెక్ట్ ఈ పరిధికి వెలుపల ఉంది."
        )
    return dict(
        operating_agency=_NSFDC_AGENCY[lang],
        eligibility_note=note,
        subsidy_or_margin_money_note=_NSFDC_MARGIN_NOTE[lang],
        interest_rate_percent_range=f"{rate}{_NSFDC_RATE_SUFFIX[lang]}",
        description=_NSFDC_DESCRIPTION[lang],
    )


_QUARTER_WORD = {"hi": "तिमाही", "kn": "ತ್ರೈಮಾಸಿಕ", "te": "త్రైమాసికం"}
_MORATORIUM_SUFFIX = {
    "hi": " (मोहलत — कोई भुगतान देय नहीं)",
    "kn": " (ಮೊರಟೋರಿಯಂ — ಯಾವುದೇ ಪಾವತಿ ಬಾಕಿ ಇಲ್ಲ)",
    "te": " (మారటోరియం — చెల్లింపు లేదు)",
}


def quarter_label(lang: str, quarter_number: int, is_moratorium: bool = False) -> Optional[str]:
    if lang not in ("hi", "kn", "te"):
        return None
    label = f"{_QUARTER_WORD[lang]} {quarter_number}"
    if is_moratorium:
        label += _MORATORIUM_SUFFIX[lang]
    return label


# ── Idea suggester ("describe your idea" reverse-flow reply) ──────────────
def idea_suggestion_no_match(lang: str) -> Optional[str]:
    if lang == "hi":
        return (
            "हम आपके विचार को हमारी मानक श्रेणियों में से किसी एक से आत्मविश्वास के साथ मेल नहीं खा सके - "
            "हमने इसे 'अन्य' के रूप में सेट किया है ताकि आप इसे स्वयं बता सकें। अगर सूची में से कोई और "
            "श्रेणी बेहतर लगे, तो बेझिझक उसे चुनें।"
        )
    if lang == "kn":
        return (
            "ನಿಮ್ಮ ಆಲೋಚನೆಯನ್ನು ನಮ್ಮ ಪ್ರಮಾಣಿತ ವರ್ಗಗಳಲ್ಲಿ ಒಂದಕ್ಕೆ ಬಳಸಿದ ಪದಗಳಿಂದ ವಿಶ್ವಾಸಾರ್ಹವಾಗಿ ಹೊಂದಿಸಲು "
            "ಸಾಧ್ಯವಾಗಲಿಲ್ಲ - ನೀವೇ ವಿವರಿಸಬಹುದೆಂದು ಇದನ್ನು 'ಇತರೆ' ಎಂದು ಹೊಂದಿಸಿದ್ದೇವೆ. ಪಟ್ಟಿಯಿಂದ ಇನ್ನೊಂದು "
            "ವರ್ಗ ಹೆಚ್ಚು ಸೂಕ್ತವೆನಿಸಿದರೆ, ಬೇಕಾದರೆ ಅದನ್ನು ಆಯ್ಕೆ ಮಾಡಿ."
        )
    if lang == "te":
        return (
            "మీ ఆలోచనను మా ప్రామాణిక వర్గాలలో ఒకదానికి ఉపయోగించిన పదాల ఆధారంగా నమ్మకంగా సరిపోల్చలేకపోయాము - "
            "మీరే వివరించుకోగలిగేలా దీన్ని 'ఇతర' గా సెట్ చేసాము. జాబితా నుండి మరొక వర్గం బాగా సరిపోతుందని "
            "అనిపిస్తే, నిరభ్యంతరంగా దాన్ని ఎంచుకోండి."
        )
    return None


def idea_suggestion_matched(lang: str, matched_keywords: List[str], category_display: str, margin: float) -> Optional[str]:
    if lang not in ("hi", "kn", "te"):
        return None
    words = ", ".join(matched_keywords)
    if lang == "hi":
        return (
            f"आपके विवरण में '{words}' शब्दों के आधार पर, यह एक {category_display} व्यवसाय जैसा लगता है। "
            f"अगर आपके पास लगाने के लिए पहले से कुछ बचत है, तो उसे दर्ज करें - अन्यथा इस पैमाने के "
            f"{category_display} व्यवसाय के लिए शुरुआत करने हेतु Rs. {margin:,.0f} एक यथार्थवादी राशि है।"
        )
    if lang == "kn":
        return (
            f"ನಿಮ್ಮ ವಿವರಣೆಯಲ್ಲಿನ '{words}' ಪದಗಳ ಆಧಾರದ ಮೇಲೆ, ಇದು {category_display} ವ್ಯಾಪಾರದಂತೆ ಕಾಣುತ್ತದೆ. "
            f"ಹೂಡಿಕೆ ಮಾಡಲು ನಿಮ್ಮ ಬಳಿ ಈಗಾಗಲೇ ಸ್ವಲ್ಪ ಉಳಿತಾಯವಿದ್ದರೆ, ಅದನ್ನು ನಮೂದಿಸಿ - ಇಲ್ಲದಿದ್ದರೆ ಈ "
            f"ಪ್ರಮಾಣದ {category_display} ವ್ಯಾಪಾರವನ್ನು ಪ್ರಾರಂಭಿಸಲು Rs. {margin:,.0f} ಒಂದು ವಾಸ್ತವಿಕ ಮೊತ್ತ."
        )
    return (
        f"మీ వివరణలోని '{words}' పదాల ఆధారంగా, ఇది {category_display} వ్యాపారంలా కనిపిస్తుంది. "
        f"పెట్టుబడి పెట్టడానికి మీ వద్ద ఇప్పటికే కొంత పొదుపు ఉంటే, దాన్ని నమోదు చేయండి - లేకపోతే ఈ "
        f"స్థాయి {category_display} వ్యాపారాన్ని ప్రారంభించడానికి Rs. {margin:,.0f} ఒక వాస్తవిక మొత్తం."
    )


_SCHEME_HINT = {
    "micro": {
        "hi": "संभवतः NSFDC माइक्रो फाइनेंस स्कीम (परियोजना लागत Rs. 1.40 लाख से कम)",
        "kn": "ಸಂಭಾವ್ಯವಾಗಿ NSFDC ಮೈಕ್ರೋ ಫೈನಾನ್ಸ್ ಯೋಜನೆ (ಯೋಜನಾ ವೆಚ್ಚ Rs. 1.40 ಲಕ್ಷಕ್ಕಿಂತ ಕಡಿಮೆ)",
        "te": "బహుశా NSFDC మైక్రో ఫైనాన్స్ పథకం (ప్రాజెక్ట్ వ్యయం Rs. 1.40 లక్షల కంటే తక్కువ)",
    },
    "suvidha": {
        "hi": "संभवतः NSFDC SUVIDHA लोन स्कीम (परियोजना लागत Rs. 1.40-10 लाख)",
        "kn": "ಸಂಭಾವ್ಯವಾಗಿ NSFDC SUVIDHA ಸಾಲ ಯೋಜನೆ (ಯೋಜನಾ ವೆಚ್ಚ Rs. 1.40-10 ಲಕ್ಷ)",
        "te": "బహుశా NSFDC SUVIDHA లోన్ పథకం (ప్రాజెక్ట్ వ్యయం Rs. 1.40-10 లక్షలు)",
    },
    "utkarsh": {
        "hi": "संभवतः NSFDC UTKARSH लोन स्कीम (परियोजना लागत Rs. 10-50 लाख), या PMEGP/MUDRA",
        "kn": "ಸಂಭಾವ್ಯವಾಗಿ NSFDC UTKARSH ಸಾಲ ಯೋಜನೆ (ಯೋಜನಾ ವೆಚ್ಚ Rs. 10-50 ಲಕ್ಷ), ಅಥವಾ PMEGP/MUDRA",
        "te": "బహుశా NSFDC UTKARSH లోన్ పథకం (ప్రాజెక్ట్ వ్యయం Rs. 10-50 లక్షలు), లేదా PMEGP/MUDRA",
    },
    "above": {
        "hi": "संभवतः PMEGP, MUDRA, या स्टैंड-अप इंडिया (परियोजना लागत NSFDC की Rs. 50 लाख सीमा से अधिक)",
        "kn": "ಸಂಭಾವ್ಯವಾಗಿ PMEGP, MUDRA, ಅಥವಾ ಸ್ಟ್ಯಾಂಡ್-ಅಪ್ ಇಂಡಿಯಾ (ಯೋಜನಾ ವೆಚ್ಚ NSFDC ಯ Rs. 50 ಲಕ್ಷ ಮಿತಿಗಿಂತ ಹೆಚ್ಚು)",
        "te": "బహుశా PMEGP, MUDRA, లేదా స్టాండ్-అప్ ఇండియా (ప్రాజెక్ట్ వ్యయం NSFDC యొక్క Rs. 50 లక్షల పరిమితిని మించి)",
    },
}


def likely_scheme_hint(lang: str, tier_key: str) -> Optional[str]:
    if lang not in ("hi", "kn", "te"):
        return None
    return _SCHEME_HINT[tier_key][lang]
