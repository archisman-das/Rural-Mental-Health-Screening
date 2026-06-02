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


def get_question_bank() -> list[dict]:
    return QUESTION_BANK


def get_response_options() -> dict[str, int]:
    return RESPONSE_OPTIONS


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
