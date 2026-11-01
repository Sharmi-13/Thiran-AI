"""Canned response library for the Thiran AI mock model.

Pure data, no SDK imports. ``MockModel`` reads from this module to produce
deterministic, language-aware responses for three intents:

* ``question``   - an interview question from the Interviewer agent
* ``evaluation`` - feedback on an answer from the Evaluator agent
* ``coaching``   - improvement tips plus an improved professional English
  sample answer, from the Coach agent

Lookup shape::

    RESPONSES[intent][category][difficulty][language] -> str

Robust fallbacks ensure the mock never raises on an unmapped combination:
an unknown category/difficulty/language falls back to a generic entry so the
agent loop always receives well-formed text.
"""

from __future__ import annotations

# Canonical values (mirrors utils.config / future utils.constants). Kept as
# plain literals here so this module stays dependency-free.
INTENTS = ("question", "evaluation", "coaching")
CATEGORIES = ("software", "data_analyst", "customer_support", "business_marketing")
DIFFICULTIES = ("beginner", "intermediate", "advanced")
LANGUAGES = ("english", "tamil", "tanglish")

DEFAULT_LANGUAGE = "english"
DEFAULT_CATEGORY = "software"
DEFAULT_DIFFICULTY = "beginner"

# Keyword hints used by MockModel to classify the requested intent from the
# system prompt / latest user message. Order matters: evaluation and coaching
# are checked before the broad "question" fallback.
INTENT_KEYWORDS = {
    "coaching": ("coach", "improve", "improved sample", "better answer", "tips"),
    "evaluation": ("evaluate", "evaluation", "score", "assess", "feedback on"),
    "question": ("question", "interview", "ask", "interviewer"),
}

# Keyword hints for inferring the job category from prompt text.
CATEGORY_KEYWORDS = {
    "software": ("software", "developer", "programming", "it ", "code", "engineer"),
    "data_analyst": ("data analyst", "data analysis", "sql", "analytics", "dataset"),
    "customer_support": ("customer support", "support agent", "helpdesk", "customer service"),
    "business_marketing": ("business", "marketing", "sales", "campaign", "brand"),
}

# Keyword hints for inferring difficulty from prompt text.
DIFFICULTY_KEYWORDS = {
    "advanced": ("advanced", "senior", "expert"),
    "intermediate": ("intermediate", "mid-level", "mid level"),
    "beginner": ("beginner", "entry", "fresher", "junior"),
}

# Keyword hints for inferring the requested language from prompt text.
LANGUAGE_KEYWORDS = {
    "tamil": ("tamil", "தமிழ்"),
    "tanglish": ("tanglish",),
    "english": ("english",),
}


# ---------------------------------------------------------------------------
# Response content.
#
# To keep the table readable, each (category, difficulty) pair has one entry
# per language for each intent. Representative Tamil (Tamil script) and
# Tanglish (Tamil written in Latin script, mixed with English) strings are
# provided per decision #4.
# ---------------------------------------------------------------------------

RESPONSES: dict[str, dict[str, dict[str, dict[str, str]]]] = {
    "question": {
        "software": {
            "beginner": {
                "english": "Can you explain the difference between a list and a tuple in Python, and when you would use each?",
                "tamil": "Python-ல் list மற்றும் tuple இடையேயான வேறுபாட்டை விளக்க முடியுமா, எதை எப்போது பயன்படுத்துவீர்கள்?",
                "tanglish": "Python-la list-kum tuple-kum enna difference, edha eppo use pannuveenga nu sollunga?",
            },
            "intermediate": {
                "english": "How would you design a REST API endpoint to handle paginated results for a large dataset?",
                "tamil": "பெரிய தரவுத்தொகுப்புக்கு pagination-ஐ கையாள REST API endpoint-ஐ எப்படி வடிவமைப்பீர்கள்?",
                "tanglish": "Periya dataset-ku pagination handle panna REST API endpoint-ah epdi design pannuveenga?",
            },
            "advanced": {
                "english": "Describe how you would diagnose and resolve a memory leak in a long-running production service.",
                "tamil": "நீண்ட நேரம் இயங்கும் production service-ல் memory leak-ஐ எப்படி கண்டறிந்து தீர்ப்பீர்கள் என்பதை விளக்குங்கள்.",
                "tanglish": "Long-running production service-la memory leak-ah epdi diagnose panni fix pannuveenga nu sollunga.",
            },
        },
        "data_analyst": {
            "beginner": {
                "english": "What is the difference between a primary key and a foreign key in a relational database?",
                "tamil": "Relational database-ல் primary key மற்றும் foreign key இடையேயான வேறுபாடு என்ன?",
                "tanglish": "Relational database-la primary key-kum foreign key-kum enna difference?",
            },
            "intermediate": {
                "english": "Given a sales table, how would you write a query to find the top 3 products by revenue per region?",
                "tamil": "sales table கொடுக்கப்பட்டால், ஒவ்வொரு பகுதிக்கும் வருவாய் அடிப்படையில் முதல் 3 தயாரிப்புகளை எப்படி கண்டறிவீர்கள்?",
                "tanglish": "Sales table irundha, region-wise revenue vachu top 3 products-ah query panna epdi?",
            },
            "advanced": {
                "english": "How would you detect and handle outliers before building a forecasting model?",
                "tamil": "forecasting model உருவாக்கும் முன் outliers-ஐ எப்படி கண்டறிந்து கையாள்வீர்கள்?",
                "tanglish": "Forecasting model panna mundhi outliers-ah epdi detect panni handle pannuveenga?",
            },
        },
        "customer_support": {
            "beginner": {
                "english": "How would you respond to a customer who is frustrated about a delayed order?",
                "tamil": "தாமதமான order குறித்து வருத்தமடைந்த வாடிக்கையாளருக்கு எப்படி பதிலளிப்பீர்கள்?",
                "tanglish": "Order late aagi customer kovama irundha, neenga epdi respond pannuveenga?",
            },
            "intermediate": {
                "english": "A customer asks for a refund outside policy. How do you balance empathy with company rules?",
                "tamil": "கொள்கைக்கு வெளியே refund கேட்கும் வாடிக்கையாளருடன் பச்சாதாபத்தையும் நிறுவன விதிகளையும் எப்படி சமநிலைப்படுத்துவீர்கள்?",
                "tanglish": "Policy-ku veliya refund kekra customer-kitta empathy-um company rules-um epdi balance pannuveenga?",
            },
            "advanced": {
                "english": "How would you handle a surge of support tickets during a major outage while keeping customers informed?",
                "tamil": "பெரிய outage-ன் போது support tickets அதிகரிக்கும் போது வாடிக்கையாளர்களுக்கு தகவல் தெரிவித்தபடி எப்படி கையாள்வீர்கள்?",
                "tanglish": "Major outage time-la ticket surge varum, customers-ku update pannindey epdi handle pannuveenga?",
            },
        },
        "business_marketing": {
            "beginner": {
                "english": "How would you explain the difference between marketing and sales to a new teammate?",
                "tamil": "புதிய குழு உறுப்பினருக்கு marketing மற்றும் sales இடையேயான வேறுபாட்டை எப்படி விளக்குவீர்கள்?",
                "tanglish": "Pudhu teammate-ku marketing-kum sales-kum enna difference nu epdi explain pannuveenga?",
            },
            "intermediate": {
                "english": "How would you measure whether a social media campaign was successful?",
                "tamil": "ஒரு social media campaign வெற்றிகரமாக இருந்ததா என்பதை எப்படி அளவிடுவீர்கள்?",
                "tanglish": "Oru social media campaign success-ah nu epdi measure pannuveenga?",
            },
            "advanced": {
                "english": "Walk me through how you would build a go-to-market strategy for a new product with a limited budget.",
                "tamil": "குறைந்த பட்ஜெட்டில் புதிய தயாரிப்புக்கு go-to-market strategy-ஐ எப்படி உருவாக்குவீர்கள் என்பதை விளக்குங்கள்.",
                "tanglish": "Limited budget vachu pudhu product-ku go-to-market strategy-ah epdi build pannuveenga nu sollunga.",
            },
        },
    },
    "evaluation": {
        "software": {
            "beginner": {
                "english": "Good start. You correctly identified the core concept. To strengthen the answer, add a concrete example and mention trade-offs.",
                "tamil": "நல்ல தொடக்கம். அடிப்படைக் கருத்தை சரியாக அடையாளம் கண்டீர்கள். பதிலை வலுப்படுத்த, ஒரு உதாரணம் சேர்த்து trade-offs-ஐ குறிப்பிடுங்கள்.",
                "tanglish": "Nalla start. Core concept-ah correct-ah sonneenga. Answer-ah strong panna oru example-um trade-offs-um add pannunga.",
            },
            "intermediate": {
                "english": "Solid structure. Your API design covers the basics; consider edge cases like empty pages and invalid cursors to make it production-ready.",
                "tamil": "உறுதியான அமைப்பு. உங்கள் API design அடிப்படைகளை உள்ளடக்கியது; empty pages, invalid cursors போன்ற edge cases-ஐ கருத்தில் கொள்ளுங்கள்.",
                "tanglish": "Structure solid-ah iruku. API design basics cover aaguthu; empty pages, invalid cursors madhiri edge cases-um consider pannunga.",
            },
            "advanced": {
                "english": "Strong, systematic approach. You covered profiling well. Mention monitoring and alerting so leaks are caught earlier next time.",
                "tamil": "வலுவான, முறையான அணுகுமுறை. profiling-ஐ நன்றாக விளக்கினீர்கள். leaks சீக்கிரம் கண்டறிய monitoring மற்றும் alerting-ஐ குறிப்பிடுங்கள்.",
                "tanglish": "Approach strong-ah systematic-ah iruku. Profiling nalla cover panneenga. Leaks early-la pudikka monitoring, alerting-um sollunga.",
            },
        },
        "data_analyst": {
            "beginner": {
                "english": "Clear explanation. You defined the keys correctly. Add why referential integrity matters to show deeper understanding.",
                "tamil": "தெளிவான விளக்கம். keys-ஐ சரியாக வரையறுத்தீர்கள். referential integrity ஏன் முக்கியம் என்பதைச் சேர்த்தால் ஆழமான புரிதல் தெரியும்.",
                "tanglish": "Clear-ah explain panneenga. Keys-ah correct-ah define panneenga. Referential integrity epdi mukkiyam nu sonna deep understanding theriyum.",
            },
            "intermediate": {
                "english": "Good query logic. Window functions would make the top-N per region cleaner; mention that as an optimization.",
                "tamil": "நல்ல query logic. ஒவ்வொரு region-க்கும் top-N-ஐ window functions மூலம் சுத்தமாக செய்யலாம்; அதை ஒரு optimization-ஆக குறிப்பிடுங்கள்.",
                "tanglish": "Query logic nalla iruku. Region-wise top-N-ah window functions use panna clean-ah varum; adha optimization-ah sollunga.",
            },
            "advanced": {
                "english": "Thoughtful answer on outliers. You balanced detection methods well; add how you'd validate that removal didn't bias the model.",
                "tamil": "outliers பற்றிய சிந்தனைமிக்க பதில். detection methods-ஐ நன்கு சமநிலைப்படுத்தினீர்கள்; removal model-ஐ bias செய்யவில்லை என்பதை எப்படி சரிபார்ப்பீர்கள் என்பதைச் சேருங்கள்.",
                "tanglish": "Outliers pathi thoughtful-ah answer panneenga. Detection methods balance panneenga; removal model-ah bias pannalaya nu epdi validate pannuveenga nu add pannunga.",
            },
        },
        "customer_support": {
            "beginner": {
                "english": "Empathetic response. You acknowledged the frustration well. Add a concrete next step and a timeline to reassure the customer.",
                "tamil": "பச்சாதாபமான பதில். வருத்தத்தை நன்கு ஏற்றுக்கொண்டீர்கள். வாடிக்கையாளருக்கு உறுதியளிக்க அடுத்த நடவடிக்கையையும் timeline-ஐயும் சேருங்கள்.",
                "tanglish": "Empathy-oda respond panneenga. Frustration-ah nalla acknowledge panneenga. Customer-ku next step-um timeline-um sonna reassure aagum.",
            },
            "intermediate": {
                "english": "Nice balance of empathy and policy. Offer an alternative within policy so the customer still feels helped.",
                "tamil": "பச்சாதாபமும் கொள்கையும் நன்கு சமநிலை. வாடிக்கையாளருக்கு உதவி கிடைத்ததாக உணர கொள்கைக்குள் ஒரு மாற்று வழங்குங்கள்.",
                "tanglish": "Empathy-um policy-um nalla balance panneenga. Policy-kkulla oru alternative offer panna customer-ku help aana madhiri irukum.",
            },
            "advanced": {
                "english": "Strong crisis handling. You prioritized communication well; add how you'd triage tickets by severity to scale the response.",
                "tamil": "வலுவான crisis handling. தகவல் தொடர்பை நன்கு முன்னுரிமைப்படுத்தினீர்கள்; severity அடிப்படையில் tickets-ஐ எப்படி triage செய்வீர்கள் என்பதைச் சேருங்கள்.",
                "tanglish": "Crisis handling strong-ah iruku. Communication-ah prioritize panneenga; severity-wise tickets-ah epdi triage pannuveenga nu add pannunga.",
            },
        },
        "business_marketing": {
            "beginner": {
                "english": "Clear distinction. You captured the roles well. Add an example of how the two teams hand off leads to show real-world insight.",
                "tamil": "தெளிவான வேறுபாடு. பாத்திரங்களை நன்கு விளக்கினீர்கள். இரு குழுக்களும் leads-ஐ எப்படி கைமாற்றுகின்றன என்பதற்கு உதாரணம் சேருங்கள்.",
                "tanglish": "Clear-ah difference sonneenga. Roles-ah nalla capture panneenga. Rendu teams leads-ah epdi hand off pannudhu nu example add pannunga.",
            },
            "intermediate": {
                "english": "Good use of metrics. You named the right KPIs; tie them back to a business goal like ROI to make it more convincing.",
                "tamil": "metrics-ஐ நன்கு பயன்படுத்தினீர்கள். சரியான KPIs-ஐ குறிப்பிட்டீர்கள்; ROI போன்ற business goal-உடன் இணைத்தால் மேலும் உறுதியாக இருக்கும்.",
                "tanglish": "Metrics nalla use panneenga. Correct KPIs sonneenga; ROI madhiri business goal-oda connect panna innum convincing-ah irukum.",
            },
            "advanced": {
                "english": "Impressive strategy. You sequenced the channels well; quantify the budget split across channels to make it actionable.",
                "tamil": "சிறப்பான strategy. channels-ஐ நன்கு வரிசைப்படுத்தினீர்கள்; channels-க்கு இடையேயான budget பிரிவை அளவிட்டால் செயல்படுத்தக்கூடியதாக இருக்கும்.",
                "tanglish": "Strategy semma. Channels-ah nalla sequence panneenga; channels-ku budget split-ah quantify panna actionable-ah irukum.",
            },
        },
    },
    "coaching": {
        "software": {
            "beginner": {
                "english": "Tip: Lead with a one-line definition, then a short example. Improved sample answer: \"A list is mutable and ordered, so I use it when items change. A tuple is immutable, so I use it for fixed records like coordinates, which also makes it safely hashable.\"",
                "tamil": "குறிப்பு: முதலில் ஒரு வரி வரையறை, பிறகு ஒரு சிறிய உதாரணம். மேம்படுத்தப்பட்ட மாதிரி பதில் (ஆங்கிலம்): \"A list is mutable and ordered, so I use it when items change. A tuple is immutable, so I use it for fixed records like coordinates, which also makes it safely hashable.\"",
                "tanglish": "Tip: Mudhalla one-line definition, apram oru chinna example sollunga. Improved sample answer (English): \"A list is mutable and ordered, so I use it when items change. A tuple is immutable, so I use it for fixed records like coordinates, which also makes it safely hashable.\"",
            },
            "intermediate": {
                "english": "Tip: Call out edge cases explicitly. Improved sample answer: \"I'd paginate with limit and cursor parameters, return a nextCursor in the response, validate the cursor, and handle empty result sets by returning an empty array with a null nextCursor.\"",
                "tamil": "குறிப்பு: edge cases-ஐ தெளிவாகக் குறிப்பிடுங்கள். மேம்படுத்தப்பட்ட மாதிரி பதில் (ஆங்கிலம்): \"I'd paginate with limit and cursor parameters, return a nextCursor in the response, validate the cursor, and handle empty result sets by returning an empty array with a null nextCursor.\"",
                "tanglish": "Tip: Edge cases-ah clear-ah sollunga. Improved sample answer (English): \"I'd paginate with limit and cursor parameters, return a nextCursor in the response, validate the cursor, and handle empty result sets by returning an empty array with a null nextCursor.\"",
            },
            "advanced": {
                "english": "Tip: Structure it as detect, isolate, fix, prevent. Improved sample answer: \"I'd confirm the leak with memory profiling, isolate it by correlating allocations with request patterns, fix the retained references, then add monitoring and alerts so regressions surface before customers notice.\"",
                "tamil": "குறிப்பு: detect, isolate, fix, prevent என்று அமைக்கவும். மேம்படுத்தப்பட்ட மாதிரி பதில் (ஆங்கிலம்): \"I'd confirm the leak with memory profiling, isolate it by correlating allocations with request patterns, fix the retained references, then add monitoring and alerts so regressions surface before customers notice.\"",
                "tanglish": "Tip: detect, isolate, fix, prevent nu structure pannunga. Improved sample answer (English): \"I'd confirm the leak with memory profiling, isolate it by correlating allocations with request patterns, fix the retained references, then add monitoring and alerts so regressions surface before customers notice.\"",
            },
        },
        "data_analyst": {
            "beginner": {
                "english": "Tip: Define the term, then state its purpose. Improved sample answer: \"A primary key uniquely identifies each row in a table. A foreign key references a primary key in another table, enforcing referential integrity between related records.\"",
                "tamil": "குறிப்பு: சொல்லை வரையறுத்து, பிறகு அதன் நோக்கத்தைக் கூறுங்கள். மேம்படுத்தப்பட்ட மாதிரி பதில் (ஆங்கிலம்): \"A primary key uniquely identifies each row in a table. A foreign key references a primary key in another table, enforcing referential integrity between related records.\"",
                "tanglish": "Tip: Term-ah define panni purpose sollunga. Improved sample answer (English): \"A primary key uniquely identifies each row in a table. A foreign key references a primary key in another table, enforcing referential integrity between related records.\"",
            },
            "intermediate": {
                "english": "Tip: Mention the technique by name. Improved sample answer: \"I'd use ROW_NUMBER() partitioned by region and ordered by revenue descending, then filter to rank <= 3, which is cleaner and faster than correlated subqueries.\"",
                "tamil": "குறிப்பு: நுட்பத்தை பெயரால் குறிப்பிடுங்கள். மேம்படுத்தப்பட்ட மாதிரி பதில் (ஆங்கிலம்): \"I'd use ROW_NUMBER() partitioned by region and ordered by revenue descending, then filter to rank <= 3, which is cleaner and faster than correlated subqueries.\"",
                "tanglish": "Tip: Technique-ah name sollunga. Improved sample answer (English): \"I'd use ROW_NUMBER() partitioned by region and ordered by revenue descending, then filter to rank <= 3, which is cleaner and faster than correlated subqueries.\"",
            },
            "advanced": {
                "english": "Tip: Show you validate your choices. Improved sample answer: \"I'd flag outliers using IQR and domain thresholds, decide per-case whether to cap or drop them, and validate that the treatment didn't shift key distributions or bias the forecast.\"",
                "tamil": "குறிப்பு: உங்கள் தேர்வுகளை சரிபார்ப்பதைக் காட்டுங்கள். மேம்படுத்தப்பட்ட மாதிரி பதில் (ஆங்கிலம்): \"I'd flag outliers using IQR and domain thresholds, decide per-case whether to cap or drop them, and validate that the treatment didn't shift key distributions or bias the forecast.\"",
                "tanglish": "Tip: Choices-ah validate panradha kaattunga. Improved sample answer (English): \"I'd flag outliers using IQR and domain thresholds, decide per-case whether to cap or drop them, and validate that the treatment didn't shift key distributions or bias the forecast.\"",
            },
        },
        "customer_support": {
            "beginner": {
                "english": "Tip: Acknowledge, apologize, act. Improved sample answer: \"I understand how frustrating a delay is, and I'm sorry for the inconvenience. Let me check the status right now and give you a firm updated delivery date within the next few minutes.\"",
                "tamil": "குறிப்பு: ஏற்றுக்கொள், மன்னிப்பு கேள், நடவடிக்கை எடு. மேம்படுத்தப்பட்ட மாதிரி பதில் (ஆங்கிலம்): \"I understand how frustrating a delay is, and I'm sorry for the inconvenience. Let me check the status right now and give you a firm updated delivery date within the next few minutes.\"",
                "tanglish": "Tip: Acknowledge, apologize, act nu pannunga. Improved sample answer (English): \"I understand how frustrating a delay is, and I'm sorry for the inconvenience. Let me check the status right now and give you a firm updated delivery date within the next few minutes.\"",
            },
            "intermediate": {
                "english": "Tip: Offer an in-policy alternative. Improved sample answer: \"I'm not able to refund outside our policy, but I can offer store credit or an exchange today. I want to make sure you still get value from this, so which option works better for you?\"",
                "tamil": "குறிப்பு: கொள்கைக்குள் ஒரு மாற்றை வழங்குங்கள். மேம்படுத்தப்பட்ட மாதிரி பதில் (ஆங்கிலம்): \"I'm not able to refund outside our policy, but I can offer store credit or an exchange today. I want to make sure you still get value from this, so which option works better for you?\"",
                "tanglish": "Tip: Policy-kkulla alternative offer pannunga. Improved sample answer (English): \"I'm not able to refund outside our policy, but I can offer store credit or an exchange today. I want to make sure you still get value from this, so which option works better for you?\"",
            },
            "advanced": {
                "english": "Tip: Communicate proactively and triage. Improved sample answer: \"I'd post a status banner, send proactive updates at fixed intervals, and triage tickets by severity so critical issues are handled first while everyone gets a clear acknowledgment.\"",
                "tamil": "குறிப்பு: முன்கூட்டியே தொடர்பு கொண்டு triage செய்யுங்கள். மேம்படுத்தப்பட்ட மாதிரி பதில் (ஆங்கிலம்): \"I'd post a status banner, send proactive updates at fixed intervals, and triage tickets by severity so critical issues are handled first while everyone gets a clear acknowledgment.\"",
                "tanglish": "Tip: Proactive-ah communicate panni triage pannunga. Improved sample answer (English): \"I'd post a status banner, send proactive updates at fixed intervals, and triage tickets by severity so critical issues are handled first while everyone gets a clear acknowledgment.\"",
            },
        },
        "business_marketing": {
            "beginner": {
                "english": "Tip: Define both, then connect them. Improved sample answer: \"Marketing creates awareness and demand through content and campaigns, while sales converts that demand into revenue through direct relationships. Marketing hands qualified leads to sales to close.\"",
                "tamil": "குறிப்பு: இரண்டையும் வரையறுத்து, பிறகு இணைக்கவும். மேம்படுத்தப்பட்ட மாதிரி பதில் (ஆங்கிலம்): \"Marketing creates awareness and demand through content and campaigns, while sales converts that demand into revenue through direct relationships. Marketing hands qualified leads to sales to close.\"",
                "tanglish": "Tip: Rendayum define panni connect pannunga. Improved sample answer (English): \"Marketing creates awareness and demand through content and campaigns, while sales converts that demand into revenue through direct relationships. Marketing hands qualified leads to sales to close.\"",
            },
            "intermediate": {
                "english": "Tip: Tie metrics to a goal. Improved sample answer: \"I'd track reach, engagement rate, click-through, and conversions, then measure them against the campaign goal and cost to report ROI, not just vanity metrics.\"",
                "tamil": "குறிப்பு: metrics-ஐ ஒரு goal-உடன் இணைக்கவும். மேம்படுத்தப்பட்ட மாதிரி பதில் (ஆங்கிலம்): \"I'd track reach, engagement rate, click-through, and conversions, then measure them against the campaign goal and cost to report ROI, not just vanity metrics.\"",
                "tanglish": "Tip: Metrics-ah goal-oda connect pannunga. Improved sample answer (English): \"I'd track reach, engagement rate, click-through, and conversions, then measure them against the campaign goal and cost to report ROI, not just vanity metrics.\"",
            },
            "advanced": {
                "english": "Tip: Make the budget concrete. Improved sample answer: \"With a limited budget I'd validate the target segment, lead with one or two high-ROI channels, allocate most spend there, reserve a small test budget for new channels, and scale what converts.\"",
                "tamil": "குறிப்பு: budget-ஐ உறுதியாக்குங்கள். மேம்படுத்தப்பட்ட மாதிரி பதில் (ஆங்கிலம்): \"With a limited budget I'd validate the target segment, lead with one or two high-ROI channels, allocate most spend there, reserve a small test budget for new channels, and scale what converts.\"",
                "tanglish": "Tip: Budget-ah concrete-ah sollunga. Improved sample answer (English): \"With a limited budget I'd validate the target segment, lead with one or two high-ROI channels, allocate most spend there, reserve a small test budget for new channels, and scale what converts.\"",
            },
        },
    },
}


def normalize(value: str | None, valid: tuple[str, ...], default: str) -> str:
    """Return ``value`` if it is a recognized option, else ``default``."""
    if not value:
        return default
    candidate = value.strip().lower()
    return candidate if candidate in valid else default


def get_response(
    intent: str,
    category: str | None = None,
    difficulty: str | None = None,
    language: str | None = None,
) -> str:
    """Look up a canned response, falling back safely on unknown inputs.

    Args:
        intent: One of ``INTENTS``.
        category: One of ``CATEGORIES`` (falls back to ``DEFAULT_CATEGORY``).
        difficulty: One of ``DIFFICULTIES`` (falls back to ``DEFAULT_DIFFICULTY``).
        language: One of ``LANGUAGES`` (falls back to ``DEFAULT_LANGUAGE``).

    Returns:
        A response string. Never raises for unmapped combinations.
    """
    intent = normalize(intent, INTENTS, "question")
    category = normalize(category, CATEGORIES, DEFAULT_CATEGORY)
    difficulty = normalize(difficulty, DIFFICULTIES, DEFAULT_DIFFICULTY)
    language = normalize(language, LANGUAGES, DEFAULT_LANGUAGE)

    by_category = RESPONSES[intent]
    by_difficulty = by_category.get(category, by_category[DEFAULT_CATEGORY])
    by_language = by_difficulty.get(difficulty, by_difficulty[DEFAULT_DIFFICULTY])
    return by_language.get(language, by_language[DEFAULT_LANGUAGE])
