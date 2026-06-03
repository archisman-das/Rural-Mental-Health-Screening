import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st

ROOT = Path(__file__).resolve().parent
SYS_PATH = str(ROOT / "src")
if SYS_PATH not in sys.path:
    sys.path.append(SYS_PATH)

from mental_health_screening.assessment import (
    get_adaptive_question_bank,
    get_question_bank,
    get_response_options,
    score_adaptive_questionnaire,
    score_questionnaire,
)
from mental_health_screening.constants import PREDICTION_LABELS
from mental_health_screening.constants import PREDICTION_DOMAINS
from mental_health_screening.feature_extract import save_upload_file
from mental_health_screening.predict import screen
from mental_health_screening.report import create_assessment_pdf_bytes
from mental_health_screening.storage import (
    build_assessment_trajectory,
    create_assessment_record,
    fetch_assessment_record,
    get_database_metadata,
)


st.set_page_config(page_title="Rural Mental Health Screening", page_icon="MH", layout="wide")

with st.sidebar:
    st.selectbox(ui_text("interface_language"), ["English", "Hindi", "Bengali"], key="ui_language")

ADAPTIVE_API_BASE_URL = os.environ.get("DASHBOARD_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
ADAPTIVE_API_TIMEOUT_SECONDS = 10
MAIN_AUDIO_UPLOAD_KEY = "online_audio_file"
MAIN_IMAGE_UPLOAD_KEY = "online_image_file"
MAIN_PASSIVE_VIDEO_UPLOAD_KEY = "online_passive_video_file"
MAIN_TYPING_EVENTS_KEY = "online_typing_events_raw"

UI_TRANSLATIONS = {
    "English": {
        "interface_language": "Interface language",
        "app_title": "Rural Mental Health Screening AI",
        "app_description": "A web-based screening system for rural mental health outreach. Users can complete an online test, submit optional speech and image inputs, and fetch saved results later using an assessment ID.",
        "prediction_scope": "Current prediction scope: Depression, Anxiety, Stress, Sleep Disorder, Burnout, Loneliness, and Substance Abuse.",
        "frontend_info": "Frontend: Streamlit | NLP backend: multilingual transformer pipeline with English BERT-family models plus MuRIL/Indic-BERT support for Hindi and Bengali",
        "database_info": "Database: {database} | Stored records: {total_records} | Audit logs: {total_audit_logs} | Encryption at rest: {encryption_at_rest}",
        "workflow_intro": "- Use the `Take Online Test` tab to conduct a structured screening session.\n- The system stores the result and generates an assessment ID.\n- Use the `Fetch Result` tab to retrieve the result later for the end user.",
        "prototype_notice": "This is a screening and triage prototype only. It should support, not replace, a clinician or trained community health worker.",
        "tab_online": "Take Online Test",
        "tab_adaptive": "Adaptive Test",
        "tab_fetch": "Fetch Result",
        "online_title": "Online Mental Health Test",
        "online_caption": "Complete the questionnaire below, then optionally add speech and facial inputs.",
        "candidate_profile": "Candidate Profile",
        "full_name": "Full name",
        "age": "Age",
        "gender": "Gender",
        "gender_option_prefer_not": "Prefer not to say",
        "gender_option_female": "Female",
        "gender_option_male": "Male",
        "gender_option_other": "Other",
        "village": "Village / Local area",
        "phone": "Phone or reference number",
        "assessor": "Assessor / Health worker name",
        "preferred_language": "Preferred language",
        "consent": "Consent received for screening and optional uploads",
        "questionnaire": "Symptom Questionnaire",
        "optional_inputs": "Optional AI Inputs",
        "describe_feeling": "Describe how you have been feeling recently",
        "describe_placeholder": "Example: I have been feeling tense, low on energy, and unable to sleep properly.",
        "voice_sample": "Upload a short voice sample",
        "voice_help": "Best if 15 to 30 seconds, recorded in a quiet place.",
        "face_image": "Upload a face image",
        "image_help": "Front-facing image with clear lighting, only if consent is available.",
        "phone_video": "Upload a phone-camera video",
        "video_help": "Optional short clip for rPPG-style heart-rate estimation.",
        "typing_rhythm": "Typing rhythm input",
        "typing_placeholder": 'Paste typing intervals as JSON like {"intervals_ms":[180,240,210]} or comma-separated numbers.',
        "submit_assessment": "Submit Assessment",
        "assessment_submitted": "Assessment submitted successfully.",
        "use_assessment_id": "Use this assessment ID in the Fetch Result tab to retrieve the stored result later.",
        "online_consent_required": "Please confirm consent before submitting the online screening.",
        "adaptive_title": "Adaptive IRT Screening",
        "adaptive_caption": "This mode asks the next most informative question based on prior answers.",
        "answered_questions": "Answered questions",
        "estimated_theta": "Estimated theta",
        "remaining_items": "Remaining candidate items",
        "top_information": "Top item information",
        "adaptive_profile": "Candidate Profile",
        "adaptive_question": "Adaptive Question",
        "select_one_answer": "Select one answer",
        "adaptive_optional_inputs": "Optional AI Inputs",
        "reuse_media": "This tab reuses the media uploaded in the main screening tab.",
        "finalize_assessment": "Finalize Assessment",
        "submit_answer": "Submit Answer",
        "adaptive_completed": "Adaptive assessment completed.",
        "adaptive_submitted": "Adaptive assessment submitted successfully.",
        "adaptive_ready_finalize": "The adaptive selector has enough information to finalize.",
        "consent_required": "Please confirm consent before continuing.",
        "adaptive_api_unavailable": "Adaptive API unavailable right now. Falling back to the local selector for this step.",
        "please_choose_answer": "Please choose an answer before continuing.",
        "start_new_adaptive": "Start a new adaptive assessment",
        "adaptive_section": "Section",
        "adaptive_irt_info": "IRT info",
        "adaptive_difficulty": "Difficulty",
        "adaptive_selection_score": "Selection score",
        "adaptive_coverage_bonus": "Coverage bonus",
        "adaptive_stop_threshold": "Stop threshold",
        "adaptive_balance_weight": "Balance weight",
        "pilot_records": "Pilot records",
        "fetch_saved": "Fetch Saved Result",
        "enter_assessment_id": "Enter assessment ID",
        "assessment_id_placeholder": "Example: MHS-1A2B3C4D",
        "fetch_button": "Fetch Assessment Result",
        "enter_valid_id": "Please enter a valid assessment ID.",
        "assessment_found": "Assessment found: {assessment_id}",
        "submitted_at": "Submitted at {created_at}",
        "questionnaire_result": "Questionnaire Result",
        "overall_score": "Overall Score",
        "multimodal_result": "Multimodal Screening Result",
        "confidence": "Confidence",
        "top_comorbidity_pair": "Top comorbidity pair: {pair} ({probability:.2f})",
        "recommendation": "Recommendation",
        "longitudinal_trajectory": "Longitudinal Trajectory",
        "trend_status": "Trend Status",
        "no_trend_summary": "No trend summary available.",
        "history_count": "History count",
        "baseline_change": "Baseline change",
        "recent_change": "Recent change",
        "unavailable": "Unavailable",
        "download_pdf": "Download PDF Report",
        "candidate_profile_result": "Candidate Profile",
        "assessment_id_report": "Use this assessment ID in the Fetch Result tab to retrieve the stored result later.",
    },
    "Hindi": {
        "interface_language": "इंटरफ़ेस भाषा",
        "app_title": "ग्रामीण मानसिक स्वास्थ्य स्क्रीनिंग AI",
        "app_description": "ग्रामीण मानसिक स्वास्थ्य पहुँच के लिए एक वेब-आधारित स्क्रीनिंग प्रणाली। उपयोगकर्ता ऑनलाइन टेस्ट पूरा कर सकते हैं, वैकल्पिक आवाज़ और छवि इनपुट दे सकते हैं, और बाद में आकलन ID से परिणाम देख सकते हैं।",
        "prediction_scope": "वर्तमान पूर्वानुमान क्षेत्र: डिप्रेशन, एंग्जायटी, तनाव, नींद संबंधी समस्या, बर्नआउट, अकेलापन, और पदार्थ दुरुपयोग।",
        "frontend_info": "फ्रंटएंड: Streamlit | NLP बैकएंड: बहुभाषी ट्रांसफॉर्मर पाइपलाइन, अंग्रेज़ी BERT-परिवार मॉडलों के साथ Hindi और Bengali के लिए MuRIL/Indic-BERT समर्थन",
        "database_info": "डेटाबेस: {database} | संग्रहीत रिकॉर्ड: {total_records} | ऑडिट लॉग: {total_audit_logs} | एट-रेस्ट एन्क्रिप्शन: {encryption_at_rest}",
        "workflow_intro": "- संरचित स्क्रीनिंग सत्र के लिए `Take Online Test` टैब का उपयोग करें।\n- सिस्टम परिणाम सहेजता है और एक आकलन ID बनाता है।\n- बाद में परिणाम देखने के लिए `Fetch Result` टैब का उपयोग करें।",
        "prototype_notice": "यह केवल एक स्क्रीनिंग और ट्रायेज प्रोटोटाइप है। इसे किसी चिकित्सक या प्रशिक्षित समुदाय स्वास्थ्य कार्यकर्ता का समर्थन करना चाहिए, उन्हें बदलना नहीं चाहिए।",
        "tab_online": "ऑनलाइन टेस्ट",
        "tab_adaptive": "अनुकूली टेस्ट",
        "tab_fetch": "परिणाम प्राप्त करें",
        "online_title": "ऑनलाइन मानसिक स्वास्थ्य टेस्ट",
        "online_caption": "नीचे प्रश्नावली पूरी करें, फिर चाहें तो आवाज़ और चेहरे के इनपुट जोड़ें।",
        "candidate_profile": "उम्मीदवार प्रोफ़ाइल",
        "full_name": "पूरा नाम",
        "age": "आयु",
        "gender": "लिंग",
        "gender_option_prefer_not": "कहना नहीं चाहते",
        "gender_option_female": "महिला",
        "gender_option_male": "पुरुष",
        "gender_option_other": "अन्य",
        "village": "गाँव / स्थानीय क्षेत्र",
        "phone": "फ़ोन या संदर्भ संख्या",
        "assessor": "आकलनकर्ता / स्वास्थ्य कर्मी का नाम",
        "preferred_language": "पसंदीदा भाषा",
        "consent": "स्क्रीनिंग और वैकल्पिक अपलोड के लिए सहमति प्राप्त हुई",
        "questionnaire": "लक्षण प्रश्नावली",
        "optional_inputs": "वैकल्पिक AI इनपुट",
        "describe_feeling": "हाल ही में आप कैसा महसूस कर रहे हैं, इसका वर्णन करें",
        "describe_placeholder": "उदाहरण: मैं तनावग्रस्त, कम ऊर्जा वाला, और ठीक से सो न पाने वाला महसूस कर रहा हूँ।",
        "voice_sample": "छोटा वॉइस सैंपल अपलोड करें",
        "voice_help": "15 से 30 सेकंड बेहतर, किसी शांत जगह पर रिकॉर्ड किया गया।",
        "face_image": "चेहरे की छवि अपलोड करें",
        "image_help": "साफ़ रोशनी वाली सामने की छवि, केवल सहमति होने पर।",
        "phone_video": "फ़ोन-कैमरा वीडियो अपलोड करें",
        "video_help": "rPPG-शैली हृदय-गति अनुमान के लिए वैकल्पिक छोटा क्लिप।",
        "typing_rhythm": "टाइपिंग रिद्म इनपुट",
        "typing_placeholder": 'टाइपिंग अंतराल JSON जैसे {"intervals_ms":[180,240,210]} या कॉमा से अलग संख्याओं के रूप में पेस्ट करें।',
        "submit_assessment": "आकलन जमा करें",
        "assessment_submitted": "आकलन सफलतापूर्वक जमा हो गया।",
        "use_assessment_id": "सहेजे गए परिणाम को बाद में देखने के लिए Fetch Result टैब में इस आकलन ID का उपयोग करें।",
        "online_consent_required": "ऑनलाइन स्क्रीनिंग जमा करने से पहले कृपया सहमति की पुष्टि करें।",
        "adaptive_title": "अनुकूली IRT स्क्रीनिंग",
        "adaptive_caption": "यह मोड पिछले उत्तरों के आधार पर अगला सबसे सूचनात्मक प्रश्न पूछता है।",
        "answered_questions": "उत्तर दिए गए प्रश्न",
        "estimated_theta": "अनुमानित थीटा",
        "remaining_items": "शेष उम्मीदवार आइटम",
        "top_information": "शीर्ष आइटम सूचना",
        "adaptive_profile": "उम्मीदवार प्रोफ़ाइल",
        "adaptive_question": "अनुकूली प्रश्न",
        "select_one_answer": "एक उत्तर चुनें",
        "adaptive_optional_inputs": "वैकल्पिक AI इनपुट",
        "reuse_media": "यह टैब मुख्य स्क्रीनिंग टैब में अपलोड किए गए मीडिया का पुन: उपयोग करता है।",
        "finalize_assessment": "आकलन अंतिम करें",
        "submit_answer": "उत्तर जमा करें",
        "adaptive_completed": "अनुकूली आकलन पूरा हुआ।",
        "adaptive_submitted": "अनुकूली आकलन सफलतापूर्वक जमा हो गया।",
        "adaptive_ready_finalize": "अनुकूली चयनकर्ता के पास अंतिम करने के लिए पर्याप्त जानकारी है।",
        "consent_required": "आगे बढ़ने से पहले कृपया सहमति की पुष्टि करें।",
        "adaptive_api_unavailable": "Adaptive API अभी उपलब्ध नहीं है। इस चरण के लिए स्थानीय चयनकर्ता का उपयोग किया जा रहा है।",
        "please_choose_answer": "कृपया आगे बढ़ने से पहले एक उत्तर चुनें।",
        "start_new_adaptive": "नया अनुकूली आकलन शुरू करें",
        "adaptive_section": "अनुभाग",
        "adaptive_irt_info": "IRT जानकारी",
        "adaptive_difficulty": "कठिनाई",
        "adaptive_selection_score": "चयन स्कोर",
        "adaptive_coverage_bonus": "कवरेज बोनस",
        "adaptive_stop_threshold": "रोकने की सीमा",
        "adaptive_balance_weight": "संतुलन भार",
        "pilot_records": "पायलट रिकॉर्ड",
        "fetch_saved": "सहेजा गया परिणाम प्राप्त करें",
        "enter_assessment_id": "आकलन ID दर्ज करें",
        "assessment_id_placeholder": "उदाहरण: MHS-1A2B3C4D",
        "fetch_button": "आकलन परिणाम प्राप्त करें",
        "enter_valid_id": "कृपया एक मान्य आकलन ID दर्ज करें।",
        "assessment_found": "आकलन मिला: {assessment_id}",
        "submitted_at": "सबमिट समय: {created_at}",
        "questionnaire_result": "प्रश्नावली परिणाम",
        "overall_score": "कुल स्कोर",
        "multimodal_result": "बहु-माध्यमी स्क्रीनिंग परिणाम",
        "confidence": "विश्वसनीयता",
        "top_comorbidity_pair": "शीर्ष सह-रुग्णता जोड़ी: {pair} ({probability:.2f})",
        "recommendation": "सिफारिश",
        "longitudinal_trajectory": "दीर्घकालिक प्रगति",
        "trend_status": "रुझान स्थिति",
        "no_trend_summary": "कोई रुझान सारांश उपलब्ध नहीं है।",
        "history_count": "इतिहास संख्या",
        "baseline_change": "आधार परिवर्तन",
        "recent_change": "हालिया परिवर्तन",
        "unavailable": "उपलब्ध नहीं",
        "download_pdf": "PDF रिपोर्ट डाउनलोड करें",
        "candidate_profile_result": "उम्मीदवार प्रोफ़ाइल",
        "assessment_id_report": "सहेजे गए परिणाम को बाद में देखने के लिए Fetch Result टैब में इस आकलन ID का उपयोग करें।",
    },
    "Bengali": {
        "interface_language": "ইন্টারফেস ভাষা",
        "app_title": "গ্রামীণ মানসিক স্বাস্থ্য স্ক্রিনিং AI",
        "app_description": "গ্রামীণ মানসিক স্বাস্থ্য সহায়তার জন্য একটি ওয়েব-ভিত্তিক স্ক্রিনিং সিস্টেম। ব্যবহারকারীরা অনলাইন টেস্ট সম্পূর্ণ করতে পারেন, ঐচ্ছিক কণ্ঠস্বর ও ছবি ইনপুট দিতে পারেন, এবং পরে assessment ID দিয়ে ফলাফল দেখতে পারেন।",
        "prediction_scope": "বর্তমান পূর্বাভাস ক্ষেত্র: Depression, Anxiety, Stress, Sleep Disorder, Burnout, Loneliness, এবং Substance Abuse.",
        "frontend_info": "Frontend: Streamlit | NLP backend: বহুভাষিক transformer pipeline, English BERT-family models এর সাথে Hindi এবং Bengali-এর জন্য MuRIL/Indic-BERT support",
        "database_info": "Database: {database} | Stored records: {total_records} | Audit logs: {total_audit_logs} | Encryption at rest: {encryption_at_rest}",
        "workflow_intro": "- structured screening session চালাতে `Take Online Test` tab ব্যবহার করুন।\n- System result save করে এবং একটি assessment ID তৈরি করে।\n- পরে result দেখতে `Fetch Result` tab ব্যবহার করুন।",
        "prototype_notice": "এটি শুধুমাত্র একটি screening এবং triage prototype। এটি clinician বা trained community health worker-এর বিকল্প নয়, বরং সহায়ক হওয়া উচিত।",
        "tab_online": "অনলাইন টেস্ট",
        "tab_adaptive": "অ্যাডাপটিভ টেস্ট",
        "tab_fetch": "ফলাফল আনুন",
        "online_title": "অনলাইন মানসিক স্বাস্থ্য টেস্ট",
        "online_caption": "নীচের questionnaire সম্পূর্ণ করুন, তারপর চাইলে voice এবং image input যোগ করুন।",
        "candidate_profile": "প্রার্থী প্রোফাইল",
        "full_name": "পূর্ণ নাম",
        "age": "বয়স",
        "gender": "লিঙ্গ",
        "gender_option_prefer_not": "বলতে চাই না",
        "gender_option_female": "মহিলা",
        "gender_option_male": "পুরুষ",
        "gender_option_other": "অন্যান্য",
        "village": "গ্রাম / স্থানীয় এলাকা",
        "phone": "ফোন বা রেফারেন্স নম্বর",
        "assessor": "মূল্যায়নকারী / স্বাস্থ্যকর্মীর নাম",
        "preferred_language": "পছন্দের ভাষা",
        "consent": "স্ক্রিনিং এবং ঐচ্ছিক আপলোডের জন্য সম্মতি নেওয়া হয়েছে",
        "questionnaire": "লক্ষণ প্রশ্নাবলী",
        "optional_inputs": "ঐচ্ছিক AI ইনপুট",
        "describe_feeling": "সাম্প্রতিক সময়ে আপনি কেমন অনুভব করছেন তা বর্ণনা করুন",
        "describe_placeholder": "উদাহরণ: আমি টানটান, শক্তি কম, এবং ঠিকমতো ঘুমাতে পারছি না বলে অনুভব করছি।",
        "voice_sample": "ছোট voice sample আপলোড করুন",
        "voice_help": "15 থেকে 30 সেকেন্ড, শান্ত জায়গায় রেকর্ড করা হলে ভাল।",
        "face_image": "face image আপলোড করুন",
        "image_help": "সামনে মুখ করা, পরিষ্কার আলোতে তোলা ছবি, শুধুমাত্র সম্মতি থাকলে।",
        "phone_video": "phone-camera ভিডিও আপলোড করুন",
        "video_help": "rPPG-style heart-rate estimation-এর জন্য ঐচ্ছিক ছোট ক্লিপ।",
        "typing_rhythm": "Typing rhythm input",
        "typing_placeholder": 'Typing intervals JSON যেমন {"intervals_ms":[180,240,210]} অথবা comma-separated সংখ্যা হিসেবে পেস্ট করুন।',
        "submit_assessment": "মূল্যায়ন জমা দিন",
        "assessment_submitted": "মূল্যায়ন সফলভাবে জমা হয়েছে।",
        "use_assessment_id": "সংরক্ষিত ফলাফল পরে দেখতে Fetch Result tab-এ এই assessment ID ব্যবহার করুন।",
        "online_consent_required": "অনলাইন screening জমা দেওয়ার আগে অনুগ্রহ করে সম্মতি নিশ্চিত করুন।",
        "adaptive_title": "অ্যাডাপটিভ IRT স্ক্রিনিং",
        "adaptive_caption": "এই mode আগের উত্তরের ভিত্তিতে পরের সবচেয়ে তথ্যবহুল প্রশ্নটি জিজ্ঞাসা করে।",
        "answered_questions": "উত্তর দেওয়া প্রশ্ন",
        "estimated_theta": "আনুমানিক theta",
        "remaining_items": "বাকি candidate item",
        "top_information": "শীর্ষ item information",
        "adaptive_profile": "প্রার্থী প্রোফাইল",
        "adaptive_question": "অ্যাডাপটিভ প্রশ্ন",
        "select_one_answer": "একটি উত্তর নির্বাচন করুন",
        "adaptive_optional_inputs": "ঐচ্ছিক AI ইনপুট",
        "reuse_media": "এই tab প্রধান screening tab-এ আপলোড করা media পুনঃব্যবহার করে।",
        "finalize_assessment": "মূল্যায়ন চূড়ান্ত করুন",
        "submit_answer": "উত্তর জমা দিন",
        "adaptive_completed": "অ্যাডাপটিভ মূল্যায়ন সম্পূর্ণ হয়েছে।",
        "adaptive_submitted": "অ্যাডাপটিভ মূল্যায়ন সফলভাবে জমা হয়েছে।",
        "adaptive_ready_finalize": "অ্যাডাপটিভ selector-এর কাছে final করার জন্য যথেষ্ট তথ্য আছে।",
        "consent_required": "এগোনোর আগে অনুগ্রহ করে সম্মতি নিশ্চিত করুন।",
        "adaptive_api_unavailable": "Adaptive API এখনই উপলব্ধ নয়। এই ধাপের জন্য local selector ব্যবহার করা হচ্ছে।",
        "please_choose_answer": "এগোনোর আগে একটি উত্তর নির্বাচন করুন।",
        "start_new_adaptive": "নতুন অ্যাডাপটিভ মূল্যায়ন শুরু করুন",
        "adaptive_section": "অধ্যায়",
        "adaptive_irt_info": "IRT তথ্য",
        "adaptive_difficulty": "কঠিনতা",
        "adaptive_selection_score": "নির্বাচন স্কোর",
        "adaptive_coverage_bonus": "কভারেজ বোনাস",
        "adaptive_stop_threshold": "থামার সীমা",
        "adaptive_balance_weight": "সামঞ্জস্য ওজন",
        "pilot_records": "পাইলট রেকর্ড",
        "fetch_saved": "সংরক্ষিত ফলাফল আনুন",
        "enter_assessment_id": "assessment ID লিখুন",
        "assessment_id_placeholder": "উদাহরণ: MHS-1A2B3C4D",
        "fetch_button": "মূল্যায়ন ফলাফল আনুন",
        "enter_valid_id": "অনুগ্রহ করে একটি বৈধ assessment ID লিখুন।",
        "assessment_found": "মূল্যায়ন পাওয়া গেছে: {assessment_id}",
        "submitted_at": "জমার সময়: {created_at}",
        "questionnaire_result": "প্রশ্নাবলী ফলাফল",
        "overall_score": "সামগ্রিক স্কোর",
        "multimodal_result": "বহুমাধ্যমিক স্ক্রিনিং ফলাফল",
        "confidence": "আস্থা",
        "top_comorbidity_pair": "শীর্ষ comorbidity pair: {pair} ({probability:.2f})",
        "recommendation": "সুপারিশ",
        "longitudinal_trajectory": "দীর্ঘমেয়াদি trajectory",
        "trend_status": "ট্রেন্ডের অবস্থা",
        "no_trend_summary": "কোনো ট্রেন্ড সারাংশ পাওয়া যায়নি।",
        "history_count": "ইতিহাস সংখ্যা",
        "baseline_change": "বেসলাইন পরিবর্তন",
        "recent_change": "সাম্প্রতিক পরিবর্তন",
        "unavailable": "অনুপলব্ধ",
        "download_pdf": "PDF রিপোর্ট ডাউনলোড করুন",
        "candidate_profile_result": "প্রার্থী প্রোফাইল",
        "assessment_id_report": "সংরক্ষিত ফলাফল পরে দেখতে Fetch Result tab-এ এই assessment ID ব্যবহার করুন।",
    },
}

st.session_state.setdefault("ui_language", "English")


def ui_language() -> str:
    return st.session_state.get("ui_language", "English")


def ui_text(key: str, **kwargs) -> str:
    language = ui_language()
    template = UI_TRANSLATIONS.get(language, UI_TRANSLATIONS["English"]).get(key, UI_TRANSLATIONS["English"].get(key, key))
    return template.format(**kwargs) if kwargs else template


def cleanup_temp_file(path: str | None) -> None:
    if path and os.path.exists(path):
        os.remove(path)


def parse_typing_events(raw_value: str | None):
    if not raw_value:
        return None
    text = raw_value.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, (dict, list)):
            return parsed
    except Exception:
        pass
    intervals = []
    for chunk in text.replace("\n", ",").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            intervals.append(float(chunk))
        except ValueError:
            continue
    return {"intervals_ms": intervals} if intervals else None


def fetch_adaptive_question_bank_from_api(responses: dict[str, int], language: str | None = None) -> dict:
    payload = json.dumps({"responses": responses, "language": language}).encode("utf-8")
    request = Request(
        f"{ADAPTIVE_API_BASE_URL}/api/adaptive/next",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=ADAPTIVE_API_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def resolve_adaptive_upload(primary_key: str, fallback_key: str):
    primary_upload = st.session_state.get(primary_key)
    if primary_upload is not None:
        return primary_upload
    return st.session_state.get(fallback_key)


def reset_adaptive_state() -> None:
    st.session_state["adaptive_responses"] = {}
    st.session_state["adaptive_completed"] = False
    st.session_state["adaptive_last_record"] = None
    st.session_state["adaptive_last_question_id"] = None
    st.session_state["adaptive_theta"] = 0.0
    st.session_state.setdefault("adaptive_language", "English")


def initialize_adaptive_state() -> None:
    if "adaptive_responses" not in st.session_state:
        reset_adaptive_state()


def render_domain_metrics(result: dict, suffix: str) -> None:
    columns = st.columns(3)
    for index, domain in enumerate(PREDICTION_DOMAINS):
        key = domain if not suffix else f"{domain}_{suffix}"
        columns[index % 3].metric(
            PREDICTION_LABELS[domain],
            str(result[key]).capitalize() if suffix == "risk" else str(result[key]).capitalize(),
        )


def render_result_view(record: dict) -> None:
    questionnaire = record["questionnaire"]
    multimodal = record["multimodal"]
    overall = multimodal["overall"]
    trajectory = build_assessment_trajectory(record["assessment_id"])

    st.success(ui_text("assessment_found", assessment_id=record["assessment_id"]))
    st.caption(ui_text("submitted_at", created_at=record["created_at"]))

    st.subheader(ui_text("candidate_profile_result"))
    st.json(record["profile"])

    st.subheader(ui_text("questionnaire_result"))
    render_domain_metrics(questionnaire, "risk")
    st.metric(ui_text("overall_score"), f"{questionnaire['overall_score']:.2f}")

    st.subheader(ui_text("multimodal_result"))
    render_domain_metrics(overall, "")
    st.metric(ui_text("confidence"), f"{overall['confidence']:.0%}")
    comorbidity = multimodal.get("comorbidity") or {}
    top_pairs = comorbidity.get("top_pairs") or []
    if top_pairs:
        top_pair = top_pairs[0]
        pair_domains = top_pair.get("domains") or []
        if len(pair_domains) == 2:
            pair_label = f"{pair_domains[0].replace('_', ' ').title()} + {pair_domains[1].replace('_', ' ').title()}"
            st.caption(ui_text("top_comorbidity_pair", pair=pair_label, probability=float(top_pair.get("probability", 0.0) or 0.0)))

    score_cols = st.columns(2)
    left_domains = PREDICTION_DOMAINS[::2]
    right_domains = PREDICTION_DOMAINS[1::2]
    for domain in left_domains:
        score_cols[0].progress(overall["scores"][domain], text=f"{PREDICTION_LABELS[domain]} score")
    for domain in right_domains:
        score_cols[1].progress(overall["scores"][domain], text=f"{PREDICTION_LABELS[domain]} score")

    st.subheader(ui_text("recommendation"))
    st.write(multimodal["recommendation"])
    st.caption(multimodal["disclaimer"])

    if trajectory:
        st.subheader(ui_text("longitudinal_trajectory"))
        st.metric(ui_text("trend_status"), trajectory.get("status_label", ui_text("unavailable")))
        st.write(trajectory.get("summary", ui_text("no_trend_summary")))
        st.caption(
            f"{ui_text('history_count')}: {trajectory.get('history_count', 0)} | "
            f"{ui_text('baseline_change')}: {trajectory.get('change_from_baseline', 0):.2f} | "
            f"{ui_text('recent_change')}: {trajectory.get('change_from_previous', 0):.2f}"
        )

    pdf_bytes = create_assessment_pdf_bytes(record)
    st.download_button(
        ui_text("download_pdf"),
        data=pdf_bytes,
        file_name=f"{record['assessment_id']}_report.pdf",
        mime="application/pdf",
    )


st.title(ui_text("app_title"))
st.write(ui_text("app_description"))
st.caption(ui_text("prediction_scope"))

stack_col, db_col = st.columns(2)
with stack_col:
    st.info(ui_text("frontend_info"))
with db_col:
    metadata = get_database_metadata()
    st.info(
        ui_text(
            "database_info",
            database=metadata["database"],
            total_records=metadata["total_records"],
            total_audit_logs=metadata.get("total_audit_logs", 0),
            encryption_at_rest=metadata.get("encryption_at_rest", False),
        )
    )

intro_left, intro_right = st.columns([1.3, 1.0])
with intro_left:
    st.markdown(
        ui_text("workflow_intro")
    )
with intro_right:
    st.info(ui_text("prototype_notice"))

test_tab, adaptive_tab, fetch_tab = st.tabs([ui_text("tab_online"), ui_text("tab_adaptive"), ui_text("tab_fetch")])

with test_tab:
    st.subheader(ui_text("online_title"))
    st.caption(ui_text("online_caption"))

    with st.form("online_screening_form"):
        profile_col, context_col = st.columns(2)

        with profile_col:
            full_name = st.text_input(ui_text("full_name"))
            age = st.number_input(ui_text("age"), min_value=10, max_value=100, value=25)
            gender = st.selectbox(
                ui_text("gender"),
                [
                    ui_text("gender_option_prefer_not"),
                    ui_text("gender_option_female"),
                    ui_text("gender_option_male"),
                    ui_text("gender_option_other"),
                ],
            )
            village = st.text_input(ui_text("village"))

        with context_col:
            phone = st.text_input(ui_text("phone"))
            assessor = st.text_input(ui_text("assessor"))
            language = st.selectbox(ui_text("preferred_language"), ["English", "Hindi", "Bengali", "Other"])
            consent = st.checkbox(ui_text("consent"))

        st.markdown(f"### {ui_text('questionnaire')}")
        questionnaire_bank = get_question_bank(language)
        response_options = list(get_response_options(language).keys())
        questionnaire_answers = {}
        current_section = None
        for question in questionnaire_bank:
            if question["section"] != current_section:
                current_section = question["section"]
                st.markdown(f"#### {question.get('section_label', current_section)}")
            questionnaire_answers[question["id"]] = st.radio(
                question["prompt"],
                response_options,
                horizontal=True,
            )

        st.markdown(f"### {ui_text('optional_inputs')}")
        text_input = st.text_area(
            ui_text("describe_feeling"),
            height=180,
            placeholder=ui_text("describe_placeholder"),
        )
        audio_file = st.file_uploader(
            ui_text("voice_sample"),
            type=["wav", "mp3", "m4a"],
            help=ui_text("voice_help"),
            key=MAIN_AUDIO_UPLOAD_KEY,
        )
        image_file = st.file_uploader(
            ui_text("face_image"),
            type=["png", "jpg", "jpeg"],
            help=ui_text("image_help"),
            key=MAIN_IMAGE_UPLOAD_KEY,
        )
        passive_video_file = st.file_uploader(
            ui_text("phone_video"),
            type=["mp4", "mov", "avi", "m4v"],
            help=ui_text("video_help"),
            key=MAIN_PASSIVE_VIDEO_UPLOAD_KEY,
        )
        typing_events_raw = st.text_area(
            ui_text("typing_rhythm"),
            height=100,
            placeholder=ui_text("typing_placeholder"),
            key=MAIN_TYPING_EVENTS_KEY,
        )

        submit_test = st.form_submit_button(ui_text("submit_assessment"))

    if submit_test:
        if not consent:
            st.warning(ui_text("online_consent_required"))
        else:
            audio_path = None
            image_path = None
            passive_video_path = None

            if audio_file is not None:
                audio_path = save_upload_file(audio_file, suffix="audio")
            if image_file is not None:
                image_path = save_upload_file(image_file, suffix="image")
            if passive_video_file is not None:
                passive_video_path = save_upload_file(passive_video_file, suffix="passive")
            typing_events = parse_typing_events(typing_events_raw)

            try:
                numeric_answers = {
                    question_id: get_response_options(language)[selected]
                    for question_id, selected in questionnaire_answers.items()
                }
                questionnaire_result = score_questionnaire(numeric_answers)
                multimodal_result = screen(
                    text_input=text_input,
                    audio_path=audio_path,
                    image_path=image_path,
                    passive_video_path=passive_video_path,
                    typing_events=typing_events,
                )
                profile = {
                    "full_name": full_name,
                    "age": int(age),
                    "gender": gender,
                    "village": village,
                    "phone": phone,
                    "assessor": assessor,
                    "language": language,
                }
                record = create_assessment_record(
                    profile=profile,
                    questionnaire=questionnaire_result,
                    multimodal=multimodal_result,
                )
            finally:
                cleanup_temp_file(audio_path)
                cleanup_temp_file(image_path)
                cleanup_temp_file(passive_video_path)

            st.success(ui_text("assessment_submitted"))
            st.code(record["assessment_id"], language="text")
            st.caption(ui_text("use_assessment_id"))
            render_result_view(record)

with adaptive_tab:
    initialize_adaptive_state()
    st.subheader(ui_text("adaptive_title"))
    st.caption(ui_text("adaptive_caption"))
    adaptive_language = st.session_state.get("adaptive_language", "English")

    if st.session_state.get("adaptive_last_record") is not None:
        st.success(ui_text("adaptive_completed"))
        render_result_view(st.session_state["adaptive_last_record"])
        if st.button(ui_text("start_new_adaptive"), key="adaptive_new_button"):
            reset_adaptive_state()
            st.rerun()
    else:
        adaptive_progress = get_adaptive_question_bank(st.session_state["adaptive_responses"], adaptive_language)
        current_question = adaptive_progress["next_question"]
        response_options = list(get_response_options(adaptive_language).keys())
        choose_one_label = {"Hindi": "एक चुनें", "Bengali": "একটি নির্বাচন করুন"}.get(adaptive_language, "Choose one")

        st.metric(ui_text("answered_questions"), f"{adaptive_progress['answered_count']}/{len(get_question_bank())}")
        st.metric(ui_text("estimated_theta"), f"{adaptive_progress['theta']:.2f}")
        st.caption(
            f"{ui_text('remaining_items')}: {adaptive_progress['remaining_count']} | "
            f"{ui_text('top_information')}: {adaptive_progress['max_information']:.3f}"
        )

        with st.form("adaptive_screening_form"):
            profile_col, context_col = st.columns(2)

            with profile_col:
                adaptive_full_name = st.text_input(ui_text("full_name"), key="adaptive_full_name")
                adaptive_age = st.number_input(ui_text("age"), min_value=10, max_value=100, value=25, key="adaptive_age")
                adaptive_gender = st.selectbox(
                    ui_text("gender"),
                    [
                        ui_text("gender_option_prefer_not"),
                        ui_text("gender_option_female"),
                        ui_text("gender_option_male"),
                        ui_text("gender_option_other"),
                    ],
                    key="adaptive_gender",
                )
                adaptive_village = st.text_input(ui_text("village"), key="adaptive_village")

            with context_col:
                adaptive_phone = st.text_input(ui_text("phone"), key="adaptive_phone")
                adaptive_assessor = st.text_input(ui_text("assessor"), key="adaptive_assessor")
                adaptive_language = st.selectbox(ui_text("preferred_language"), ["English", "Hindi", "Bengali", "Other"], key="adaptive_language")
                adaptive_consent = st.checkbox(ui_text("consent"), key="adaptive_consent")

            st.markdown(f"### {ui_text('adaptive_question')}")
            if current_question is not None:
                st.info(current_question["prompt"])
                adaptive_meta = current_question.get("adaptive", {})
                section_label = ui_text("adaptive_section")
                irt_info_label = ui_text("adaptive_irt_info")
                difficulty_label = ui_text("adaptive_difficulty")
                selection_score_label = ui_text("adaptive_selection_score")
                coverage_bonus_label = ui_text("adaptive_coverage_bonus")
                stop_threshold_label = ui_text("adaptive_stop_threshold")
                balance_weight_label = ui_text("adaptive_balance_weight")
                st.caption(
                    f"{section_label}: {current_question.get('section_label', current_question['section'])} | "
                    f"{irt_info_label}: {current_question['irt']['information']:.3f} | "
                    f"{difficulty_label}: {current_question['irt']['difficulty']:.2f} | "
                    f"{selection_score_label}: {adaptive_meta.get('selection_score', current_question['irt']['information']):.3f} | "
                    f"{coverage_bonus_label}: {adaptive_meta.get('coverage_bonus', 1.0):.2f}"
                )
                tuning = adaptive_progress.get("tuning", {})
                if tuning:
                    st.caption(
                        f"{stop_threshold_label}: {tuning.get('info_threshold', 0.0):.3f} | "
                        f"{balance_weight_label}: {tuning.get('coverage_weight', 0.0):.3f} | "
                        f"{ui_text('pilot_records')}: {tuning.get('pilot_size', 0)}"
                    )
                selected_answer = st.selectbox(
                    ui_text("select_one_answer"),
                    [choose_one_label] + response_options,
                    key=f"adaptive_answer_{current_question['id']}",
                )
            else:
                st.success(ui_text("adaptive_ready_finalize"))
                selected_answer = None

            st.markdown(f"### {ui_text('adaptive_optional_inputs')}")
            st.caption(ui_text("reuse_media"))
            adaptive_text_input = st.text_area(
                ui_text("describe_feeling"),
                height=180,
                placeholder=ui_text("describe_placeholder"),
                key="adaptive_text_input",
            )
            adaptive_typing_events_raw = st.text_area(
                ui_text("typing_rhythm"),
                height=100,
                placeholder=ui_text("typing_placeholder"),
                key="adaptive_typing_events_raw",
            )

            submit_label = ui_text("finalize_assessment") if current_question is None else ui_text("submit_answer")
            submit_adaptive = st.form_submit_button(submit_label)

        if submit_adaptive:
            if not adaptive_consent:
                st.warning(ui_text("consent_required"))
            elif current_question is not None and selected_answer == choose_one_label:
                st.warning(ui_text("please_choose_answer"))
            else:
                adaptive_audio_path = None
                adaptive_image_path = None
                adaptive_passive_video_path = None
                resolved_adaptive_audio = resolve_adaptive_upload("adaptive_audio_file", MAIN_AUDIO_UPLOAD_KEY)
                resolved_adaptive_image = resolve_adaptive_upload("adaptive_image_file", MAIN_IMAGE_UPLOAD_KEY)
                resolved_adaptive_passive_video = resolve_adaptive_upload("adaptive_passive_video_file", MAIN_PASSIVE_VIDEO_UPLOAD_KEY)
                if resolved_adaptive_audio is not None:
                    adaptive_audio_path = save_upload_file(resolved_adaptive_audio, suffix="adaptive_audio")
                if resolved_adaptive_image is not None:
                    adaptive_image_path = save_upload_file(resolved_adaptive_image, suffix="adaptive_image")
                if resolved_adaptive_passive_video is not None:
                    adaptive_passive_video_path = save_upload_file(resolved_adaptive_passive_video, suffix="adaptive_passive")

                try:
                    updated_answers = dict(st.session_state["adaptive_responses"])
                    if current_question is not None:
                        updated_answers[current_question["id"]] = get_response_options(adaptive_language)[selected_answer]

                    try:
                        next_state = fetch_adaptive_question_bank_from_api(updated_answers, adaptive_language)
                    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
                        st.warning(ui_text("adaptive_api_unavailable"))
                        next_state = get_adaptive_question_bank(updated_answers, adaptive_language)
                        st.session_state["adaptive_last_api_error"] = str(error)
                    else:
                        st.session_state.pop("adaptive_last_api_error", None)

                    st.session_state["adaptive_responses"] = updated_answers
                    st.session_state["adaptive_theta"] = next_state["theta"]

                    if next_state["should_stop"] or next_state["next_question"] is None:
                        questionnaire_result = score_adaptive_questionnaire(updated_answers)
                        multimodal_result = screen(
                            text_input=adaptive_text_input,
                            audio_path=adaptive_audio_path,
                            image_path=adaptive_image_path,
                            passive_video_path=adaptive_passive_video_path,
                            typing_events=parse_typing_events(adaptive_typing_events_raw),
                            language=adaptive_language,
                        )
                        profile = {
                            "full_name": adaptive_full_name,
                            "age": int(adaptive_age),
                            "gender": adaptive_gender,
                            "village": adaptive_village,
                            "phone": adaptive_phone,
                            "assessor": adaptive_assessor,
                            "language": adaptive_language,
                        }
                        record = create_assessment_record(
                            profile=profile,
                            questionnaire=questionnaire_result,
                            multimodal=multimodal_result,
                        )
                        st.session_state["adaptive_last_record"] = record
                        st.session_state["adaptive_completed"] = True
                        st.success(ui_text("adaptive_submitted"))
                        st.code(record["assessment_id"], language="text")
                        st.caption(ui_text("use_assessment_id"))
                        render_result_view(record)
                    else:
                        st.session_state["adaptive_last_question_id"] = next_state["next_question"]["id"]
                        st.rerun()
                finally:
                    cleanup_temp_file(adaptive_audio_path)
                    cleanup_temp_file(adaptive_image_path)
                    cleanup_temp_file(adaptive_passive_video_path)

with fetch_tab:
    st.subheader(ui_text("fetch_saved"))
    assessment_id = st.text_input(ui_text("enter_assessment_id"), placeholder=ui_text("assessment_id_placeholder"))
    if st.button(ui_text("fetch_button")):
        if not assessment_id.strip():
            st.warning(ui_text("enter_valid_id"))
        else:
            record = fetch_assessment_record(assessment_id)
            if record is None:
                st.error("No saved assessment was found for that ID.")
            else:
                render_result_view(record)
