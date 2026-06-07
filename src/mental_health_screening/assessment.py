import math
import json
from pathlib import Path
from functools import lru_cache

from .constants import PREDICTION_DOMAINS
from .utils import average, normalize_score, risk_level


QUESTION_BANK = [
    {
        "id": "dep_interest",
        "section": "Depression",
        "prompt": "In the last two weeks, how often have you had little interest or pleasure in daily activities?",
        "domain": "depression",
    },
    {
        "id": "dep_down",
        "section": "Depression",
        "prompt": "In the last two weeks, how often have you felt down, hopeless, or emotionally low?",
        "domain": "depression",
    },
    {
        "id": "dep_sleep",
        "section": "Depression",
        "prompt": "In the last two weeks, how often have sleep problems made your days harder?",
        "domain": "depression",
    },
    {
        "id": "dep_energy",
        "section": "Depression",
        "prompt": "In the last two weeks, how often have you felt low in energy or slowed down during the day?",
        "domain": "depression",
    },
    {
        "id": "dep_guilt",
        "section": "Depression",
        "prompt": "In the last two weeks, how often have you felt like a burden, a failure, or blamed yourself too much?",
        "domain": "depression",
    },
    {
        "id": "dep_focus",
        "section": "Depression",
        "prompt": "In the last two weeks, how often have you had trouble focusing, remembering, or making simple decisions?",
        "domain": "depression",
    },
    {
        "id": "anx_worry",
        "section": "Anxiety",
        "prompt": "In the last two weeks, how often have you found it hard to control worrying?",
        "domain": "anxiety",
    },
    {
        "id": "anx_restless",
        "section": "Anxiety",
        "prompt": "In the last two weeks, how often have you felt nervous, restless, or on edge?",
        "domain": "anxiety",
    },
    {
        "id": "anx_fear",
        "section": "Anxiety",
        "prompt": "In the last two weeks, how often have you felt afraid that something bad may happen?",
        "domain": "anxiety",
    },
    {
        "id": "anx_body",
        "section": "Anxiety",
        "prompt": "In the last two weeks, how often have you had physical anxiety signs such as a racing heart, trembling, or sweating?",
        "domain": "anxiety",
    },
    {
        "id": "anx_avoid",
        "section": "Anxiety",
        "prompt": "In the last two weeks, how often have you avoided people, places, or tasks because they increased your anxiety?",
        "domain": "anxiety",
    },
    {
        "id": "anx_reassure",
        "section": "Anxiety",
        "prompt": "In the last two weeks, how often have you needed repeated reassurance before doing ordinary daily activities?",
        "domain": "anxiety",
    },
    {
        "id": "str_overload",
        "section": "Stress",
        "prompt": "In the last two weeks, how often have daily responsibilities felt too overwhelming to manage?",
        "domain": "stress",
    },
    {
        "id": "str_irritable",
        "section": "Stress",
        "prompt": "In the last two weeks, how often have you felt irritable, tense, or unable to relax?",
        "domain": "stress",
    },
    {
        "id": "str_function",
        "section": "Stress",
        "prompt": "In the last two weeks, how often have stress symptoms affected your work, home life, or relationships?",
        "domain": "stress",
    },
    {
        "id": "str_pressure",
        "section": "Stress",
        "prompt": "In the last two weeks, how often have you felt under constant pressure with too little time or support?",
        "domain": "stress",
    },
    {
        "id": "str_recovery",
        "section": "Stress",
        "prompt": "In the last two weeks, how often have you found it hard to calm down or recover after stressful events?",
        "domain": "stress",
    },
    {
        "id": "str_headaches",
        "section": "Stress",
        "prompt": "In the last two weeks, how often has stress shown up as headaches, body pain, or stomach discomfort?",
        "domain": "stress",
    },
    {
        "id": "sleep_quality",
        "section": "Sleep Disorder",
        "prompt": "In the last two weeks, how often have you had trouble falling asleep, staying asleep, or waking too early?",
        "domain": "sleep_disorder",
    },
    {
        "id": "sleep_daytime",
        "section": "Sleep Disorder",
        "prompt": "In the last two weeks, how often have poor sleep symptoms made you tired or sleepy during the day?",
        "domain": "sleep_disorder",
    },
    {
        "id": "sleep_routine",
        "section": "Sleep Disorder",
        "prompt": "In the last two weeks, how often has your sleep schedule felt irregular or difficult to control?",
        "domain": "sleep_disorder",
    },
    {
        "id": "sleep_refresh",
        "section": "Sleep Disorder",
        "prompt": "In the last two weeks, how often have you woken up feeling unrefreshed even after enough hours in bed?",
        "domain": "sleep_disorder",
    },
    {
        "id": "sleep_worry",
        "section": "Sleep Disorder",
        "prompt": "In the last two weeks, how often has worrying about sleep made it harder for you to rest?",
        "domain": "sleep_disorder",
    },
    {
        "id": "sleep_interrupt",
        "section": "Sleep Disorder",
        "prompt": "In the last two weeks, how often has your sleep been interrupted by dreams, worry, pain, or restlessness?",
        "domain": "sleep_disorder",
    },
    {
        "id": "burnout_exhaustion",
        "section": "Burnout",
        "prompt": "In the last two weeks, how often have you felt emotionally or physically exhausted by daily responsibilities?",
        "domain": "burnout",
    },
    {
        "id": "burnout_detachment",
        "section": "Burnout",
        "prompt": "In the last two weeks, how often have you felt detached, numb, or less motivated toward work or caregiving duties?",
        "domain": "burnout",
    },
    {
        "id": "burnout_capacity",
        "section": "Burnout",
        "prompt": "In the last two weeks, how often have you felt that you could no longer keep up with your usual responsibilities?",
        "domain": "burnout",
    },
    {
        "id": "burnout_cynical",
        "section": "Burnout",
        "prompt": "In the last two weeks, how often have you felt frustrated, cynical, or emotionally distant from your work or caregiving role?",
        "domain": "burnout",
    },
    {
        "id": "burnout_reward",
        "section": "Burnout",
        "prompt": "In the last two weeks, how often has your effort felt high while appreciation, return, or support felt low?",
        "domain": "burnout",
    },
    {
        "id": "burnout_recovery",
        "section": "Burnout",
        "prompt": "In the last two weeks, how often have you still felt drained even after taking rest?",
        "domain": "burnout",
    },
    {
        "id": "lonely_isolated",
        "section": "Loneliness",
        "prompt": "In the last two weeks, how often have you felt alone or isolated even when other people were nearby?",
        "domain": "loneliness",
    },
    {
        "id": "lonely_support",
        "section": "Loneliness",
        "prompt": "In the last two weeks, how often have you felt that you lacked emotional support from family or friends?",
        "domain": "loneliness",
    },
    {
        "id": "lonely_connection",
        "section": "Loneliness",
        "prompt": "In the last two weeks, how often have you found it hard to feel connected to people around you?",
        "domain": "loneliness",
    },
    {
        "id": "lonely_belong",
        "section": "Loneliness",
        "prompt": "In the last two weeks, how often have you felt that you did not fully belong in your family, workplace, or community?",
        "domain": "loneliness",
    },
    {
        "id": "lonely_share",
        "section": "Loneliness",
        "prompt": "In the last two weeks, how often have you felt you had few people to openly share worries or emotions with?",
        "domain": "loneliness",
    },
    {
        "id": "lonely_withdraw",
        "section": "Loneliness",
        "prompt": "In the last two weeks, how often have you withdrawn from conversations, gatherings, or relationships more than before?",
        "domain": "loneliness",
    },
    {
        "id": "substance_frequency",
        "section": "Substance Abuse",
        "prompt": "In the last two weeks, how often have alcohol, tobacco, or other substances been used to cope with emotions or stress?",
        "domain": "substance_abuse",
    },
    {
        "id": "substance_control",
        "section": "Substance Abuse",
        "prompt": "In the last two weeks, how often have you found it difficult to reduce or control substance use?",
        "domain": "substance_abuse",
    },
    {
        "id": "substance_impact",
        "section": "Substance Abuse",
        "prompt": "In the last two weeks, how often has substance use affected your health, relationships, or daily responsibilities?",
        "domain": "substance_abuse",
    },
    {
        "id": "substance_craving",
        "section": "Substance Abuse",
        "prompt": "In the last two weeks, how often have you had strong urges or cravings that were difficult to ignore?",
        "domain": "substance_abuse",
    },
    {
        "id": "substance_tolerance",
        "section": "Substance Abuse",
        "prompt": "In the last two weeks, how often have you needed more of a substance than before to get the same effect?",
        "domain": "substance_abuse",
    },
    {
        "id": "substance_withdrawal",
        "section": "Substance Abuse",
        "prompt": "In the last two weeks, how often have you felt unwell, irritable, or restless when trying not to use the substance?",
        "domain": "substance_abuse",
    },
]

RESPONSE_OPTIONS = {
    "Not at all": 0,
    "Several days": 1,
    "More than half the days": 2,
    "Nearly every day": 3,
}

LANGUAGE_ALIASES = {
    "english": "English",
    "en": "English",
    "hindi": "Hindi",
    "hi": "Hindi",
    "हिंदी": "Hindi",
    "bengali": "Bengali",
    "bangla": "Bengali",
    "bn": "Bengali",
    "বাংলা": "Bengali",
    "বাঙলা": "Bengali",
}

RESPONSE_OPTION_TRANSLATIONS = {
    "English": {
        "Not at all": "Not at all",
        "Several days": "Several days",
        "More than half the days": "More than half the days",
        "Nearly every day": "Nearly every day",
    },
    "Hindi": {
        "Not at all": "बिलकुल नहीं",
        "Several days": "कुछ दिन",
        "More than half the days": "आधे से अधिक दिन",
        "Nearly every day": "लगभग हर दिन",
    },
    "Bengali": {
        "Not at all": "একদম না",
        "Several days": "কয়েক দিন",
        "More than half the days": "অর্ধেকের বেশি দিন",
        "Nearly every day": "প্রায় প্রতিদিন",
    },
}

ADAPTIVE_CHOOSE_ONE_TRANSLATIONS = {
    "English": "Choose one",
    "Hindi": "\u090f\u0915 \u091a\u0941\u0928\u0947\u0902",
    "Bengali": "\u098f\u0995\u099f\u09bf \u09a8\u09bf\u09b0\u09cd\u09ac\u09be\u099a\u09a8 \u0995\u09b0\u09c1\u09a8",
}

ADAPTIVE_SECTION_TRANSLATIONS = {
    "Depression": {"Hindi": "डिप्रेशन", "Bengali": "বিষণ্নতা"},
    "Anxiety": {"Hindi": "एंग्जायटी", "Bengali": "উদ্বেগ"},
    "Stress": {"Hindi": "स्ट्रेस", "Bengali": "স্ট্রেস"},
    "Sleep Disorder": {"Hindi": "नींद संबंधी समस्या", "Bengali": "ঘুমের সমস্যা"},
    "Burnout": {"Hindi": "बर्नआउट", "Bengali": "বার্নআউট"},
    "Loneliness": {"Hindi": "अकेलापन", "Bengali": "একাকীত্ব"},
    "Substance Abuse": {"Hindi": "पदार्थ दुरुपयोग", "Bengali": "পদার্থের অপব্যবহার"},
}

ADAPTIVE_QUESTION_TRANSLATIONS = {
    "dep_interest": {"Hindi": "दैनिक गतिविधियों में रुचि या आनंद कम लगना।", "Bengali": "দৈনন্দিন কাজে আগ্রহ বা আনন্দ কমে যাওয়া।"},
    "dep_down": {"Hindi": "उदास, निराश या भावनात्मक रूप से नीचे महसूस करना।", "Bengali": "উদাস, নিরাশ বা মানসিকভাবে ভেঙে পড়া অনুভব করা।"},
    "dep_sleep": {"Hindi": "नींद की समस्या के कारण दिन और कठिन लगना।", "Bengali": "ঘুমের সমস্যার কারণে দিন আরও কঠিন লাগা।"},
    "dep_energy": {"Hindi": "दिन में ऊर्जा कम होना या सुस्त महसूस करना।", "Bengali": "দিনে শক্তি কম থাকা বা ধীর অনুভব করা।"},
    "dep_guilt": {"Hindi": "खुद को बोझ, असफल या बहुत अधिक दोषी महसूस करना।", "Bengali": "নিজেকে বোঝা, ব্যর্থ বা অতিরিক্ত দোষী মনে হওয়া।"},
    "dep_focus": {"Hindi": "ध्यान, याददाश्त या छोटे फैसले लेने में कठिनाई।", "Bengali": "মনোযোগ, স্মৃতি বা ছোট সিদ্ধান্ত নিতে অসুবিধা।"},
    "anx_worry": {"Hindi": "चिंता को नियंत्रित करना कठिन लगना।", "Bengali": "দুশ্চিন্তা নিয়ন্ত্রণ করা কঠিন লাগা।"},
    "anx_restless": {"Hindi": "बेचैन, घबराया हुआ या तनावग्रस्त महसूस करना।", "Bengali": "অস্থির, নার্ভাস বা চাপে থাকা অনুভব করা।"},
    "anx_fear": {"Hindi": "ऐसा डर लगना कि कुछ बुरा होने वाला है।", "Bengali": "মনে হওয়া যে কিছু খারাপ ঘটতে পারে।"},
    "anx_body": {"Hindi": "घबराहट के शारीरिक संकेत जैसे दिल तेज चलना, कांपना या पसीना आना।", "Bengali": "উদ্বেগের শারীরিক লক্ষণ যেমন হৃদস্পন্দন বেড়ে যাওয়া, কাঁপা বা ঘাম হওয়া।"},
    "anx_avoid": {"Hindi": "चिंता बढ़ने के डर से लोगों, जगहों या कामों से बचना।", "Bengali": "উদ্বেগ বাড়ে বলে মানুষ, জায়গা বা কাজ এড়িয়ে চলা।"},
    "anx_reassure": {"Hindi": "साधारण काम करने से पहले बार-बार आश्वासन की जरूरत महसूस होना।", "Bengali": "সাধারণ কাজের আগে বারবার আশ্বাসের প্রয়োজন অনুভব করা।"},
    "str_overload": {"Hindi": "दैनिक जिम्मेदारियाँ बहुत भारी लगना।", "Bengali": "দৈনন্দিন দায়িত্ব খুব বেশি চাপের মনে হওয়া।"},
    "str_irritable": {"Hindi": "चिड़चिड़ापन, तनाव या आराम न कर पाना।", "Bengali": "খিটখিটে লাগা, টানটান থাকা বা আরাম করতে না পারা।"},
    "str_function": {"Hindi": "तनाव का काम, घर या संबंधों पर असर पड़ना।", "Bengali": "চাপের কারণে কাজ, বাড়ি বা সম্পর্ক ক্ষতিগ্রস্ত হওয়া।"},
    "str_pressure": {"Hindi": "लगातार दबाव महसूस होना और समय या समर्थन कम लगना।", "Bengali": "নিরন্তর চাপ অনুভব করা और समय বা সহায়তা कम মনে হওয়া।"},
    "str_recovery": {"Hindi": "तनावपूर्ण घटना के बाद शांत होने या संभलने में कठिनाई।", "Bengali": "চাপের ঘটনার পর শান্ত হতে বা সামলাতে কষ্ট হওয়া।"},
    "str_headaches": {"Hindi": "तनाव का सिरदर्द, शरीर दर्द या पेट की तकलीफ के रूप में दिखना।", "Bengali": "চাপের কারণে মাথাব্যথা, শরীর ব্যথা বা পেটের সমস্যা হওয়া।"},
    "sleep_quality": {"Hindi": "नींद आने, नींद बनाए रखने या बहुत जल्दी जागने में कठिनाई।", "Bengali": "ঘুম আসা, ঘুম ধরে রাখা বা খুব তাড়াতাড়ি জেগে ওঠার সমস্যা।"},
    "sleep_daytime": {"Hindi": "खराब नींद के कारण दिन में थकान या नींद आना।", "Bengali": "খারাপ ঘুমের কারণে দিনে ক্লান্তি বা ঘুম ঘুম ভাব হওয়া।"},
    "sleep_routine": {"Hindi": "अनियमित नींद का समय जिसे नियंत्रित करना मुश्किल हो।", "Bengali": "অনিয়মিত ঘুমের সময়সূচি যা নিয়ন্ত্রণ করা কঠিন।"},
    "sleep_refresh": {"Hindi": "काफी समय बिस्तर पर रहने के बाद भी तरोताजा महसूस न होना।", "Bengali": "যথেষ্ট সময় ঘুমিয়েও সতেজ না লাগা।"},
    "sleep_worry": {"Hindi": "नींद को लेकर इतनी चिंता होना कि आराम और मुश्किल हो जाए।", "Bengali": "ঘুম নিয়ে এত দুশ্চিন্তা হওয়া যে বিশ্রাম আরও কঠিন হয়ে যায়।"},
    "sleep_interrupt": {"Hindi": "सपनों, चिंता, दर्द या बेचैनी से बार-बार नींद टूटना।", "Bengali": "স্বপ্ন, দুশ্চিন্তা, ব্যথা বা অস্থিরতায় বারবার ঘুম ভাঙা।"},
    "burnout_exhaustion": {"Hindi": "जिम्मेदारियों के कारण भावनात्मक या शारीरिक थकान महसूस करना।", "Bengali": "দায়িত্বের কারণে মানসিক বা শারীরিক ক্লান্তি অনুভব করা।"},
    "burnout_detachment": {"Hindi": "जिम्मेदारियों से अलगाव, सुन्नपन या प्रेरणा कम लगना।", "Bengali": "দায়িত্ব থেকে বিচ্ছিন্ন, নিস্তেজ या অনুপ্রেরণাহীন লাগা।"},
    "burnout_capacity": {"Hindi": "सामान्य जिम्मेदारियों को निभा पाने में असमर्थ महसूस करना।", "Bengali": "সাধারণ দায়িত্ব সামলাতে না পারার মতো অনুভব করা।"},
    "burnout_cynical": {"Hindi": "काम या देखभाल की भूमिका के प्रति चिड़चिड़ापन, निराशा या दूरी महसूस करना।", "Bengali": "কাজ বা যত্নের ভূমিকার প্রতি বিরক্তি, হতাশा বা দূরত্ব অনুভব করা।"},
    "burnout_reward": {"Hindi": "लगना कि मेहनत ज़्यादा है लेकिन सराहना, लाभ या समर्थन कम है।", "Bengali": "মনে হওয়া যে পরিশ্রম বেশি কিন্তু মূল্যায়ন, ফল বা সহায়তা কম।"},
    "burnout_recovery": {"Hindi": "आराम के बाद भी पूरी तरह ठीक या तरोताजा महसूस न होना।", "Bengali": "বিশ্রামের পরও পুরোপুরি সুস্থ বা সতেজ না লাগা।"},
    "lonely_isolated": {"Hindi": "लोगों के पास होने पर भी अकेला या अलग-थलग महसूस करना।", "Bengali": "মানুষ কাছে থাকলেও একা या বিচ্ছিন্ন লাগা।"},
    "lonely_support": {"Hindi": "भावनात्मक समर्थन की कमी महसूस होना।", "Bengali": "মানসিক সহায়তার অভাব অনুভव করা।"},
    "lonely_connection": {"Hindi": "आसपास के लोगों से जुड़ाव महसूस करना कठिन होना।", "Bengali": "চারপাশের মানুষের সাথে সংযোগ অনুভব করতে কষ্ট হওয়া।"},
    "lonely_belong": {"Hindi": "परिवार, काम या समुदाय में अपनेपन की कमी महसूस होना।", "Bengali": "পরিবার, কাজ বা সমাজে নিজের জায়গা না পাওয়ার অনুভূতি।"},
    "lonely_share": {"Hindi": "ऐसे लोगों की कमी जिनसे खुलकर चिंता या भावनाएँ बाँट सकें।", "Bengali": "খোলামেলা ভাবে দুশ্চিন্তা বা অনুভূতি ভাগ করার মতো মানুষ কম থাকা।"},
    "lonely_withdraw": {"Hindi": "बातचीत, मेल-मिलाप या रिश्तों से पहले से ज़्यादा दूर होना।", "Bengali": "আলোচনা, মেলামেশा বা সম্পর্ক থেকে আগের চেয়ে বেশি সরে যাওয়া।"},
    "substance_frequency": {"Hindi": "तनाव या भावनाओं से निपटने के लिए शराब, तंबाकू या अन्य पदार्थों का उपयोग करना।", "Bengali": "চাপ বা আবেগ সামলাতে মদ, তামাক বা অন্য পদার্থ ব্যবহার করা।"},
    "substance_control": {"Hindi": "पदार्थ उपयोग कम या नियंत्रित करना कठिन लगना।", "Bengali": "পদার্থের ব্যবহার কমানো বা নিয়ন্ত্রণ করা কঠিন লাগা।"},
    "substance_impact": {"Hindi": "पदार्थ उपयोग का स्वास्थ्य, संबंधों या जिम्मेदारियों पर असर पड़ना।", "Bengali": "পদার্থ ব্যবহারের কারণে স্বাস্থ্য, সম্পর্ক বা দায়িত্ব ক্ষতিগ্রস্ত হওয়া।"},
    "substance_craving": {"Hindi": "तेज़ इच्छा या लालसा जिसे रोकना कठिन हो।", "Bengali": "তীব্র চাহিদা বা ক্রেভিং যা নিয়ন্ত্রণ করা কঠিন।"},
    "substance_tolerance": {"Hindi": "पहले जैसा असर पाने के लिए पहले से अधिक मात्रा की जरूरत होना।", "Bengali": "আগের মতো প্রভাব পেতে আগের চেয়ে বেশি পরিমাণ দরকার হওয়া।"},
    "substance_withdrawal": {"Hindi": "उपयोग कम करने पर बेचैनी, चिड़चिड़ापन या अस्वस्थता महसूस होना।", "Bengali": "ব্যবহার কমালে অস্বস্তি, খিটখিটে ভাব বা অস্থিরতা অনুভव করা।"},
}

ADAPTIVE_MIN_ITEMS = 4
ADAPTIVE_MAX_ITEMS = 10
ADAPTIVE_INFO_THRESHOLD = 0.18
ADAPTIVE_DOMAIN_BALANCE_WEIGHT = 0.18
ADAPTIVE_THETA_PRIOR_SD = 1.5
ADAPTIVE_THETA_GRID_MIN = -3.0
ADAPTIVE_THETA_GRID_MAX = 3.0
ADAPTIVE_THETA_GRID_STEP = 0.05
ADAPTIVE_RESPONSE_THRESHOLDS = (-1.0, 0.0, 1.0)
ADAPTIVE_BANK_PATH = Path(__file__).resolve().parents[2] / "data" / "adaptive_question_bank.json"
ADAPTIVE_PILOT_RESULTS_PATH = Path(__file__).resolve().parents[2] / "data" / "screening_results.json"

SECTION_BASE_DIFFICULTY = {
    "Depression": -0.2,
    "Anxiety": -0.1,
    "Stress": 0.0,
    "Sleep Disorder": 0.15,
    "Burnout": 0.1,
    "Loneliness": -0.05,
    "Substance Abuse": 0.25,
}


def _normalize_language(value: str | None) -> str:
    text = str(value or "").strip().lower()
    return LANGUAGE_ALIASES.get(text, "English")


def _localize_adaptive_section(section: str, language: str) -> str:
    if language == "English":
        return section
    return ADAPTIVE_SECTION_TRANSLATIONS.get(section, {}).get(language, section)


def _localize_adaptive_question(question: dict, language: str) -> dict:
    localized = dict(question)
    localized["prompt_en"] = question.get("prompt", "")
    localized["section_label"] = _localize_adaptive_section(str(question.get("section", "")), language)
    if language != "English":
        localized["prompt"] = ADAPTIVE_QUESTION_TRANSLATIONS.get(str(question.get("id", "")), {}).get(
            language,
            question.get("prompt", ""),
        )
    localized["language"] = language
    return localized


def _localize_question(question: dict, language: str) -> dict:
    localized = dict(question)
    localized["prompt_en"] = question.get("prompt", "")
    localized["section_label"] = _localize_adaptive_section(str(question.get("section", "")), language)
    if language != "English":
        localized["prompt"] = ADAPTIVE_QUESTION_TRANSLATIONS.get(str(question.get("id", "")), {}).get(
            language,
            question.get("prompt", ""),
        )
    localized["language"] = language
    return localized


def get_question_bank(language: str | None = None) -> list[dict]:
    normalized_language = _normalize_language(language)
    return [_localize_question(question, normalized_language) for question in QUESTION_BANK]


def get_response_options(language: str | None = None) -> dict[str, int]:
    normalized_language = _normalize_language(language)
    translations = RESPONSE_OPTION_TRANSLATIONS.get(normalized_language, RESPONSE_OPTION_TRANSLATIONS["English"])
    return {translations[label]: value for label, value in RESPONSE_OPTIONS.items()}


@lru_cache(maxsize=1)
def _load_adaptive_item_overrides() -> dict[str, dict]:
    if not ADAPTIVE_BANK_PATH.exists():
        return {}
    try:
        payload = json.loads(ADAPTIVE_BANK_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

    overrides: dict[str, dict] = {}
    if isinstance(payload, dict):
        items = payload.get("items") if isinstance(payload.get("items"), list) else payload.get("questions")
        if isinstance(items, list):
            candidates = items
        else:
            candidates = [payload]
    elif isinstance(payload, list):
        candidates = payload
    else:
        return {}

    for item in candidates:
        if not isinstance(item, dict):
            continue
        question_id = str(item.get("id") or "").strip()
        if not question_id:
            continue
        overrides[question_id] = {
            "a": item.get("a"),
            "b": item.get("b"),
            "section": item.get("section"),
            "domain": item.get("domain"),
        }
    return overrides


def _population_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean_value = average(values)
    variance = average([(float(value) - mean_value) ** 2 for value in values])
    return float(math.sqrt(max(variance, 0.0)))


@lru_cache(maxsize=1)
def _load_local_pilot_records() -> list[dict]:
    if not ADAPTIVE_PILOT_RESULTS_PATH.exists():
        return []
    try:
        payload = json.loads(ADAPTIVE_PILOT_RESULTS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []

    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        records = payload.get("records")
        if isinstance(records, list):
            return [item for item in records if isinstance(item, dict)]
        return [payload]
    return []


@lru_cache(maxsize=1)
def _adaptive_tuning() -> dict:
    records = _load_local_pilot_records()
    questionnaire_rows = []
    overall_scores = []

    for record in records:
        questionnaire = record.get("questionnaire")
        if not isinstance(questionnaire, dict):
            continue
        domain_scores = []
        for domain in PREDICTION_DOMAINS:
            raw_score = questionnaire.get(f"{domain}_score")
            if raw_score is None:
                continue
            score = normalize_score(raw_score)
            domain_scores.append(score)
        if not domain_scores:
            continue

        questionnaire_rows.append(questionnaire)
        overall_score = questionnaire.get("overall_score")
        if overall_score is None:
            overall_score = average(domain_scores)
        overall_scores.append(normalize_score(overall_score))

    if questionnaire_rows:
        per_domain_means = {
            domain: average(
                [normalize_score(row.get(f"{domain}_score", 0.0)) for row in questionnaire_rows if row.get(f"{domain}_score") is not None]
            )
            for domain in PREDICTION_DOMAINS
        }
        domain_balance = _population_std(list(per_domain_means.values()))
        overall_mean = average(overall_scores)
        overall_spread = _population_std(overall_scores)
        pilot_size = len(questionnaire_rows)
    else:
        per_domain_means = {domain: 0.0 for domain in PREDICTION_DOMAINS}
        domain_balance = 0.0
        overall_mean = 0.0
        overall_spread = 0.0
        pilot_size = 0

    info_threshold = 0.16 + (0.08 * (0.45 - overall_mean)) + (0.05 * domain_balance) + (0.01 * overall_spread)
    info_threshold = max(0.12, min(info_threshold, 0.24))

    coverage_weight = 0.18 + (0.35 * domain_balance) + (0.02 * min(pilot_size, 20) / 20.0) + (0.03 * overall_spread)
    coverage_weight = max(0.14, min(coverage_weight, 0.38))

    return {
        "info_threshold": round(info_threshold, 3),
        "coverage_weight": round(coverage_weight, 3),
        "pilot_size": pilot_size,
        "overall_mean": round(overall_mean, 3),
        "overall_spread": round(overall_spread, 3),
        "domain_balance": round(domain_balance, 3),
        "domain_means": {domain: round(score, 3) for domain, score in per_domain_means.items()},
        "source": str(ADAPTIVE_PILOT_RESULTS_PATH),
    }


def _logistic(value: float) -> float:
    exponent = max(min(-float(value), 60.0), -60.0)
    return 1.0 / (1.0 + math.exp(exponent))


def _response_category_probabilities(theta: float, discrimination: float, difficulty: float) -> list[float]:
    thresholds = [float(difficulty) + float(offset) for offset in ADAPTIVE_RESPONSE_THRESHOLDS]
    cumulative = [1.0]
    cumulative.extend(_logistic(discrimination * (theta - threshold)) for threshold in thresholds)
    cumulative.append(0.0)

    probabilities = [max(cumulative[index] - cumulative[index + 1], 1e-9) for index in range(len(cumulative) - 1)]
    total = sum(probabilities)
    if total <= 0.0:
        return [0.25, 0.25, 0.25, 0.25]
    return [probability / total for probability in probabilities]


def _theta_log_posterior(theta: float, responses: dict[str, int]) -> float:
    log_likelihood = 0.0
    for index, question in enumerate(QUESTION_BANK):
        value = responses.get(question["id"])
        if value is None:
            continue
        params = _question_parameters(question, index)
        category = int(max(0, min(3, int(value))))
        probabilities = _response_category_probabilities(theta, params["a"], params["b"])
        log_likelihood += math.log(probabilities[category])

    prior_scale = ADAPTIVE_THETA_PRIOR_SD
    log_prior = -0.5 * (theta / prior_scale) ** 2
    return log_likelihood + log_prior


def _domain_coverage_bonus(domain: str, answered_counts: dict[str, int], balance_weight: float | None = None) -> float:
    target_count = max(1.0, len(QUESTION_BANK) / max(len(PREDICTION_DOMAINS), 1))
    answered_count = float(answered_counts.get(domain, 0))
    coverage_gap = max(0.0, target_count - answered_count) / target_count
    weight = ADAPTIVE_DOMAIN_BALANCE_WEIGHT if balance_weight is None else float(balance_weight)
    return 1.0 + (weight * coverage_gap)


def _estimate_theta_grid(responses: dict[str, int]) -> float:
    best_theta = 0.0
    best_score = float("-inf")
    theta = ADAPTIVE_THETA_GRID_MIN
    while theta <= ADAPTIVE_THETA_GRID_MAX + 1e-9:
        score = _theta_log_posterior(theta, responses)
        if score > best_score:
            best_score = score
            best_theta = theta
        theta += ADAPTIVE_THETA_GRID_STEP

    refinement_start = max(ADAPTIVE_THETA_GRID_MIN, best_theta - ADAPTIVE_THETA_GRID_STEP)
    refinement_end = min(ADAPTIVE_THETA_GRID_MAX, best_theta + ADAPTIVE_THETA_GRID_STEP)
    theta = refinement_start
    while theta <= refinement_end + 1e-9:
        score = _theta_log_posterior(theta, responses)
        if score > best_score:
            best_score = score
            best_theta = theta
        theta += ADAPTIVE_THETA_GRID_STEP / 10.0

    return float(max(min(best_theta, ADAPTIVE_THETA_GRID_MAX), ADAPTIVE_THETA_GRID_MIN))


def score_questionnaire(responses: dict[str, int]) -> dict:
    domain_scores = {domain: [] for domain in PREDICTION_DOMAINS}

    for question in QUESTION_BANK:
        value = int(responses.get(question["id"], 0))
        domain_scores[question["domain"]].append(value / 3.0)

    result = {"available": True}
    normalized_scores = []
    for domain in PREDICTION_DOMAINS:
        score = average(domain_scores[domain])
        normalized = normalize_score(score)
        result[f"{domain}_score"] = normalized
        result[f"{domain}_risk"] = risk_level(score)
        normalized_scores.append(normalized)

    result["overall_score"] = normalize_score(average(normalized_scores))
    result["notes"] = (
        "Questionnaire scoring reflects self-reported frequency of emotional and functional symptoms "
        "over the last two weeks."
    )
    return result


def _question_parameters(question: dict, index: int) -> dict:
    section = str(question.get("section", "")).strip()
    section_offset = SECTION_BASE_DIFFICULTY.get(section, 0.0)
    within_section_step = 0.12 * (index % 3)
    discrimination = 1.0 + 0.15 * (index % 4)
    if question.get("domain") in {"depression", "anxiety", "stress"}:
        discrimination += 0.1
    override = _load_adaptive_item_overrides().get(question.get("id"), {})
    if override.get("a") is not None:
        discrimination = float(override["a"])
    if override.get("b") is not None:
        section_offset = float(override["b"])
        within_section_step = 0.0
    return {
        "a": round(discrimination, 3),
        "b": round(section_offset + within_section_step, 3),
    }


def _irt_probability(theta: float, discrimination: float, difficulty: float) -> float:
    exponent = -float(discrimination) * (float(theta) - float(difficulty))
    return 1.0 / (1.0 + math.exp(max(min(exponent, 60.0), -60.0)))


def _irt_information(theta: float, discrimination: float, difficulty: float) -> float:
    probability = _irt_probability(theta, discrimination, difficulty)
    return float((discrimination**2) * probability * (1.0 - probability))


def estimate_questionnaire_theta(responses: dict[str, int]) -> float:
    sanitized_responses = {key: int(value) for key, value in responses.items() if value is not None}
    if not sanitized_responses:
        return 0.0

    theta = _estimate_theta_grid(sanitized_responses)
    return float(max(min(theta, 3.0), -3.0))


def get_adaptive_tuning() -> dict:
    tuning = dict(_adaptive_tuning())
    tuning["defaults"] = {
        "info_threshold": ADAPTIVE_INFO_THRESHOLD,
        "coverage_weight": ADAPTIVE_DOMAIN_BALANCE_WEIGHT,
    }
    return tuning


def get_adaptive_question_bank(responses: dict[str, int] | None = None, language: str | None = None) -> dict:
    answered = dict(responses or {})
    answered_ids = {question_id for question_id, value in answered.items() if value is not None}
    theta = estimate_questionnaire_theta(answered)
    tuning = _adaptive_tuning()
    normalized_language = _normalize_language(language)
    response_options = [
        {"label": label, "value": value}
        for label, value in get_response_options(normalized_language).items()
    ]
    answered_counts = {domain: 0 for domain in PREDICTION_DOMAINS}
    for question in QUESTION_BANK:
        if question["id"] in answered_ids:
            answered_counts[question["domain"]] += 1
    scored_questions = []
    for index, question in enumerate(QUESTION_BANK):
        if question["id"] in answered_ids:
            continue
        params = _question_parameters(question, index)
        information = _irt_information(theta, params["a"], params["b"])
        coverage_bonus = _domain_coverage_bonus(question["domain"], answered_counts, tuning["coverage_weight"])
        selection_score = information * coverage_bonus
        scored_questions.append(
            {
                **_localize_adaptive_question(question, normalized_language),
                "irt": {
                    "discrimination": params["a"],
                    "difficulty": params["b"],
                    "information": round(information, 6),
                },
                "adaptive": {
                    "selection_score": round(selection_score, 6),
                    "coverage_bonus": round(coverage_bonus, 6),
                    "answered_in_domain": answered_counts[question["domain"]],
                },
            }
        )

    scored_questions.sort(
        key=lambda item: (
            item["adaptive"]["selection_score"],
            item["irt"]["information"],
        ),
        reverse=True,
    )
    next_question = scored_questions[0] if scored_questions else None
    max_information = max((item["irt"]["information"] for item in scored_questions), default=0.0)
    selected_information = next_question["irt"]["information"] if next_question else 0.0
    should_stop = (
        len(answered_ids) >= ADAPTIVE_MAX_ITEMS
        or (len(answered_ids) >= ADAPTIVE_MIN_ITEMS and max_information < tuning["info_threshold"])
        or next_question is None
    )
    return {
        "theta": round(theta, 6),
        "answered_count": len(answered_ids),
        "remaining_count": len(scored_questions),
        "next_question": next_question,
        "should_stop": should_stop,
        "max_information": round(max_information, 6),
        "selected_information": round(selected_information, 6),
        "tuning": tuning,
        "remaining_questions": scored_questions,
        "response_options": response_options,
        "choose_one_label": ADAPTIVE_CHOOSE_ONE_TRANSLATIONS.get(normalized_language, ADAPTIVE_CHOOSE_ONE_TRANSLATIONS["English"]),
        "language": normalized_language,
    }


def score_adaptive_questionnaire(responses: dict[str, int]) -> dict:
    theta = estimate_questionnaire_theta(responses)
    domain_scores = {domain: [] for domain in PREDICTION_DOMAINS}

    for index, question in enumerate(QUESTION_BANK):
        params = _question_parameters(question, index)
        value = responses.get(question["id"])
        if value is None:
            expected_distribution = _response_category_probabilities(theta, params["a"], params["b"])
            expected_response = sum(category * probability for category, probability in enumerate(expected_distribution))
            score_value = normalize_score(expected_response / 3.0)
        else:
            score_value = normalize_score(int(value) / 3.0)
        domain_scores[question["domain"]].append(score_value)

    result = {"available": True, "adaptive": True, "theta": round(theta, 6)}
    normalized_scores = []
    for domain in PREDICTION_DOMAINS:
        score = average(domain_scores[domain])
        normalized = normalize_score(score)
        result[f"{domain}_score"] = normalized
        result[f"{domain}_risk"] = risk_level(score)
        normalized_scores.append(normalized)

    result["overall_score"] = normalize_score(average(normalized_scores))
    result["answered_count"] = len([value for value in responses.values() if value is not None])
    result["notes"] = (
        "Adaptive questionnaire scoring uses a lightweight IRT-style selector and estimates the remaining "
        "unasked items from the current latent trait."
    )
    return result
