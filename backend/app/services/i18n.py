"""
Lightweight, deterministic language support for the AI's narrative text.

The report's narrative (narrative_summary, next steps, scheme explanation,
flowchart, disclaimer) is generated from Python string templates, not an
LLM call - so rather than bolt on an external translation API (none is
configured in this project, and a live translation call would be one more
thing that can silently fail during a demo), each supported language gets
its own parallel template function here. English and Hindi are fully
supported; any other `language` code currently falls back to English with
no error, so the UI/API never breaks for an unsupported code.

Hindi text below intentionally mixes Devanagari with a few widely-understood
English/financial terms (like "EMI", "loan", scheme names) exactly the way
real rural Hindi-medium government and bank communication does - a fully
"pure" Hindi translation of financial terms would actually be less
understandable to the target audience, not more.
"""
from typing import Dict, List

SUPPORTED_LANGUAGES = ["en", "hi"]


def normalize_language(language: str) -> str:
    lang = (language or "en").strip().lower()
    return lang if lang in SUPPORTED_LANGUAGES else "en"


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
}


def scheme_explanation(
    lang: str, project_cost: float, band_desc_en: str, band_desc_hi: str,
    scheme_value: str, rate: float, tenure_years: int, moratorium_months: int,
    verified_on: str,
) -> str:
    if lang == "hi":
        return (
            f"आपकी परियोजना लागत Rs. {project_cost:,.0f} है, जो {band_desc_hi} में आती है, "
            f"इसलिए आप {scheme_value} के लिए पात्र हैं - ब्याज दर {rate}% प्रति वर्ष, "
            f"चुकौती अवधि {tenure_years} वर्ष (जिसमें {moratorium_months} महीने की मोहलत/मोरेटोरियम शामिल है)। "
            f"ये शर्तें NSFDC की आधिकारिक वेबसाइट से {verified_on} को सत्यापित की गई हैं - "
            f"स्रोत लिंक इसी योजना के साथ दिया गया है।"
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
) -> str:
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
            f"जिनका घनत्व '{density}' है। "
            f"जिले की साक्षरता दर ({lit_pct}%) और मोबाइल पहुंच ({mobile_pct}%) दिखाती हैं कि यह बाजार "
            f"धीरे-धीरे औपचारिक लेन-देन की ओर बढ़ रहा है। "
            f"सुझाई गई बिक्री कीमत: Rs. {price_min}-{price_max} {unit} (स्रोत: Agmarknet वास्तविक डेटा)।"
        )
    return None  # caller keeps its existing detailed English builder


NEXT_STEPS_HEADER = {
    "en": "Actionable next steps",
    "hi": "अगले जरूरी कदम",
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
