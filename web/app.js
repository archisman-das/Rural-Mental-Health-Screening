const DOMAINS = [
  "depression",
  "anxiety",
  "stress",
  "sleep_disorder",
  "burnout",
  "loneliness",
  "substance_abuse",
];

const DOMAIN_LABELS = {
  depression: "Depression",
  anxiety: "Anxiety",
  stress: "Stress",
  sleep_disorder: "Sleep Disorder",
  burnout: "Burnout",
  loneliness: "Loneliness",
  substance_abuse: "Substance Abuse",
};

const RESPONSE_OPTIONS = [
  { label: "Not at all", value: 0 },
  { label: "Several days", value: 1 },
  { label: "More than half the days", value: 2 },
  { label: "Nearly every day", value: 3 },
];

const OFFLINE_DB_NAME = "mh-dashboard-offline";
const OFFLINE_DB_VERSION = 1;
const OFFLINE_RECORDS_STORE = "records";
const OFFLINE_PENDING_STORE = "pending_assessments";

const RESPONSE_OPTION_TRANSLATIONS = {
  English: ["Not at all", "Several days", "More than half the days", "Nearly every day"],
  Hindi: ["बिलकुल नहीं", "कुछ दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
  Bengali: ["একদম না", "কয়েক দিন", "অর্ধেকের বেশি দিন", "প্রায় প্রতিদিন"],
};

const ADAPTIVE_CHOOSE_ONE_TRANSLATIONS = {
  English: "Choose one",
  Hindi: "एक चुनें",
  Bengali: "একটি নির্বাচন করুন",
};

const LANGUAGE_OPTION_LABELS = {
  English: {
    English: "English",
    Hindi: "Hindi",
    Bengali: "Bengali",
    Other: "Other",
  },
  Hindi: {
    English: "\u0905\u0902\u0917\u094d\u0930\u0947\u091c\u0940",
    Hindi: "\u0939\u093f\u0902\u0926\u0940",
    Bengali: "\u092c\u093e\u0902\u0917\u094d\u0932\u093e",
    Other: "\u0905\u0928\u094d\u092f",
  },
  Bengali: {
    English: "\u0987\u0982\u09b0\u09c7\u099c\u09bf",
    Hindi: "\u09b9\u09bf\u09a8\u09cd\u09a6\u09bf",
    Bengali: "\u09ac\u09be\u0982\u09b2\u09be",
    Other: "\u0985\u09a8\u09cd\u09af",
  },
};

const GENDER_OPTION_LABELS = {
  English: ["Prefer not to say", "Female", "Male", "Other"],
  Hindi: ["कृपया चुनें", "महिला", "पुरुष", "अन्य"],
  Bengali: ["অনুগ্রহ করে নির্বাচন করুন", "নারী", "পুরুষ", "অন্যান্য"],
};

const RISK_LEVEL_LABELS = {
  English: { low: "Low", moderate: "Moderate", high: "High" },
  Hindi: { low: "निम्न", moderate: "मध्यम", high: "उच्च" },
  Bengali: { low: "নিম্ন", moderate: "মাঝারি", high: "উচ্চ" },
};

const TRAJECTORY_STATUS_LABELS = {
  English: {
    insufficient_history: "Need more screenings",
    escalating: "Escalating risk",
    worsening: "Worsening trend",
    improving: "Improving trend",
    volatile: "Volatile trajectory",
    stable: "Stable trajectory",
    default: "Trajectory available",
  },
  Hindi: {
    insufficient_history: "और स्क्रीनिंग की ज़रूरत है",
    escalating: "जोखिम बढ़ रहा है",
    worsening: "रुझान बिगड़ रहा है",
    improving: "रुझान बेहतर हो रहा है",
    volatile: "अस्थिर रुझान",
    stable: "स्थिर रुझान",
    default: "रुझान उपलब्ध है",
  },
  Bengali: {
    insufficient_history: "আরও স্ক্রিনিং প্রয়োজন",
    escalating: "ঝুঁকি বাড়ছে",
    worsening: "অবনমিত প্রবণতা",
    improving: "উন্নতিশীল প্রবণতা",
    volatile: "অস্থির প্রবণতা",
    stable: "স্থিতিশীল প্রবণতা",
    default: "প্রবণতা উপলব্ধ",
  },
};

const TRAJECTORY_SUMMARY_TEXTS = {
  English: {
    insufficient_history: "Only one screening is available. Capture a follow-up visit to start trend modeling.",
    volatile: "Risk is fluctuating across visits, so closer monitoring may be needed.",
    improving: "Recent visits suggest improving risk scores. Continue follow-up to confirm the recovery holds.",
    stable: "Risk has stayed relatively stable across the available screenings.",
    escalating: "Risk is rising over time. Compare this visit with the last one and plan follow-up quickly.",
  },
  Hindi: {
    insufficient_history: "केवल एक स्क्रीनिंग उपलब्ध है। रुझान मॉडलिंग शुरू करने के लिए एक फॉलो-अप विज़िट दर्ज करें।",
    volatile: "विभिन्न विज़िट के बीच जोखिम बदल रहा है, इसलिए अधिक नज़दीकी निगरानी की ज़रूरत हो सकती है।",
    improving: "हाल की विज़िट जोखिम स्कोर में सुधार दिखाती हैं। सुधार बने रहने की पुष्टि के लिए फॉलो-अप जारी रखें।",
    stable: "उपलब्ध स्क्रीनिंग में जोखिम अपेक्षाकृत स्थिर रहा है।",
    escalating: "समय के साथ जोखिम बढ़ रहा है। इस विज़िट की पिछली विज़िट से तुलना करें और जल्दी फॉलो-अप की योजना बनाएं।",
  },
  Bengali: {
    insufficient_history: "শুধুমাত্র একটি স্ক্রিনিং উপলব্ধ আছে। ট্রেন্ড মডেলিং শুরু করতে একটি ফলো-আপ ভিজিট নথিভুক্ত করুন।",
    volatile: "বিভিন্ন ভিজিটে ঝুঁকি ওঠানামা করছে, তাই আরও কাছ থেকে নজরদারি দরকার হতে পারে।",
    improving: "সাম্প্রতিক ভিজিটগুলো ঝুঁকির স্কোর উন্নত হওয়ার ইঙ্গিত দিচ্ছে। উন্নতি বজায় আছে কিনা দেখতে ফলো-আপ চালিয়ে যান।",
    stable: "উপলব্ধ স্ক্রিনিংগুলোতে ঝুঁকি তুলনামূলকভাবে স্থির রয়েছে।",
    escalating: "সময়ের সাথে ঝুঁকি বাড়ছে। এই ভিজিটটি আগেরটির সাথে তুলনা করুন এবং দ্রুত ফলো-আপ পরিকল্পনা করুন।",
  },
};

const MODALITY_LABELS = {
  English: { text: "Text", audio: "Audio", image: "Image" },
  Hindi: { text: "पाठ", audio: "ऑडियो", image: "छवि" },
  Bengali: { text: "পাঠ্য", audio: "অডিও", image: "ছবি" },
};

const DOMAIN_LABEL_TRANSLATIONS = {
  English: {
    depression: "Depression",
    anxiety: "Anxiety",
    stress: "Stress",
    sleep_disorder: "Sleep Disorder",
    burnout: "Burnout",
    loneliness: "Loneliness",
    substance_abuse: "Substance Abuse",
  },
  Hindi: {
    depression: "अवसाद",
    anxiety: "चिंता",
    stress: "तनाव",
    sleep_disorder: "नींद विकार",
    burnout: "बर्नआउट",
    loneliness: "अकेलापन",
    substance_abuse: "पदार्थ उपयोग",
  },
  Bengali: {
    depression: "অবসাদ",
    anxiety: "উদ্বেগ",
    stress: "চাপ",
    sleep_disorder: "ঘুমের সমস্যা",
    burnout: "বার্নআউট",
    loneliness: "একাকীত্ব",
    substance_abuse: "পদার্থ ব্যবহার",
  },
};

function localizedRiskLevel(level, language = currentLanguage()) {
  return RISK_LEVEL_LABELS[language]?.[level] || RISK_LEVEL_LABELS.English[level] || level;
}

function localizedTrajectoryStatus(status, language = currentLanguage()) {
  return TRAJECTORY_STATUS_LABELS[language]?.[status] || TRAJECTORY_STATUS_LABELS.English[status] || TRAJECTORY_STATUS_LABELS.English.default;
}

function localizedTrajectorySummary(status, language = currentLanguage()) {
  return TRAJECTORY_SUMMARY_TEXTS[language]?.[status] || TRAJECTORY_SUMMARY_TEXTS.English[status] || "";
}

function localizedModalityLabel(key, language = currentLanguage()) {
  return MODALITY_LABELS[language]?.[key] || MODALITY_LABELS.English[key] || key;
}

function localizedDomainLabel(key, language = currentLanguage()) {
  return DOMAIN_LABEL_TRANSLATIONS[language]?.[key] || DOMAIN_LABEL_TRANSLATIONS.English[key] || key;
}

const ADAPTIVE_UI_TRANSLATIONS = {
  English: {
    chooseOne: "Choose one",
    answerLabel: "Choose your answer",
    answerHelp: "Choose the option that best matches the person's experience.",
    narrativeSubtitle: "Use this note alongside the files already uploaded in the main screening workspace.",
    remaining: "Remaining",
    section: "Section",
    irtInfo: "IRT info",
    difficulty: "Difficulty",
    selectionScore: "Selection score",
    coverageBonus: "Coverage bonus",
    stopThreshold: "Stop threshold",
    balanceWeight: "Balance weight",
    completedPrompt: "{id} has been saved. Start a new session to run another adaptive screening.",
    completedMeta: "Adaptive interview complete.",
    idleMeta: "No adaptive session started yet.",
    loadingMeta: "Selecting the next best question...",
    profileMissing: "Please complete the candidate profile before saving the adaptive assessment.",
    consentMissing: "Please confirm consent before saving the adaptive assessment.",
    fallbackNotice: "Adaptive API unavailable. Using browser fallback selector.",
    answerRequired: "Please choose an answer before continuing.",
  },
  Hindi: {
    chooseOne: "\u090f\u0915 \u091a\u0941\u0928\u0947\u0902",
    answerLabel: "\u0905\u092a\u0928\u093e \u0909\u0924\u094d\u0924\u0930 \u091a\u0941\u0928\u0947\u0902",
    answerHelp: "\u0909\u0938 \u0935\u093f\u0915\u0932\u094d\u092a \u091a\u0941\u0928\u0947\u0902 \u091c\u094b \u0909\u0928\u0915\u0947 \u0905\u0928\u0941\u092d\u0935 \u0938\u0947 \u0938\u092c\u0938\u0947 \u0905\u091a\u094d\u091b\u0940 \u0924\u0930\u0939 \u092e\u093f\u0932\u0924\u093e \u0939\u094b\u0964",
    narrativeSubtitle: "\u092f\u0939 \u0928\u094b\u091f \u092e\u0941\u0916\u094d\u092f screening workspace \u092e\u0947\u0902 \u092a\u0939\u0932\u0947 \u0938\u0947 \u0905\u092a\u0932\u094b\u0921 \u0915\u0940 \u0917\u0908 \u092b\u093e\u0907\u0932\u094b\u0902 \u0915\u0947 \u0938\u093e\u0925 \u0909\u092a\u092f\u094b\u0917 \u0915\u0930\u0947\u0902\u0964",
    remaining: "\u0936\u0947\u0937",
    section: "\u0905\u0928\u0941\u092d\u093e\u0917",
    irtInfo: "IRT \u091c\u093e\u0928\u0915\u093e\u0930\u0940",
    difficulty: "\u0915\u0920\u093f\u0928\u093e\u0908",
    selectionScore: "\u091a\u092f\u0928 \u0938\u094d\u0915\u094b\u0930",
    coverageBonus: "\u0915\u0935\u0930\u0947\u091c \u092c\u094b\u0928\u0938",
    stopThreshold: "\u0930\u094b\u0915\u0928\u0947 \u0915\u0940 \u0938\u0940\u092e\u093e",
    balanceWeight: "\u0938\u0902\u0924\u0941\u0932\u0928 \u092d\u093e\u0930",
    completedPrompt: "{id} \u0938\u0947\u0935 \u0939\u094b \u0917\u092f\u093e \u0939\u0948\u0964 \u0905\u0917\u0932\u0947 \u0906\u0902\u0915\u0932\u0928 \u0915\u0947 \u0932\u093f\u090f \u0928\u092f\u093e \u0938\u0924\u094d\u0930 \u0936\u0941\u0930\u0942 \u0915\u0930\u0947\u0902\u0964",
    completedMeta: "\u0905\u0928\u0941\u0915\u0942\u0932\u0940 \u0938\u093e\u0915\u094d\u0937\u093e\u0924\u094d\u0915\u093e\u0930 \u092a\u0942\u0930\u093e \u0939\u0941\u0906\u0964",
    idleMeta: "\u0905\u0928\u0941\u0915\u0942\u0932 \u0938\u0924\u094d\u0930 \u0905\u092d\u0940 \u0936\u0941\u0930\u0942 \u0928\u0939\u0940\u0902 \u0939\u0941\u0906 \u0939\u0948\u0964",
    loadingMeta: "\u0905\u0917\u0932\u093e \u0938\u092c\u0938\u0947 \u0909\u092a\u092f\u0941\u0915\u094d\u0924 \u092a\u094d\u0930\u0936\u094d\u0928 \u091a\u0941\u0928\u093e \u091c\u093e \u0930\u0939\u093e \u0939\u0948\u0964",
    profileMissing: "\u0905\u0928\u0941\u0915\u0942\u0932\u0940 \u0906\u0915\u0932\u0928 \u0938\u0947\u0935 \u0915\u0930\u0928\u0947 \u0938\u0947 \u092a\u0939\u0932\u0947 \u0909\u092e\u094d\u092e\u0940\u0926\u0935\u093e\u0930 \u092a\u094d\u0930\u094b\u092b\u093e\u0907\u0932 \u092a\u0942\u0930\u093e \u0915\u0930\u0947\u0902\u0964",
    consentMissing: "\u0905\u0928\u0941\u0915\u0942\u0932\u0940 \u0906\u0915\u0932\u0928 \u0938\u0947\u0935 \u0915\u0930\u0928\u0947 \u0938\u0947 \u092a\u0939\u0932\u0947 \u0915\u0943\u092a\u092f\u093e \u0938\u0939\u092e\u0924\u093f \u0915\u0940 \u092a\u0941\u0937\u094d\u091f\u093f \u0915\u0930\u0947\u0902\u0964",
    fallbackNotice: "\u0905\u0928\u0941\u0915\u0942\u0932\u0940 API \u0905\u092d\u0940 \u0909\u092a\u0932\u092c\u094d\u0927 \u0928\u0939\u0940\u0902 \u0939\u0948\u0964 \u092c\u094d\u0930\u093e\u0909\u091c\u093c\u0930 fallback selector \u0915\u093e \u0909\u092a\u092f\u094b\u0917 \u0939\u094b \u0930\u0939\u093e \u0939\u0948\u0964",
    answerRequired: "\u0905\u0917\u0947 \u092c\u0922\u093c\u0928\u0947 \u0938\u0947 \u092a\u0939\u0932\u0947 \u0915\u0943\u092a\u092f\u093e \u090f\u0915 \u0909\u0924\u094d\u0924\u0930 \u091a\u0941\u0928\u0947\u0902\u0964",
  },
  Bengali: {
    chooseOne: "\u098f\u0995\u099f\u09bf \u09a8\u09bf\u09b0\u09cd\u09ac\u09be\u099a\u09a8 \u0995\u09b0\u09c1\u09a8",
    answerLabel: "\u0986\u09aa\u09a8\u09be\u09b0 \u0989\u09a4\u09cd\u09a4\u09b0 \u09a8\u09bf\u09b0\u09cd\u09ac\u09be\u099a\u09a8 \u0995\u09b0\u09c1\u09a8",
    answerHelp: "\u098f\u09ae\u09a8 \u0985\u09aa\u09cd\u09b6\u09a8 \u09a8\u09bf\u09b0\u09cd\u09ac\u09be\u099a\u09a8 \u0995\u09b0\u09c1\u09a8 \u099c\u09be \u09a4\u09be\u09b0 \u0985\u09a8\u09c1\u09ad\u09ac\u09c7\u09b0 \u09b8\u09ac\u099a\u09c7\u09af\u09bc\u09c7 \u09ad\u09be\u09b2\u09cb \u09ae\u09c7\u09b2\u09c7\u0964",
    narrativeSubtitle: "\u09ae\u09c1\u0996\u09cd\u09af screening workspace-\u098f \u0985\u09a8\u09c1\u09aa\u09cd\u09b2\u09cb\u09a1 \u0995\u09b0\u09be \u09ab\u09be\u0987\u09b2\u0997\u09c1\u09b2\u09bf\u09b0 \u09b8\u09be\u09a5\u09c7 \u098f\u0987 \u09a8\u09cb\u099f\u099f\u09bf \u09ac\u09cd\u09af\u09ac\u09b9\u09be\u09b0 \u0995\u09b0\u09c1\u09a8\u0964",
    remaining: "\u09ac\u09be\u0995\u09bf",
    section: "\u0985\u09a7\u09cd\u09af\u09be\u09df",
    irtInfo: "IRT \u09a4\u09a5\u09cd\u09af",
    difficulty: "\u0995\u09a0\u09bf\u09a8\u09a4\u09be",
    selectionScore: "\u09a8\u09bf\u09b0\u09cd\u09ac\u09be\u099a\u09a8 \u09b8\u09cd\u0995\u09cb\u09b0",
    coverageBonus: "\u0995\u09ad\u09be\u09b0\u09c7\u099c \u09ac\u09cb\u09a8\u09be\u09b8",
    stopThreshold: "\u09b8\u09ae\u09be\u09aa\u09cd\u09a4\u09bf \u09b8\u09c0\u09ae\u09be",
    balanceWeight: "\u09b8\u09be\u09ae\u09cd\u09af\u09a4\u09be \u0993\u099c\u09a8",
    completedPrompt: "{id} \u09b8\u0982\u09b0\u0995\u09cd\u09b7\u09bf\u09a4 \u09b9\u09df\u09c7\u099b\u09c7\u0964 \u0986\u09b0\u09cb \u098f\u0995\u099f\u09bf adaptive screening \u09b6\u09c1\u09b0\u09c1 \u0995\u09b0\u09a4\u09c7 \u09a8\u09a4\u09c1\u09a8 \u09b8\u09c7\u09b6\u09a8 \u09b6\u09c1\u09b0\u09c1 \u0995\u09b0\u09c1\u09a8\u0964",
    completedMeta: "\u0985\u09a8\u09c1\u0995\u09c2\u09b2 \u09b8\u09be\u0995\u09cd\u09b7\u09be\u09a4\u09cd\u0995\u09be\u09b0 \u09b8\u09ae\u09be\u09aa\u09cd\u09a4\u0964",
    idleMeta: "\u0985\u09a8\u09c1\u0995\u09c2\u09b2 \u09b8\u09c7\u09b6\u09a8 \u098f\u09ad\u09be\u09b2\u09be \u09b6\u09c1\u09b0\u09c1 \u09b9\u09df\u09a8\u09bf\u0964",
    loadingMeta: "\u09aa\u09b0\u09ac\u09b0\u09cd\u09a4\u09c0 \u09b8\u09ac\u099a\u09c7\u09af\u09bc\u09c7 \u0989\u09aa\u09af\u09cb\u0997\u09c0 \u09aa\u09cd\u09b0\u09b6\u09cd\u09a8 \u09ac\u09c7\u099b\u09c7 \u09a8\u09bf\u09af\u09bc\u09c7 \u09b9\u099a\u09cd\u099b\u09c7\u0964",
    profileMissing: "\u0985\u09a8\u09c1\u0995\u09c2\u09b2 \u0986\u09a7\u09be\u09b0 \u09b8\u0982\u09b0\u0995\u09cd\u09b7\u09a3 \u09b8\u09c7\u09ac\u09c7 \u09a8\u09bf\u099a\u09cd\u099b\u09bf\u09a4 \u0995\u09b0\u09a4\u09c7 \u09b9\u09b2\u09c7 \u0989\u09ae\u09cd\u09ae\u09c0\u09a6\u09ac\u09be\u09b0 \u09aa\u09cd\u09b0\u09cb\u09ab\u09be\u0987\u09b2 \u09aa\u09c2\u09b0\u09cd\u09a3 \u0995\u09b0\u09c1\u09a8\u0964",
    consentMissing: "\u0985\u09a8\u09c1\u0995\u09c2\u09b2 \u0986\u09a7\u09be\u09b0 \u09b8\u0982\u09b0\u0995\u09cd\u09b7\u09a3 \u09b8\u09c7\u09ac\u09c7 \u09a8\u09bf\u099a\u09cd\u099b\u09bf\u09a4 \u0995\u09b0\u09a4\u09c7 \u09b9\u09b2\u09c7 \u09a6\u09af\u09bc\u09be \u0995\u09b0\u09c7 \u09b8\u09ae\u09cd\u09ae\u09a4\u09bf \u09a8\u09bf\u09b6\u09cd\u099a\u09bf\u09a4 \u0995\u09b0\u09c1\u09a8\u0964",
    fallbackNotice: "\u0985\u09a8\u09c1\u0995\u09c2\u09b2 API \u098f\u0996\u09a8\u0993 \u09aa\u09b0\u09bf\u09b7\u09c7\u09ac\u09be\u09df \u09a8\u09c7\u0987\u0964 \u09ac\u09cd\u09b0\u09c8\u099c\u09be\u09b0 fallback selector \u09ac\u09cd\u09af\u09ac\u09b9\u09be\u09b0 \u0995\u09b0\u09be \u09b9\u099a\u09cd\u099b\u09c7\u0964",
    answerRequired: "\u098f\u0997\u09cb\u09a8\u09cb\u09b0 \u0986\u0997\u09c7 \u098f\u0995\u099f\u09bf \u0989\u09a4\u09cd\u09a4\u09b0 \u09a8\u09bf\u09b0\u09cd\u09ac\u09be\u099a\u09a8 \u0995\u09b0\u09c1\u09a8\u0964",
  },
};

const UI_TRANSLATIONS = {
  English: {
    workspaceTab: "Assessment Workspace",
    heroEyebrow: "Start Screening",
    heroTitle: "Rural Mental Health Screening",
    heroText: "Begin one diagnostic screening session at a time, save the result, and view the current assessment without loading background records.",
    heroMetricRisk: "risk domains tracked",
    heroMetricModalities: "modalities blended",
    heroMetricOffline: "offline capture support",
    dashboardLanguageLabel: "Dashboard language",
    adaptiveTab: "Adaptive Test",
    analyticsTab: "Analytics Hub",
    recordsTab: "Records and Reports",
    applyLanguageBtn: "Apply Language",
    intakeFlowTitle: "Complete one screening from start to finish",
    intakeFlowText: "Enter the person's details, capture their responses, review the live preview, and save one finalized assessment for analysis.",
    step1Title: "Capture profile and consent",
    step1Text: "Start with identity, village, assessor, language, and consent so the screening record is complete.",
    step2Title: "Collect symptoms and narrative",
    step2Text: "Use the questionnaire, written response, and optional speech or face inputs to build a stronger assessment.",
    step3Title: "Provide supporting inputs",
    step3Text: "Add either a written response or a speech recording. For the image input, you can capture a live photo or upload an image file.",
    step4Title: "Review and save for analysis",
    step4Text: "Once saved, the result moves into Analytics Hub and Records and Reports for visualization and follow-up.",
    questionnaireTitle: "Questionnaire",
    questionnaireSubtitle: "Rate how often each symptom appeared in the last two weeks.",
    questionnaireNotes: "Dashboard questionnaire scoring reflects symptom frequency over the last two weeks.",
    adaptiveTitle: "Adaptive Test",
    adaptiveSubtitle: "Ask one question at a time using the backend IRT selector and reuse the workspace uploads.",
    adaptiveIntroFlowTitle: "Adaptive Flow",
    adaptiveIntroFlowHeading: "One question at a time",
    adaptiveIntroFlowText: "The backend selects the next most informative item and keeps the session aligned with the current language.",
    adaptiveIntroLanguageTitle: "Language Sync",
    adaptiveIntroLanguageHeading: "Language-aware prompts",
    adaptiveIntroLanguageText: "Prompts, response options, and session guidance automatically follow the selected dashboard language.",
    adaptiveIntroSharedTitle: "Shared Inputs",
    adaptiveIntroSharedHeading: "Reuse workspace inputs",
    adaptiveIntroSharedText: "Reuse the candidate profile and narrative inputs from the main screening workspace without re-entering them.",
    adaptiveProfileTitle: "Candidate Profile",
    adaptiveQuestionTitle: "Adaptive Question",
    adaptiveQuestionHint: "Start a session to load the first adaptive question.",
    adaptiveNarrativeTitle: "Workspace Narrative",
    adaptiveStartBtn: "Start Session",
    adaptiveNextBtn: "Submit Answer",
    adaptiveResetBtn: "Reset Session",
    adaptiveStatusIdle: "Start an adaptive session to load the first question.",
    adaptiveStatusLoading: "Fetching the next adaptive question...",
    adaptiveStatusReady: "Adaptive question ready.",
    adaptiveStatusComplete: "Adaptive session complete. The record has been saved.",
    adaptiveStatusError: "Adaptive API unavailable. Please try again.",
    candidateProfileTitle: "Candidate Profile",
    freeTextTitle: "Free Text and Upload Metadata",
    fullNameLabel: "Full name",
    ageLabel: "Age",
    genderLabel: "Gender",
    villageLabel: "Village / Local area",
    phoneLabel: "Phone / reference number",
    assessorLabel: "Assessor name",
    languageLabel: "Preferred language",
    consentLabel: "Consent received for screening",
    fullNamePlaceholder: "Enter full name",
    villagePlaceholder: "Village or locality",
    assessorPlaceholder: "Health worker or counselor",
    narrativeLabel: "Describe how the person has been feeling",
    narrativePlaceholder: "Example: I have been feeling tired, disconnected, anxious, and unable to sleep well.",
    genderOptions: ["Prefer not to say", "Female", "Male", "Other"],
    guidedSpeechTitle: "Guided Speech Recording",
    guidedSpeechTopic: "Topic: Describe your last few days, your sleep, stress, and how connected you feel to people around you.",
    audioFileLabel: "Voice sample",
    liveFaceTitle: "Live Face Capture",
    liveFaceTopic: "Capture one clear front-facing photo from the webcam for live facial-cue analysis.",
    imageFileLabel: "Face image",
    saveAssessmentBtn: "Save Assessment",
    resetAssessmentBtn: "Reset Form",
    workspaceStatusDefault: "Complete the assessment and save it to generate the result.",
    workspacePredictionEmpty: "Start a new assessment to generate a fresh live prediction preview.",
    workspaceNlpEmpty: "Start a new assessment to see fresh NLP insights from the narrative text.",
    workspaceReadinessEmpty: "Fill in candidate details, consent, questionnaire, and narrative to see readiness feedback.",
    workspacePredictionTitle: "Live Prediction Preview",
    workspacePredictionText: "Combined questionnaire and NLP preview before save",
    workspaceNlpTitle: "Live NLP Insights",
    workspaceNlpText: "Sentiment, emotions, and safety indicators from the narrative text",
    workspaceReadinessTitle: "Intake Readiness",
    workspaceReadinessText: "Checks whether the record is ready to save and analyze",
    analyticsBannerDefault: "Complete and save an assessment to open detailed analysis here.",
    recordsBannerDefault: "Fetch a saved assessment by ID when you want to review or download an older report.",
    analyticsReady: "detailed component-wise analysis is ready.",
    savedMessage: "saved through the backend API.",
    analyticsShowing: "Analytics Hub is now showing assessment",
    saveInProgress: "Saving assessment through the Python NLP backend...",
    previewRefreshing: "Refreshing the live preview from the Python NLP backend...",
    noRecordSelected: "No assessment selected.",
    assessmentIdLabel: "Assessment ID",
    overallConfidenceLabel: "Overall Confidence",
    overallRiskLabel: "Overall Risk",
    candidateLabel: "Candidate",
    villageShortLabel: "Village",
    assessorShortLabel: "Assessor",
    createdAtLabel: "Created At",
    analyticsIntroCurrent: "One assessment in focus",
    analyticsIntroCurrentText: "Analytics Hub now explains the currently saved assessment and does not preload backend records automatically.",
    analyticsIntroModel: "Model Insights",
    analyticsIntroModelText: "Review domain-level scores, modality quality, confidence, transformer usage, and NLP signal interpretation for this assessment.",
    analyticsIntroScope: "Prediction Scope",
    analyticsIntroScopeText: "Depression, Anxiety, Stress, Sleep Disorder, Burnout, Loneliness, and Substance Abuse.",
    detailAnalysisTitle: "Detailed component-wise analysis for the current assessment.",
    recordsHeadingText: "Fetch records, inspect individual predictions, and export a PDF report.",
    recordLookupPlaceholder: "Enter assessment ID to fetch",
    fetchRecordBtn: "Fetch Record",
    downloadPdfBtn: "Download Selected PDF",
    domainScoreComparisonTitle: "Domain Score Comparison",
    domainScoreComparisonText: "Questionnaire score versus combined AI score",
    modalityQualityShortText: "Availability, confidence, and processing quality",
    modalityQualityHelperText: "Use this section to understand which inputs were strong enough to support the final decision.",
    domainScoreComparisonDescription: "This section compares self-reported symptoms with the final multimodal backend score for each condition.",
    domainAnalysisTitle: "Domain Analysis",
    domainAnalysisText: "Questionnaire versus combined AI score for each prediction domain",
    componentContributionTitle: "Component Contribution",
    componentContributionText: "How text, audio, and image influenced the final assessment",
    modelStatisticsTitle: "Model Statistics",
    modelStatisticsText: "Deep learning and NLP model details used in this assessment",
    nlpSafetyTitle: "NLP and Safety Signals",
    nlpSafetyText: "Sentiment, emotion, self-harm language, and narrative interpretation",
    modalityQualityTitle: "Modality Quality",
    modalityQualityText: "Availability, confidence, and processing quality for each input stream",
    recommendationTitle: "Recommendation and Follow-up",
    recommendationText: "End-user explanation, follow-up note, and screening disclaimer",
    recordsExplorerTitle: "Assessment Explorer",
    recordsExplorerText: "Click any row to inspect a single record in detail.",
    assessmentDetailTitle: "Assessment Detail",
    assessmentDetailText: "Candidate profile and risk summary",
    scoreComparisonTitle: "Score Comparison",
    scoreComparisonText: "Questionnaire versus dashboard prediction",
    modalityBreakdownTitle: "Modality Breakdown",
    modalityBreakdownText: "Text, audio metadata, and image metadata",
    featureSnapshotTitle: "Feature Snapshot",
    featureSnapshotText: "NLP and record features for the selected assessment",
    patientHistoryTitle: "Patient History",
    patientHistoryText: "Prior screenings and overall risk movement over time",
    domainTrajectoryTitle: "Domain Drift",
    domainTrajectoryText: "Which risk domains are worsening, improving, or staying stable",
    questionnaireRiskTitle: "Questionnaire Risk",
    questionnaireOverall: "Questionnaire Overall",
    combinedResultTitle: "Combined Dashboard Result",
    confidenceLabel: "Confidence",
    recommendationLabel: "Recommendation",
    questionnaireLabel: "Questionnaire",
    dashboardLabel: "Dashboard",
    combinedAiLabel: "Combined AI",
    noDataModality: "No data available for this modality.",
    noQuestionnaireNotesLabel: "No questionnaire notes available.",
    availableLabel: "Available",
    uploadReceivedLabel: "Upload Received, Not Analyzable",
    notAvailableLabel: "Not available",
    noFeaturesLabel: "No raw feature values were captured for this record.",
    noMatchRecords: "No assessments match the current filters.",
    previousLabel: "Previous",
    nextLabel: "Next",
    riskLabel: "Risk",
    noRecordsLoaded: "No records loaded yet.",
    pageStatus: "Page {page} of {total}",
    noAssessmentAnalysis: "No assessment analysis available yet.",
    noComponentBreakdown: "No component breakdown available yet.",
    noModalityQuality: "No modality quality information available yet.",
    noRecommendationDetails: "No recommendation details available yet.",
    noModelStats: "No model statistics available yet.",
    noNlpSummary: "No NLP signal summary available yet.",
    sentimentLabel: "Sentiment",
    emotionLabel: "Emotion",
    safetyLanguageLabel: "Safety Language",
    transformerLabel: "Transformer",
    audioModalityLabel: "Audio Modality",
    imageModalityLabel: "Image Modality",
    readinessScoreLabel: "Readiness Score",
    completionLabel: "Completion",
    needsAttention: "Needs attention",
    readyLabel: "Ready",
    infoLabel: "Info",
    livePreviewLabel: "Live preview",
    savedAtLabel: "Saved at",
    fetchPrompt: "Enter an assessment ID before fetching a record.",
    fetchSuccess: "Fetched assessment {id} from the backend API.",
    fetchMissing: "No record matched that assessment ID in the backend API.",
    deleteRecord: "Delete Record",
    deleteRecordConfirm: "Delete this assessment permanently?",
    deleteRecordSuccess: "Deleted assessment {id}.",
    deleteRecordFailed: "Could not delete assessment {id}.",
    deleteRecordRequiresOnline: "Deletion requires an online connection for synced records.",
    deleteRecordNotFound: "The selected assessment could not be found.",
    hiddenDemoRecord: "Demo/backend records are hidden from the user list.",
    noDataLabel: "No data",
    noDataMetricLabel: "No data",
    unknownUserLabel: "Unnamed user",
    unknownLocationLabel: "Unknown location",
    unknownLabel: "Unknown",
    notStatedLabel: "Not stated",
    unavailableLabel: "Unavailable",
    noneLabel: "None",
    detectedLabel: "Detected",
    notDetectedLabel: "Not detected",
    currentLabel: "Current",
    currentUserLabel: "Current user",
    topComorbidityLabel: "Top comorbidity",
    scoreLabel: "Score",
    featuresLabel: "Features",
    recommendationAndDisclaimerTitle: "Recommendation and Disclaimer",
    recommendationTitle: "Recommendation",
    screeningDisclaimerTitle: "Screening Disclaimer",
    noRecommendationText: "No recommendation available.",
    noDisclaimerText: "No disclaimer available.",
    recommendationOverviewText: "This area gives the end user the screening interpretation and the appropriate follow-up note.",
    overallRiskTrajectoryTitle: "Overall Risk Trajectory",
    trajectoryModelTitle: "Longitudinal Trajectory",
    trajectoryModelText: "Trend modeling across repeated screenings for the same person",
    screeningCountLabel: "{status} across {count} screenings",
    trendSummaryTitle: "Trend Summary",
    trajectorySummaryTitle: "Trend Summary",
    trajectorySummaryText: "Change since baseline, recent change, and domain movement",
    statusTitle: "Status",
    trajectoryMetricsTitle: "Trajectory Metrics",
    baselineToCurrentLabel: "Baseline {baseline} to current {current}",
    changeSinceBaselineLabel: "Change since baseline",
    recentChangeLabel: "Recent change",
    volatilityLabel: "Volatility",
    noTrajectoryLabel: "No longitudinal trajectory available yet.",
    noTrendSummaryLabel: "No trend summary available yet.",
    noMoreDataLabel: "Need more data",
    noTrainedModelStatsLabel: "No trained model bundle statistics are available for this assessment yet.",
    trainedBundleComparisonTitle: "Trained Bundle Comparison",
    macroR2CoverageText: "Macro R2 and sample coverage by modality",
    trainedBundleDescription: "This compares the locally trained bundle quality for text, audio, and image using the current saved model metadata.",
    textTransformerLabel: "Text transformer",
    trainedModalitiesLabel: "Trained modalities",
    confidenceHintLabel: "Confidence Hint",
    trainedBundleLabel: "Trained bundle",
    fallbackLabel: "Fallback",
    trainedAtLabel: "Trained at",
    safetyKeywordsLabel: "Safety keywords",
    keywordMatchesLabel: "Keyword matches",
    narrativeWordCountLabel: "Narrative word count",
    emotionIntensityLabel: "Emotion intensity",
    domainCoverageLabel: "Domain coverage",
    analysisEngineLabel: "engine",
    macroR2Label: "Macro R2",
    samplesLabel: "Samples",
    domainsLabel: "Domains",
    manifestLabel: "Manifest",
    datasetRootLabel: "Dataset root",
    trendModelDescription: "Trend modeling combines repeated visits, slope, and volatility so health workers can see whether risk is rising, falling, or fluctuating.",
    noFilteredExportLabel: "There are no filtered records to export.",
    exportedFilteredLabel: "Exported {count} filtered records.",
    backendApiLabel: "the backend API",
    sampleDatasetLabel: "the bundled sample dataset",
    localOfflineStorageLabel: "local offline storage",
    offlineQueueSyncedLabel: "Offline queue synced where possible and local records were refreshed.",
    savedOfflineQueuedLabel: "Assessment saved offline. It will sync automatically when the connection returns.",
    backendUnavailableSavedOfflineLabel: "Backend unavailable. The assessment was saved offline and queued for sync.",
    backendPreviewUnavailableLabel: "Backend preview unavailable. Showing offline heuristic preview instead.",
    loadedOfflineRecordLabel: "Loaded {id} from offline storage.",
    savedOfflineQueuedShortLabel: "saved offline and queued for sync.",
    savedOfflineQueuedAfterApiLabel: "saved offline after the API became unavailable.",
    loadRecordsFromApiFailedLabel: "Could not load records from the backend API. Import a JSON file manually instead.",
    offlineRecordsLoadedLabel: "Backend unavailable. Loaded records from offline storage.",
    loadRecordsFromApiGenericErrorLabel: "Could not load records from the backend API.",
    offlineModeActiveLabel: "Offline mode active. New assessments will be saved locally and synced later.",
    onlineSyncReadyLabel: "Online sync ready",
    offlineModeQueuedLabel: "Offline mode active | {count} queued",
    offlineScreeningElevatedLabel: "Offline screening suggests elevated {domain} risk. Sync this assessment when a connection is available for backend review.",
    offlineScreeningCompletedLabel: "Offline screening completed. Sync this assessment when a connection is available for backend confirmation.",
    pdfReportTitle: "Rural Mental Health Screening Dashboard Report",
    pdfQuestionnaireLabel: "Questionnaire",
    pdfDashboardLabel: "Dashboard",
    pdfRecommendationLabel: "Recommendation",
    pdfWhyFlaggedLabel: "Why {domain} was flagged",
    pdfTopContributorsLabel: "Top model contributors for this domain:",
    usableLabel: "Usable",
    limitedLabel: "Limited",
    noModalityNoteLabel: "No modality note available.",
    noAdditionalProcessingStatsLabel: "No additional processing statistics available.",
    whyFlaggedLabel: "Why {domain} was flagged",
    topModelContributorsLabel: "Top model contributors for this domain:",
  },
  Hindi: {
    adaptiveTab: "अनुकूली परीक्षण",
    workspaceTab: "आकलन कार्यक्षेत्र",
    heroEyebrow: "स्क्रीनिंग शुरू करें",
    heroTitle: "ग्रामीण मानसिक स्वास्थ्य स्क्रीनिंग",
    heroText: "एक समय में एक नैदानिक स्क्रीनिंग सत्र शुरू करें, परिणाम सहेजें, और बैकग्राउंड रिकॉर्ड लोड किए बिना वर्तमान आकलन देखें।",
    heroMetricRisk: "जोखिम डोमेन ट्रैक किए गए",
    heroMetricModalities: "मॉडेलिटी जोड़ी गई",
    heroMetricOffline: "ऑफलाइन कैप्चर समर्थन",
    dashboardLanguageLabel: "डैशबोर्ड भाषा",
    analyticsTab: "विश्लेषण केंद्र",
    recordsTab: "रिकॉर्ड और रिपोर्ट",
    applyLanguageBtn: "भाषा लागू करें",
    intakeFlowTitle: "एक स्क्रीनिंग शुरू से अंत तक पूरी करें",
    intakeFlowText: "व्यक्ति का विवरण भरें, उनके उत्तर दर्ज करें, लाइव प्रीव्यू देखें, और विश्लेषण के लिए अंतिम आकलन सहेजें।",
    step1Title: "प्रोफ़ाइल और सहमति दर्ज करें",
    step1Text: "पहचान, गाँव, आकलनकर्ता, भाषा और सहमति से शुरुआत करें ताकि रिकॉर्ड पूरा हो।",
    step2Title: "लक्षण और विवरण एकत्र करें",
    step2Text: "मजबूत आकलन के लिए प्रश्नावली, लिखित उत्तर, और वैकल्पिक आवाज़ या चेहरे का इनपुट उपयोग करें।",
    step3Title: "सहायक इनपुट जोड़ें",
    step3Text: "या तो लिखित उत्तर दें या आवाज़ रिकॉर्ड करें। छवि के लिए लाइव फ़ोटो लें या फ़ाइल अपलोड करें।",
    step4Title: "समीक्षा करें और विश्लेषण के लिए सहेजें",
    step4Text: "सहेजने के बाद परिणाम Analytics Hub और Records and Reports में दिखाई देगा।",
    questionnaireTitle: "प्रश्नावली",
    questionnaireSubtitle: "पिछले दो हफ्तों में लक्षण कितनी बार दिखाई दिए, यह चुनें।",
    questionnaireNotes: "डैशबोर्ड प्रश्नावली स्कोर पिछले दो हफ्तों की लक्षण आवृत्ति पर आधारित है।",
    adaptiveTitle: "अनुकूली परीक्षण",
    adaptiveSubtitle: "बैकएंड IRT चयनकर्ता का उपयोग करके एक समय में एक प्रश्न पूछें और कार्यक्षेत्र अपलोड का पुन: उपयोग करें।",
    adaptiveIntroFlowTitle: "अनुकूली प्रवाह",
    adaptiveIntroFlowHeading: "एक समय में एक प्रश्न",
    adaptiveIntroFlowText: "बैकएंड अगले सबसे उपयोगी प्रश्न का चयन करता है और सत्र को वर्तमान भाषा के साथ संरेखित रखता है।",
    adaptiveIntroLanguageTitle: "भाषा समन्वय",
    adaptiveIntroLanguageHeading: "भाषा-सचेत प्रॉम्प्ट",
    adaptiveIntroLanguageText: "प्रॉम्प्ट, उत्तर विकल्प और सत्र मार्गदर्शन चयनित डैशबोर्ड भाषा के अनुसार स्वतः बदलते हैं।",
    adaptiveIntroSharedTitle: "साझा इनपुट",
    adaptiveIntroSharedHeading: "कार्यक्षेत्र इनपुट पुन: उपयोग करें",
    adaptiveIntroSharedText: "मुख्य स्क्रीनिंग कार्यक्षेत्र से उम्मीदवार प्रोफ़ाइल और विवरण पुनः दर्ज किए बिना उपयोग करें।",
    adaptiveProfileTitle: "उम्मीदवार प्रोफ़ाइल",
    adaptiveQuestionTitle: "अनुकूली प्रश्न",
    adaptiveQuestionHint: "पहला अनुकूली प्रश्न लोड करने के लिए सत्र शुरू करें।",
    adaptiveNarrativeTitle: "कार्यस्थान विवरण",
    adaptiveStartBtn: "सत्र शुरू करें",
    adaptiveNextBtn: "उत्तर भेजें",
    adaptiveResetBtn: "सत्र रीसेट करें",
    adaptiveStatusIdle: "पहला प्रश्न लोड करने के लिए अनुकूली सत्र शुरू करें।",
    adaptiveStatusLoading: "अगला सबसे उपयुक्त प्रश्न चुना जा रहा है...",
    adaptiveStatusReady: "अनुकूली प्रश्न तैयार है।",
    adaptiveStatusComplete: "अनुकूली सत्र पूरा हुआ। रिकॉर्ड सहेज लिया गया है।",
    adaptiveStatusError: "अनुकूली API उपलब्ध नहीं है। कृपया पुनः प्रयास करें।",
    candidateProfileTitle: "उम्मीदवार प्रोफ़ाइल",
    freeTextTitle: "मुक्त पाठ और अपलोड विवरण",
    fullNameLabel: "पूरा नाम",
    ageLabel: "आयु",
    genderLabel: "लिंग",
    villageLabel: "गाँव / क्षेत्र",
    phoneLabel: "फ़ोन / संदर्भ संख्या",
    assessorLabel: "आकलनकर्ता का नाम",
    languageLabel: "पसंदीदा भाषा",
    consentLabel: "स्क्रीनिंग के लिए सहमति प्राप्त हुई",
    fullNamePlaceholder: "पूरा नाम दर्ज करें",
    villagePlaceholder: "गाँव या क्षेत्र",
    assessorPlaceholder: "स्वास्थ्य कार्यकर्ता या परामर्शदाता",
    narrativeLabel: "व्यक्ति कैसा महसूस कर रहा है, इसका वर्णन करें",
    narrativePlaceholder: "उदाहरण: मैं थका हुआ, अलग-थलग, चिंतित और ठीक से सो नहीं पा रहा हूँ।",
    genderOptions: ["कृपया चुनें", "महिला", "पुरुष", "अन्य"],
    guidedSpeechTitle: "निर्देशित वॉइस रिकॉर्डिंग",
    guidedSpeechTopic: "विषय: पिछले कुछ दिनों, नींद, तनाव और लोगों से जुड़ाव के बारे में बताएं।",
    audioFileLabel: "आवाज़ नमूना",
    liveFaceTitle: "लाइव चेहरे की फ़ोटो",
    liveFaceTopic: "चेहरे के संकेत विश्लेषण के लिए वेबकैम से एक साफ़ सामने की फ़ोटो लें।",
    imageFileLabel: "चेहरे की छवि",
    saveAssessmentBtn: "आकलन सहेजें",
    resetAssessmentBtn: "फॉर्म रीसेट करें",
    workspaceStatusDefault: "परिणाम देखने के लिए आकलन पूरा करके सहेजें।",
    workspacePredictionEmpty: "लाइव प्रेडिक्शन प्रीव्यू के लिए आकलन भरना शुरू करें।",
    workspaceNlpEmpty: "वर्णन लिखते समय NLP संकेत यहाँ दिखाई देंगे।",
    workspaceReadinessEmpty: "तैयारी फीडबैक देखने के लिए विवरण, सहमति, प्रश्नावली और वर्णन भरें।",
    workspacePredictionTitle: "लाइव प्रेडिक्शन प्रीव्यू",
    workspacePredictionText: "सहेजने से पहले प्रश्नावली और NLP का संयुक्त प्रीव्यू",
    workspaceNlpTitle: "लाइव NLP इनसाइट्स",
    workspaceNlpText: "वर्णन पाठ से भाव, भावना और सुरक्षा संकेत",
    workspaceReadinessTitle: "इनटेक तैयारी",
    workspaceReadinessText: "जाँचता है कि रिकॉर्ड सहेजने और विश्लेषण के लिए तैयार है या नहीं",
    analyticsBannerDefault: "विस्तृत विश्लेषण देखने के लिए आकलन पूरा करके सहेजें।",
    recordsBannerDefault: "पुरानी रिपोर्ट देखने या डाउनलोड करने के लिए आकलन ID से रिकॉर्ड खोजें।",
    analyticsReady: "का विस्तृत घटक-आधारित विश्लेषण तैयार है।",
    savedMessage: "बैकएंड API के माध्यम से सहेजा गया।",
    analyticsShowing: "Analytics Hub अब यह आकलन दिखा रहा है",
    saveInProgress: "Python NLP बैकएंड के माध्यम से आकलन सहेजा जा रहा है...",
    previewRefreshing: "Python NLP बैकएंड से लाइव प्रीव्यू ताज़ा किया जा रहा है...",
    noRecordSelected: "कोई आकलन चुना नहीं गया है।",
    assessmentIdLabel: "आकलन आईडी",
    overallConfidenceLabel: "कुल कॉन्फिडेंस",
    overallRiskLabel: "कुल जोखिम",
    candidateLabel: "उम्मीदवार",
    villageShortLabel: "गाँव",
    assessorShortLabel: "आकलनकर्ता",
    createdAtLabel: "समय",
    analyticsIntroCurrent: "एक आकलन पर ध्यान",
    analyticsIntroCurrentText: "Analytics Hub अब पुराने रिकॉर्ड स्वतः लोड करने के बजाय वर्तमान सहेजे गए आकलन की व्याख्या करता है।",
    analyticsIntroModel: "मॉडल अंतर्दृष्टि",
    analyticsIntroModelText: "इस आकलन के लिए डोमेन स्कोर, मॉडेलिटी गुणवत्ता, कॉन्फिडेंस, ट्रांसफॉर्मर उपयोग और NLP संकेत देखें।",
    analyticsIntroScope: "पूर्वानुमान क्षेत्र",
    analyticsIntroScopeText: "डिप्रेशन, एंग्जायटी, तनाव, नींद संबंधी समस्या, बर्नआउट, अकेलापन और पदार्थ दुरुपयोग।",
    detailAnalysisTitle: "वर्तमान आकलन का विस्तृत घटक-आधारित विश्लेषण।",
    recordsHeadingText: "रिकॉर्ड खोजें, व्यक्तिगत परिणाम देखें और PDF रिपोर्ट निर्यात करें।",
    recordLookupPlaceholder: "खोजने के लिए आकलन ID दर्ज करें",
    fetchRecordBtn: "रिकॉर्ड खोजें",
    downloadPdfBtn: "चयनित PDF डाउनलोड करें",
    domainScoreComparisonTitle: "डोमेन स्कोर तुलना",
    domainScoreComparisonText: "प्रश्नावली स्कोर बनाम संयुक्त AI स्कोर",
    modalityQualityShortText: "उपलब्धता, कॉन्फिडेंस और प्रोसेसिंग गुणवत्ता",
    modalityQualityHelperText: "यह अनुभाग समझने में मदद करता है कि कौन-से इनपुट अंतिम निर्णय के लिए पर्याप्त मज़बूत थे।",
    domainScoreComparisonDescription: "यह अनुभाग हर स्थिति के लिए स्व-रिपोर्ट किए गए लक्षणों की अंतिम बहु-मॉडेल AI स्कोर से तुलना करता है।",
    domainAnalysisTitle: "डोमेन विश्लेषण",
    domainAnalysisText: "हर पूर्वानुमान क्षेत्र के लिए प्रश्नावली बनाम संयुक्त AI स्कोर",
    componentContributionTitle: "घटक योगदान",
    componentContributionText: "टेक्स्ट, ऑडियो और इमेज ने अंतिम आकलन को कैसे प्रभावित किया",
    modelStatisticsTitle: "मॉडल सांख्यिकी",
    modelStatisticsText: "इस आकलन में उपयोग किए गए डीप लर्निंग और NLP मॉडल विवरण",
    nlpSafetyTitle: "NLP और सुरक्षा संकेत",
    nlpSafetyText: "भाव, भावना, आत्म-हानि भाषा और वर्णन की व्याख्या",
    modalityQualityTitle: "मॉडेलिटी गुणवत्ता",
    modalityQualityText: "हर इनपुट स्ट्रीम की उपलब्धता, कॉन्फिडेंस और प्रोसेसिंग गुणवत्ता",
    recommendationTitle: "सिफारिश और फॉलो-अप",
    recommendationText: "उपयोगकर्ता व्याख्या, फॉलो-अप नोट और स्क्रीनिंग अस्वीकरण",
    recordsExplorerTitle: "आकलन एक्सप्लोरर",
    recordsExplorerText: "किसी एक रिकॉर्ड का विवरण देखने के लिए किसी पंक्ति पर क्लिक करें।",
    assessmentDetailTitle: "आकलन विवरण",
    assessmentDetailText: "उम्मीदवार प्रोफ़ाइल और जोखिम सारांश",
    scoreComparisonTitle: "स्कोर तुलना",
    scoreComparisonText: "प्रश्नावली बनाम डैशबोर्ड पूर्वानुमान",
    modalityBreakdownTitle: "मॉडेलिटी विवरण",
    modalityBreakdownText: "टेक्स्ट, ऑडियो मेटाडेटा और इमेज मेटाडेटा",
    featureSnapshotTitle: "फीचर स्नैपशॉट",
    featureSnapshotText: "चयनित आकलन के NLP और रिकॉर्ड फीचर",
    patientHistoryTitle: "रोगी इतिहास",
    patientHistoryText: "पिछली स्क्रीनिंग और समय के साथ कुल जोखिम में बदलाव",
    domainTrajectoryTitle: "डोमेन ड्रिफ्ट",
    domainTrajectoryText: "कौन से जोखिम डोमेन बिगड़ रहे हैं, सुधर रहे हैं, या स्थिर हैं",
    questionnaireRiskTitle: "प्रश्नावली जोखिम",
    questionnaireOverall: "प्रश्नावली कुल स्कोर",
    combinedResultTitle: "संयुक्त डैशबोर्ड परिणाम",
    confidenceLabel: "कॉन्फिडेंस",
    recommendationLabel: "सिफारिश",
    questionnaireLabel: "प्रश्नावली",
    dashboardLabel: "डैशबोर्ड",
    combinedAiLabel: "संयुक्त AI",
    noDataModality: "इस मॉडेलिटी के लिए कोई डेटा उपलब्ध नहीं है।",
    noQuestionnaireNotesLabel: "प्रश्नावली नोट उपलब्ध नहीं हैं।",
    availableLabel: "उपलब्ध",
    uploadReceivedLabel: "अपलोड मिला, लेकिन विश्लेषण योग्य नहीं",
    notAvailableLabel: "उपलब्ध नहीं",
    noFeaturesLabel: "इस रिकॉर्ड के लिए कोई कच्चे फीचर मान उपलब्ध नहीं हैं।",
    noMatchRecords: "मौजूदा फ़िल्टर से कोई आकलन मेल नहीं खाता।",
    previousLabel: "पिछला",
    nextLabel: "अगला",
    riskLabel: "जोखिम",
    noRecordsLoaded: "अभी तक कोई रिकॉर्ड लोड नहीं हुआ है।",
    pageStatus: "पृष्ठ {page} / {total}",
    noAssessmentAnalysis: "अभी तक कोई आकलन विश्लेषण उपलब्ध नहीं है।",
    noComponentBreakdown: "अभी तक कोई घटक-विश्लेषण उपलब्ध नहीं है।",
    noModalityQuality: "अभी तक मॉडेलिटी गुणवत्ता जानकारी उपलब्ध नहीं है।",
    noRecommendationDetails: "अभी तक कोई सिफारिश विवरण उपलब्ध नहीं है।",
    noModelStats: "अभी तक कोई मॉडल सांख्यिकी उपलब्ध नहीं है।",
    noNlpSummary: "अभी तक कोई NLP संकेत सारांश उपलब्ध नहीं है।",
    sentimentLabel: "भाव",
    emotionLabel: "भावना",
    safetyLanguageLabel: "सुरक्षा भाषा",
    transformerLabel: "ट्रांसफॉर्मर",
    audioModalityLabel: "ऑडियो मॉडेलिटी",
    imageModalityLabel: "इमेज मॉडेलिटी",
    readinessScoreLabel: "तैयारी स्कोर",
    completionLabel: "पूर्णता",
    needsAttention: "ध्यान आवश्यक",
    readyLabel: "तैयार",
    infoLabel: "जानकारी",
    livePreviewLabel: "लाइव प्रीव्यू",
    savedAtLabel: "सहेजा गया",
    fetchPrompt: "रिकॉर्ड लाने से पहले आकलन आईडी दर्ज करें।",
    fetchSuccess: "आकलन {id} बैकएंड API से प्राप्त हुआ।",
    fetchMissing: "उस आकलन आईडी से कोई रिकॉर्ड नहीं मिला।",
    deleteRecord: "रिकॉर्ड हटाएँ",
    deleteRecordConfirm: "क्या इस आकलन को स्थायी रूप से हटाना है?",
    deleteRecordSuccess: "आकलन {id} हटा दिया गया।",
    deleteRecordFailed: "{id} आकलन हटाया नहीं जा सका।",
    deleteRecordRequiresOnline: "सिंक किए गए रिकॉर्ड को हटाने के लिए ऑनलाइन कनेक्शन चाहिए।",
    deleteRecordNotFound: "चुना गया आकलन नहीं मिला।",
    hiddenDemoRecord: "डेमो/बैकएंड रिकॉर्ड उपयोगकर्ता सूची से छिपाए गए हैं।",
    noDataLabel: "कोई डेटा नहीं",
    noDataMetricLabel: "कोई डेटा नहीं",
    unknownUserLabel: "बिना नाम का उपयोगकर्ता",
    unknownLocationLabel: "अज्ञात स्थान",
    unknownLabel: "अज्ञात",
    notStatedLabel: "दर्ज नहीं",
    unavailableLabel: "उपलब्ध नहीं",
    noneLabel: "कोई नहीं",
    detectedLabel: "पाया गया",
    notDetectedLabel: "नहीं पाया गया",
    currentLabel: "वर्तमान",
    currentUserLabel: "वर्तमान उपयोगकर्ता",
    topComorbidityLabel: "शीर्ष सह-रुग्णता",
    scoreLabel: "स्कोर",
    featuresLabel: "विशेषताएँ",
    recommendationAndDisclaimerTitle: "सिफारिश और अस्वीकरण",
    recommendationTitle: "सिफारिश",
    screeningDisclaimerTitle: "स्क्रीनिंग अस्वीकरण",
    noRecommendationText: "कोई सिफारिश उपलब्ध नहीं है।",
    noDisclaimerText: "कोई अस्वीकरण उपलब्ध नहीं है।",
    recommendationOverviewText: "यह क्षेत्र उपयोगकर्ता को स्क्रीनिंग व्याख्या और उचित फॉलो-अप नोट देता है।",
    overallRiskTrajectoryTitle: "कुल जोखिम रुझान",
    trajectoryModelTitle: "अनुदैर्ध्य रुझान",
    trajectoryModelText: "एक ही व्यक्ति की बार-बार स्क्रीनिंग के बीच रुझान मॉडलिंग",
    screeningCountLabel: "{status} - {count} स्क्रीनिंग",
    trendSummaryTitle: "रुझान सारांश",
    trajectorySummaryTitle: "रुझान सारांश",
    trajectorySummaryText: "आधार से परिवर्तन, हाल का परिवर्तन और डोमेन गति",
    statusTitle: "स्थिति",
    trajectoryMetricsTitle: "रुझान मीट्रिक्स",
    baselineToCurrentLabel: "आधार {baseline} से वर्तमान {current} तक",
    changeSinceBaselineLabel: "आधार से परिवर्तन",
    recentChangeLabel: "हाल का परिवर्तन",
    volatilityLabel: "अस्थिरता",
    noTrajectoryLabel: "अभी तक कोई दीर्घकालिक रुझान उपलब्ध नहीं है।",
    noTrendSummaryLabel: "अभी तक कोई रुझान सारांश उपलब्ध नहीं है।",
    noMoreDataLabel: "और डेटा चाहिए",
    noTrainedModelStatsLabel: "इस आकलन के लिए अभी कोई प्रशिक्षित मॉडल आँकड़े उपलब्ध नहीं हैं।",
    trainedBundleComparisonTitle: "प्रशिक्षित बंडल तुलना",
    macroR2CoverageText: "मॉडेलिटी के अनुसार Macro R2 और सैंपल कवरेज",
    trainedBundleDescription: "यह मौजूदा सहेजे गए मॉडल मेटाडेटा का उपयोग करके टेक्स्ट, ऑडियो और इमेज के स्थानीय रूप से प्रशिक्षित बंडल की गुणवत्ता की तुलना करता है।",
    textTransformerLabel: "पाठ ट्रांसफॉर्मर",
    trainedModalitiesLabel: "प्रशिक्षित मॉडेलिटियाँ",
    confidenceHintLabel: "विश्वास संकेत",
    trainedBundleLabel: "प्रशिक्षित बंडल",
    fallbackLabel: "विकल्प",
    trainedAtLabel: "प्रशिक्षण समय",
    safetyKeywordsLabel: "सुरक्षा शब्द",
    keywordMatchesLabel: "मिलान शब्द",
    narrativeWordCountLabel: "विवरण शब्द गणना",
    emotionIntensityLabel: "भाव तीव्रता",
    domainCoverageLabel: "डोमेन कवरेज",
    analysisEngineLabel: "इंजन",
    macroR2Label: "Macro R2",
    samplesLabel: "नमूने",
    domainsLabel: "डोमेन",
    manifestLabel: "मैनिफेस्ट",
    datasetRootLabel: "डेटासेट रूट",
    trendModelDescription: "रुझान मॉडलिंग में बार-बार हुई स्क्रीनिंग, ढलान और अस्थिरता को मिलाकर यह देखा जाता है कि जोखिम बढ़ रहा है, घट रहा है या उतार-चढ़ाव कर रहा है।",
    noFilteredExportLabel: "निर्यात करने के लिए कोई फ़िल्टर किया गया रिकॉर्ड नहीं है।",
    exportedFilteredLabel: "{count} फ़िल्टर किए गए रिकॉर्ड निर्यात किए गए।",
    backendApiLabel: "बैकएंड API",
    sampleDatasetLabel: "बंडल किया गया सैंपल डेटासेट",
    localOfflineStorageLabel: "स्थानीय ऑफलाइन स्टोरेज",
    offlineQueueSyncedLabel: "जहाँ संभव हुआ, ऑफलाइन क्यू सिंक हो गई और स्थानीय रिकॉर्ड ताज़ा कर दिए गए।",
    savedOfflineQueuedLabel: "आकलन ऑफलाइन सहेजा गया। कनेक्शन वापस आते ही यह अपने आप सिंक हो जाएगा।",
    backendUnavailableSavedOfflineLabel: "बैकएंड उपलब्ध नहीं है। आकलन ऑफलाइन सहेज दिया गया और सिंक के लिए कतार में डाल दिया गया।",
    backendPreviewUnavailableLabel: "बैकएंड प्रीव्यू उपलब्ध नहीं है। इसके बजाय ऑफलाइन हीयूरिस्टिक प्रीव्यू दिखाया जा रहा है।",
    loadedOfflineRecordLabel: "{id} ऑफलाइन स्टोरेज से लोड किया गया।",
    savedOfflineQueuedShortLabel: "ऑफलाइन सहेजा गया और सिंक के लिए कतार में डाल दिया गया।",
    savedOfflineQueuedAfterApiLabel: "API अनुपलब्ध होने के बाद ऑफलाइन सहेजा गया।",
    loadRecordsFromApiFailedLabel: "बैकएंड API से रिकॉर्ड लोड नहीं हो सके। आवश्यकता हो तो JSON फाइल मैन्युअली आयात करें।",
    offlineRecordsLoadedLabel: "बैकएंड उपलब्ध नहीं है। ऑफलाइन स्टोरेज से रिकॉर्ड लोड किए गए।",
    loadRecordsFromApiGenericErrorLabel: "बैकएंड API से रिकॉर्ड लोड नहीं हो सके।",
    offlineModeActiveLabel: "ऑफलाइन मोड सक्रिय है। नए आकलन स्थानीय रूप से सहेजे जाएंगे और बाद में सिंक होंगे।",
    onlineSyncReadyLabel: "ऑनलाइन सिंक तैयार है",
    offlineModeQueuedLabel: "ऑफलाइन मोड सक्रिय | {count} कतार में",
    offlineScreeningElevatedLabel: "ऑफलाइन स्क्रीनिंग में {domain} जोखिम अधिक दिख रहा है। बैकएंड समीक्षा के लिए कनेक्शन उपलब्ध होने पर इस आकलन को सिंक करें।",
    offlineScreeningCompletedLabel: "ऑफलाइन स्क्रीनिंग पूरी हुई। बैकएंड पुष्टि के लिए कनेक्शन उपलब्ध होने पर इस आकलन को सिंक करें।",
    pdfReportTitle: "ग्रामीण मानसिक स्वास्थ्य स्क्रीनिंग डैशबोर्ड रिपोर्ट",
    pdfQuestionnaireLabel: "प्रश्नावली",
    pdfDashboardLabel: "डैशबोर्ड",
    pdfRecommendationLabel: "सिफारिश",
    pdfWhyFlaggedLabel: "{domain} को क्यों चिह्नित किया गया",
    pdfTopContributorsLabel: "इस डोमेन के लिए शीर्ष मॉडल योगदानकर्ता:",
    usableLabel: "उपयोगी",
    limitedLabel: "सीमित",
    noModalityNoteLabel: "मोडालिटी के लिए कोई नोट उपलब्ध नहीं है।",
    noAdditionalProcessingStatsLabel: "अतिरिक्त प्रोसेसिंग सांख्यिकी उपलब्ध नहीं है।",
    whyFlaggedLabel: "{domain} को क्यों चिह्नित किया गया",
    topModelContributorsLabel: "इस डोमेन के लिए शीर्ष मॉडल योगदानकर्ता:",
  },
  Bengali: {
    adaptiveTab: "অভিযোজিত পরীক্ষা",
    workspaceTab: "মূল্যায়ন কর্মক্ষেত্র",
    heroEyebrow: "স্ক্রিনিং শুরু করুন",
    heroTitle: "গ্রামীণ মানসিক স্বাস্থ্য স্ক্রিনিং",
    heroText: "একবারে একটি ডায়াগনস্টিক স্ক্রিনিং সেশন শুরু করুন, ফলাফল সংরক্ষণ করুন, এবং ব্যাকগ্রাউন্ড রেকর্ড লোড না করেই বর্তমান মূল্যায়ন দেখুন।",
    heroMetricRisk: "ঝুঁকির ডোমেইন ট্র্যাক করা হয়",
    heroMetricModalities: "মডালিটি মিশ্রিত",
    heroMetricOffline: "অফলাইন ক্যাপচার সহায়তা",
    dashboardLanguageLabel: "ড্যাশবোর্ড ভাষা",
    analyticsTab: "বিশ্লেষণ কেন্দ্র",
    recordsTab: "রেকর্ড ও রিপোর্ট",
    applyLanguageBtn: "ভাষা প্রয়োগ করুন",
    intakeFlowTitle: "শুরু থেকে শেষ পর্যন্ত একটি স্ক্রিনিং সম্পূর্ণ করুন",
    intakeFlowText: "ব্যক্তির তথ্য পূরণ করুন, প্রতিক্রিয়া নিন, লাইভ প্রিভিউ দেখুন, এবং বিশ্লেষণের জন্য চূড়ান্ত মূল্যায়ন সংরক্ষণ করুন।",
    step1Title: "প্রোফাইল ও সম্মতি নিন",
    step1Text: "পরিচয়, গ্রাম, মূল্যায়নকারী, ভাষা ও সম্মতি দিয়ে শুরু করুন যাতে রেকর্ড সম্পূর্ণ হয়।",
    step2Title: "উপসর্গ ও বর্ণনা সংগ্রহ করুন",
    step2Text: "শক্তিশালী মূল্যায়নের জন্য প্রশ্নমালা, লিখিত উত্তর, এবং ঐচ্ছিক কণ্ঠ বা মুখের ইনপুট ব্যবহার করুন।",
    step3Title: "সহায়ক ইনপুট যোগ করুন",
    step3Text: "লিখিত উত্তর দিন অথবা কণ্ঠ রেকর্ড করুন। ছবির জন্য লাইভ ছবি তুলুন বা ফাইল আপলোড করুন।",
    step4Title: "রিভিউ করে বিশ্লেষণের জন্য সংরক্ষণ করুন",
    step4Text: "সংরক্ষণ করার পর ফলাফল Analytics Hub এবং Records and Reports-এ দেখা যাবে।",
    questionnaireTitle: "প্রশ্নমালা",
    questionnaireSubtitle: "গত দুই সপ্তাহে উপসর্গ কতবার দেখা গেছে তা নির্বাচন করুন।",
    questionnaireNotes: "ড্যাশবোর্ড প্রশ্নমালার স্কোর গত দুই সপ্তাহের উপসর্গের ঘনত্বের উপর ভিত্তি করে।",
    adaptiveTitle: "অ্যাডাপটিভ পরীক্ষা",
    adaptiveSubtitle: "ব্যাকএন্ড IRT selector ব্যবহার করে একবারে একটি প্রশ্ন করুন এবং workspace uploads পুনরায় ব্যবহার করুন।",
    adaptiveIntroFlowTitle: "অ্যাডাপটিভ প্রবাহ",
    adaptiveIntroFlowHeading: "একবারে একটি প্রশ্ন",
    adaptiveIntroFlowText: "ব্যাকএন্ড সবচেয়ে তথ্যবহ প্রশ্নটি বেছে নেয় এবং সেশনকে বর্তমান ভাষার সাথে সঙ্গতিপূর্ণ রাখে।",
    adaptiveIntroLanguageTitle: "ভাষা সমন্বয়",
    adaptiveIntroLanguageHeading: "ভাষা-সচেতন প্রম্পট",
    adaptiveIntroLanguageText: "প্রম্পট, উত্তর বিকল্প এবং সেশন নির্দেশনা নির্বাচিত dashboard ভাষা অনুযায়ী স্বয়ংক্রিয়ভাবে বদলে যায়।",
    adaptiveIntroSharedTitle: "শেয়ার করা ইনপুট",
    adaptiveIntroSharedHeading: "workspace ইনপুট পুনরায় ব্যবহার করুন",
    adaptiveIntroSharedText: "main screening workspace থেকে candidate profile এবং narrative input আবার না লিখেই ব্যবহার করুন।",
    adaptiveProfileTitle: "প্রার্থীর প্রোফাইল",
    adaptiveQuestionTitle: "অভিযোজিত প্রশ্ন",
    adaptiveQuestionHint: "প্রথম অভিযোজিত প্রশ্ন লোড করতে একটি সেশন শুরু করুন।",
    adaptiveNarrativeTitle: "ওয়ার্কস্পেস নোট",
    adaptiveStartBtn: "সেশন শুরু করুন",
    adaptiveNextBtn: "উত্তর জমা দিন",
    adaptiveResetBtn: "সেশন রিসেট করুন",
    adaptiveStatusIdle: "প্রথম প্রশ্ন লোড করতে অভিযোজিত সেশন শুরু করুন।",
    adaptiveStatusLoading: "পরবর্তী সবচেয়ে উপযোগী প্রশ্ন বেছে নেওয়া হচ্ছে...",
    adaptiveStatusReady: "অভিযোজিত প্রশ্ন প্রস্তুত।",
    adaptiveStatusComplete: "অভিযোজিত সেশন সম্পন্ন হয়েছে। রেকর্ড সংরক্ষিত হয়েছে।",
    adaptiveStatusError: "অভিযোজিত API উপলব্ধ নয়। অনুগ্রহ করে আবার চেষ্টা করুন।",
    candidateProfileTitle: "প্রার্থীর প্রোফাইল",
    freeTextTitle: "মুক্ত লেখা ও আপলোড তথ্য",
    fullNameLabel: "পূর্ণ নাম",
    ageLabel: "বয়স",
    genderLabel: "লিঙ্গ",
    villageLabel: "গ্রাম / এলাকা",
    phoneLabel: "ফোন / রেফারেন্স নম্বর",
    assessorLabel: "মূল্যায়নকারীর নাম",
    languageLabel: "পছন্দের ভাষা",
    consentLabel: "স্ক্রিনিং-এর জন্য সম্মতি পাওয়া গেছে",
    fullNamePlaceholder: "পূর্ণ নাম লিখুন",
    villagePlaceholder: "গ্রাম বা এলাকা",
    assessorPlaceholder: "স্বাস্থ্যকর্মী বা পরামর্শদাতা",
    narrativeLabel: "ব্যক্তি কেমন অনুভব করছেন তা বর্ণনা করুন",
    narrativePlaceholder: "উদাহরণ: আমি ক্লান্ত, বিচ্ছিন্ন, উদ্বিগ্ন এবং ঠিকমতো ঘুমাতে পারছি না।",
    genderOptions: ["অনুগ্রহ করে নির্বাচন করুন", "নারী", "পুরুষ", "অন্যান্য"],
    guidedSpeechTitle: "নির্দেশিত কণ্ঠ রেকর্ডিং",
    guidedSpeechTopic: "বিষয়: গত কয়েক দিন, ঘুম, চাপ ও মানুষের সাথে সংযোগ সম্পর্কে বলুন।",
    audioFileLabel: "কণ্ঠের নমুনা",
    liveFaceTitle: "লাইভ মুখের ছবি",
    liveFaceTopic: "মুখের সংকেত বিশ্লেষণের জন্য ওয়েবক্যাম থেকে একটি পরিষ্কার সামনের ছবি তুলুন।",
    imageFileLabel: "মুখের ছবি",
    saveAssessmentBtn: "মূল্যায়ন সংরক্ষণ করুন",
    resetAssessmentBtn: "ফর্ম রিসেট করুন",
    workspaceStatusDefault: "ফলাফল দেখতে মূল্যায়ন সম্পূর্ণ করে সংরক্ষণ করুন।",
    workspacePredictionEmpty: "লাইভ প্রেডিকশন প্রিভিউ পেতে মূল্যায়ন পূরণ শুরু করুন।",
    workspaceNlpEmpty: "বর্ণনা লিখতে থাকলে NLP সংকেত এখানে দেখা যাবে।",
    workspaceReadinessEmpty: "প্রস্তুতির বার্তা দেখতে বিবরণ, সম্মতি, প্রশ্নমালা ও বর্ণনা পূরণ করুন।",
    workspacePredictionTitle: "লাইভ প্রেডিকশন প্রিভিউ",
    workspacePredictionText: "সংরক্ষণের আগে প্রশ্নমালা ও NLP-এর যৌথ প্রিভিউ",
    workspaceNlpTitle: "লাইভ NLP ইনসাইটস",
    workspaceNlpText: "বর্ণনা পাঠ থেকে সেন্টিমেন্ট, আবেগ ও নিরাপত্তা সংকেত",
    workspaceReadinessTitle: "ইনটেক প্রস্তুতি",
    workspaceReadinessText: "রেকর্ডটি সংরক্ষণ ও বিশ্লেষণের জন্য প্রস্তুত কি না তা যাচাই করে",
    analyticsBannerDefault: "বিস্তারিত বিশ্লেষণ দেখতে মূল্যায়ন সম্পূর্ণ করে সংরক্ষণ করুন।",
    recordsBannerDefault: "পুরোনো রিপোর্ট দেখতে বা ডাউনলোড করতে মূল্যায়ন আইডি দিয়ে রেকর্ড আনুন।",
    analyticsReady: "এর বিস্তারিত অংশভিত্তিক বিশ্লেষণ প্রস্তুত।",
    savedMessage: "ব্যাকএন্ড API-এর মাধ্যমে সংরক্ষিত হয়েছে।",
    analyticsShowing: "Analytics Hub এখন এই মূল্যায়ন দেখাচ্ছে",
    saveInProgress: "Python NLP ব্যাকএন্ডের মাধ্যমে মূল্যায়ন সংরক্ষণ করা হচ্ছে...",
    previewRefreshing: "Python NLP ব্যাকএন্ড থেকে লাইভ প্রিভিউ আপডেট করা হচ্ছে...",
    noRecordSelected: "কোনো মূল্যায়ন নির্বাচন করা হয়নি।",
    assessmentIdLabel: "মূল্যায়ন আইডি",
    overallConfidenceLabel: "সামগ্রিক কনফিডেন্স",
    overallRiskLabel: "সামগ্রিক ঝুঁকি",
    candidateLabel: "প্রার্থী",
    villageShortLabel: "গ্রাম",
    assessorShortLabel: "মূল্যায়নকারী",
    createdAtLabel: "সময়",
    analyticsIntroCurrent: "একটি মূল্যায়ন এখন কেন্দ্রে",
    analyticsIntroCurrentText: "Analytics Hub আর আগের রেকর্ড নিজে থেকে টেনে আনে না; এখন এটি সদ্য সংরক্ষিত বর্তমান মূল্যায়নটিকেই ব্যাখ্যা করে।",
    analyticsIntroModel: "মডেল বিশ্লেষণ",
    analyticsIntroModelText: "এই মূল্যায়নের জন্য ডোমেইনভিত্তিক স্কোর, ইনপুটের মান, কনফিডেন্স, ট্রান্সফর্মার ব্যবহার এবং NLP সংকেত দেখুন।",
    analyticsIntroScope: "পূর্বাভাসের ক্ষেত্র",
    analyticsIntroScopeText: "বিষণ্নতা, উদ্বেগ, চাপ, ঘুমের সমস্যা, বার্নআউট, একাকীত্ব এবং পদার্থের অপব্যবহার।",
    detailAnalysisTitle: "বর্তমান মূল্যায়নের বিস্তারিত অংশভিত্তিক বিশ্লেষণ।",
    recordsHeadingText: "রেকর্ড আনুন, ব্যক্তিগত ফলাফল দেখুন এবং PDF রিপোর্ট ডাউনলোড করুন।",
    recordLookupPlaceholder: "রেকর্ড আনতে মূল্যায়ন আইডি লিখুন",
    fetchRecordBtn: "রেকর্ড আনুন",
    downloadPdfBtn: "নির্বাচিত PDF ডাউনলোড করুন",
    domainScoreComparisonTitle: "ডোমেইন স্কোর তুলনা",
    domainScoreComparisonText: "প্রশ্নমালা স্কোর বনাম যৌথ AI স্কোর",
    modalityQualityShortText: "প্রাপ্যতা, কনফিডেন্স এবং প্রসেসিং মান",
    modalityQualityHelperText: "এই অংশটি বোঝাতে সাহায্য করে কোন ইনপুটগুলো চূড়ান্ত সিদ্ধান্তকে সমর্থন করার জন্য যথেষ্ট শক্তিশালী ছিল।",
    domainScoreComparisonDescription: "এই অংশটি প্রতিটি অবস্থার জন্য স্ব-প্রতিবেদিত উপসর্গের সাথে চূড়ান্ত বহুমাত্রিক backend স্কোর তুলনা করে।",
    domainAnalysisTitle: "ডোমেইন বিশ্লেষণ",
    domainAnalysisText: "প্রতিটি পূর্বাভাস ক্ষেত্রের জন্য প্রশ্নমালা ও যৌথ AI স্কোরের তুলনা",
    componentContributionTitle: "উপাদানের অবদান",
    componentContributionText: "টেক্সট, অডিও ও ইমেজ কীভাবে চূড়ান্ত মূল্যায়নকে প্রভাবিত করেছে",
    modelStatisticsTitle: "মডেল পরিসংখ্যান",
    modelStatisticsText: "এই মূল্যায়নে ব্যবহৃত ডিপ লার্নিং ও NLP মডেলের বিবরণ",
    nlpSafetyTitle: "NLP ও নিরাপত্তা সংকেত",
    nlpSafetyText: "সেন্টিমেন্ট, আবেগ, আত্মক্ষতির ভাষা এবং বর্ণনার ব্যাখ্যা",
    modalityQualityTitle: "ইনপুটের মান",
    modalityQualityText: "প্রতিটি ইনপুট উৎসের প্রাপ্যতা, কনফিডেন্স এবং প্রসেসিং মান",
    recommendationTitle: "পরামর্শ ও পরবর্তী পদক্ষেপ",
    recommendationText: "ব্যবহারকারী-বান্ধব ব্যাখ্যা, ফলো-আপ নোট এবং স্ক্রিনিং সতর্কীকরণ",
    recordsExplorerTitle: "মূল্যায়ন অনুসন্ধান",
    recordsExplorerText: "একটি নির্দিষ্ট রেকর্ডের বিস্তারিত দেখতে যে কোনো সারিতে ক্লিক করুন।",
    assessmentDetailTitle: "মূল্যায়নের বিস্তারিত",
    assessmentDetailText: "প্রার্থীর প্রোফাইল ও ঝুঁকির সারাংশ",
    scoreComparisonTitle: "স্কোরের তুলনা",
    scoreComparisonText: "প্রশ্নমালা বনাম ড্যাশবোর্ড পূর্বাভাস",
    modalityBreakdownTitle: "ইনপুটভিত্তিক বিশ্লেষণ",
    modalityBreakdownText: "টেক্সট, অডিও মেটাডেটা এবং ইমেজ মেটাডেটা",
    featureSnapshotTitle: "ফিচার স্ন্যাপশট",
    featureSnapshotText: "নির্বাচিত মূল্যায়নের NLP ও রেকর্ড ফিচার",
    patientHistoryTitle: "রোগীর ইতিহাস",
    patientHistoryText: "পূর্ববর্তী স্ক্রিনিং এবং সময়ের সঙ্গে সামগ্রিক ঝুঁকির পরিবর্তন",
    domainTrajectoryTitle: "ডোমেইন ড্রিফট",
    domainTrajectoryText: "কোন ঝুঁকির ডোমেইনগুলো খারাপ হচ্ছে, উন্নত হচ্ছে, বা স্থিতিশীল আছে",
    questionnaireRiskTitle: "প্রশ্নমালার ঝুঁকি",
    questionnaireOverall: "প্রশ্নমালার সামগ্রিক স্কোর",
    combinedResultTitle: "সমন্বিত ড্যাশবোর্ড ফলাফল",
    confidenceLabel: "কনফিডেন্স",
    recommendationLabel: "পরামর্শ",
    questionnaireLabel: "প্রশ্নমালা",
    dashboardLabel: "ড্যাশবোর্ড",
    combinedAiLabel: "যৌথ AI",
    noDataModality: "এই ইনপুট উৎসের জন্য কোনো তথ্য পাওয়া যায়নি।",
    noQuestionnaireNotesLabel: "প্রশ্নমালার কোনো নোট নেই।",
    availableLabel: "উপলব্ধ",
    uploadReceivedLabel: "আপলোড পাওয়া গেছে, তবে বিশ্লেষণযোগ্য নয়",
    notAvailableLabel: "উপলব্ধ নয়",
    noFeaturesLabel: "এই রেকর্ডের জন্য কোনো কাঁচা ফিচার মান সংরক্ষিত নেই।",
    noMatchRecords: "বর্তমান ফিল্টারের সাথে কোনো মূল্যায়ন মেলেনি।",
    previousLabel: "পূর্ববর্তী",
    nextLabel: "পরবর্তী",
    riskLabel: "ঝুঁকি",
    noRecordsLoaded: "এখনও কোনো রেকর্ড লোড করা হয়নি।",
    pageStatus: "পৃষ্ঠা {page} / {total}",
    noAssessmentAnalysis: "এখনও কোনো মূল্যায়ন বিশ্লেষণ পাওয়া যায়নি।",
    noComponentBreakdown: "এখনও কোনো উপাদানভিত্তিক বিশ্লেষণ পাওয়া যায়নি।",
    noModalityQuality: "এখনও ইনপুটের মান-সংক্রান্ত তথ্য পাওয়া যায়নি।",
    noRecommendationDetails: "এখনও কোনো পরামর্শের বিস্তারিত পাওয়া যায়নি।",
    noModelStats: "এখনও কোনো মডেল পরিসংখ্যান পাওয়া যায়নি।",
    noNlpSummary: "এখনও কোনো NLP সংকেতের সারাংশ পাওয়া যায়নি।",
    sentimentLabel: "অনুভূতির প্রবণতা",
    emotionLabel: "প্রধান আবেগ",
    safetyLanguageLabel: "নিরাপত্তা-সংক্রান্ত ভাষা",
    transformerLabel: "ট্রান্সফর্মার",
    audioModalityLabel: "অডিও ইনপুট",
    imageModalityLabel: "ছবিভিত্তিক ইনপুট",
    readinessScoreLabel: "প্রস্তুতির স্কোর",
    completionLabel: "সম্পূর্ণতা",
    needsAttention: "অতিরিক্ত মনোযোগ দরকার",
    readyLabel: "প্রস্তুত",
    infoLabel: "তথ্য",
    livePreviewLabel: "লাইভ প্রিভিউ",
    savedAtLabel: "সংরক্ষিত হয়েছে",
    fetchPrompt: "রেকর্ড আনার আগে মূল্যায়ন আইডি লিখুন।",
    fetchSuccess: "মূল্যায়ন {id} ব্যাকএন্ড API থেকে আনা হয়েছে।",
    fetchMissing: "ওই মূল্যায়ন আইডির কোনো রেকর্ড পাওয়া যায়নি।",
    deleteRecord: "রেকর্ড মুছুন",
    deleteRecordConfirm: "এই মূল্যায়ন স্থায়ীভাবে মুছবেন?",
    deleteRecordSuccess: "মূল্যায়ন {id} মুছে ফেলা হয়েছে।",
    deleteRecordFailed: "{id} মূল্যায়ন মুছতে ব্যর্থ হয়েছে।",
    deleteRecordRequiresOnline: "সিঙ্ক করা রেকর্ড মুছতে অনলাইন সংযোগ প্রয়োজন।",
    deleteRecordNotFound: "নির্বাচিত মূল্যায়নটি পাওয়া যায়নি।",
    hiddenDemoRecord: "ডেমো/ব্যাকএন্ড রেকর্ড ব্যবহারকারী তালিকা থেকে লুকানো হয়েছে।",
    noDataLabel: "কোনো তথ্য নেই",
    noDataMetricLabel: "কোনো তথ্য নেই",
    unknownUserLabel: "নামহীন ব্যবহারকারী",
    unknownLocationLabel: "অজানা স্থান",
    unknownLabel: "অজানা",
    notStatedLabel: "উল্লেখ করা হয়নি",
    unavailableLabel: "উপলব্ধ নয়",
    noneLabel: "কিছু নেই",
    detectedLabel: "সনাক্ত হয়েছে",
    notDetectedLabel: "সনাক্ত হয়নি",
    currentLabel: "বর্তমান",
    currentUserLabel: "বর্তমান ব্যবহারকারী",
    topComorbidityLabel: "শীর্ষ সহ-অসুস্থতা",
    scoreLabel: "স্কোর",
    featuresLabel: "বৈশিষ্ট্য",
    recommendationAndDisclaimerTitle: "সুপারিশ ও সতর্কীকরণ",
    recommendationTitle: "সুপারিশ",
    screeningDisclaimerTitle: "স্ক্রিনিং সতর্কীকরণ",
    noRecommendationText: "কোনো সুপারিশ নেই।",
    noDisclaimerText: "কোনো সতর্কীকরণ নেই।",
    recommendationOverviewText: "এই অংশে ব্যবহারকারীর জন্য স্ক্রিনিং ব্যাখ্যা ও উপযুক্ত ফলো-আপ নোট দেওয়া হয়।",
    overallRiskTrajectoryTitle: "সামগ্রিক ঝুঁকির প্রবণতা",
    trajectoryModelTitle: "দীর্ঘমেয়াদি প্রবণতা",
    trajectoryModelText: "একই ব্যক্তির পুনরাবৃত্ত স্ক্রিনিং জুড়ে প্রবণতা মডেলিং",
    screeningCountLabel: "{status} — {count}টি স্ক্রিনিং",
    trendSummaryTitle: "প্রবণতার সারাংশ",
    trajectorySummaryTitle: "প্রবণতার সারাংশ",
    trajectorySummaryText: "বেসলাইন থেকে পরিবর্তন, সাম্প্রতিক পরিবর্তন, এবং ডোমেইন গতি",
    statusTitle: "অবস্থা",
    trajectoryMetricsTitle: "প্রবণতার মেট্রিক্স",
    baselineToCurrentLabel: "বেসলাইন {baseline} থেকে বর্তমান {current} পর্যন্ত",
    changeSinceBaselineLabel: "বেসলাইন থেকে পরিবর্তন",
    recentChangeLabel: "সাম্প্রতিক পরিবর্তন",
    volatilityLabel: "অস্থিরতা",
    noTrajectoryLabel: "এখনও কোনো দীর্ঘমেয়াদি প্রবণতা পাওয়া যায়নি।",
    noTrendSummaryLabel: "এখনও কোনো প্রবণতার সারাংশ পাওয়া যায়নি।",
    noMoreDataLabel: "আরও তথ্য প্রয়োজন",
    noTrainedModelStatsLabel: "এই মূল্যায়নের জন্য এখনও কোনো প্রশিক্ষিত মডেল পরিসংখ্যান নেই।",
    trainedBundleComparisonTitle: "প্রশিক্ষিত বান্ডেল তুলনা",
    macroR2CoverageText: "মডালিটি অনুযায়ী Macro R2 এবং স্যাম্পল কভারেজ",
    trainedBundleDescription: "এটি বর্তমান সংরক্ষিত মডেল মেটাডেটা ব্যবহার করে টেক্সট, অডিও এবং ইমেজের স্থানীয়ভাবে প্রশিক্ষিত বান্ডেলের মান তুলনা করে।",
    textTransformerLabel: "টেক্সট ট্রান্সফর্মার",
    trainedModalitiesLabel: "প্রশিক্ষিত ইনপুট উৎস",
    confidenceHintLabel: "আত্মবিশ্বাস সূচক",
    trainedBundleLabel: "প্রশিক্ষিত বান্ডেল",
    fallbackLabel: "ফলব্যাক",
    trainedAtLabel: "প্রশিক্ষণের সময়",
    safetyKeywordsLabel: "নিরাপত্তা কীওয়ার্ড",
    keywordMatchesLabel: "মিলে যাওয়া কীওয়ার্ড",
    narrativeWordCountLabel: "বর্ণনার শব্দসংখ্যা",
    emotionIntensityLabel: "আবেগের তীব্রতা",
    domainCoverageLabel: "ডোমেইন কভারেজ",
    analysisEngineLabel: "ইঞ্জিন",
    macroR2Label: "Macro R2",
    samplesLabel: "নমুনা",
    domainsLabel: "ডোমেইন",
    manifestLabel: "ম্যানিফেস্ট",
    datasetRootLabel: "ডেটাসেট রুট",
    trendModelDescription: "পুনরাবৃত্ত ভিজিট, ঢাল এবং অস্থিরতা একত্র করে ট্রেন্ড মডেলিং করা হয় যাতে স্বাস্থ্যকর্মীরা ঝুঁকি বাড়ছে, কমছে, নাকি ওঠানামা করছে তা বুঝতে পারেন।",
    noFilteredExportLabel: "রপ্তানি করার মতো কোনো ফিল্টার করা রেকর্ড নেই।",
    exportedFilteredLabel: "{count}টি ফিল্টার করা রেকর্ড রপ্তানি হয়েছে।",
    backendApiLabel: "ব্যাকএন্ড API",
    sampleDatasetLabel: "সংযুক্ত স্যাম্পল ডেটাসেট",
    localOfflineStorageLabel: "স্থানীয় অফলাইন স্টোরেজ",
    offlineQueueSyncedLabel: "যেখানে সম্ভব অফলাইন কিউ সিঙ্ক করা হয়েছে এবং স্থানীয় রেকর্ডগুলো রিফ্রেশ করা হয়েছে।",
    savedOfflineQueuedLabel: "মূল্যায়ন অফলাইনে সংরক্ষণ করা হয়েছে। সংযোগ ফিরে এলে এটি স্বয়ংক্রিয়ভাবে সিঙ্ক হবে।",
    backendUnavailableSavedOfflineLabel: "ব্যাকএন্ড অনুপলব্ধ। মূল্যায়নটি অফলাইনে সংরক্ষণ করে সিঙ্কের জন্য কিউ করা হয়েছে।",
    backendPreviewUnavailableLabel: "ব্যাকএন্ড প্রিভিউ অনুপলব্ধ। এর বদলে অফলাইন heuristic preview দেখানো হচ্ছে।",
    loadedOfflineRecordLabel: "{id} অফলাইন স্টোরেজ থেকে লোড করা হয়েছে।",
    savedOfflineQueuedShortLabel: "অফলাইনে সংরক্ষণ করা হয়েছে এবং সিঙ্কের জন্য কিউ করা হয়েছে।",
    savedOfflineQueuedAfterApiLabel: "API অনুপলব্ধ হওয়ার পরে অফলাইনে সংরক্ষণ করা হয়েছে।",
    loadRecordsFromApiFailedLabel: "ব্যাকএন্ড API থেকে রেকর্ড লোড করা যায়নি। প্রয়োজনে JSON ফাইল ম্যানুয়ালি আনুন।",
    offlineRecordsLoadedLabel: "ব্যাকএন্ড অনুপলব্ধ। অফলাইন স্টোরেজ থেকে রেকর্ড লোড করা হয়েছে।",
    loadRecordsFromApiGenericErrorLabel: "ব্যাকএন্ড API থেকে রেকর্ড লোড করা যায়নি।",
    offlineModeActiveLabel: "অফলাইন মোড সক্রিয়। নতুন মূল্যায়নগুলো স্থানীয়ভাবে সংরক্ষণ করা হবে এবং পরে সিঙ্ক হবে।",
    onlineSyncReadyLabel: "অনলাইন সিঙ্ক প্রস্তুত",
    offlineModeQueuedLabel: "অফলাইন মোড সক্রিয় | {count}টি কিউতে আছে",
    offlineScreeningElevatedLabel: "অফলাইন স্ক্রিনিংয়ে {domain} ঝুঁকি বেশি দেখা যাচ্ছে। ব্যাকএন্ড পর্যালোচনার জন্য সংযোগ উপলব্ধ হলে এই মূল্যায়নটি সিঙ্ক করুন।",
    offlineScreeningCompletedLabel: "অফলাইন স্ক্রিনিং সম্পন্ন হয়েছে। ব্যাকএন্ড নিশ্চিতকরণের জন্য সংযোগ উপলব্ধ হলে এই মূল্যায়নটি সিঙ্ক করুন।",
    pdfReportTitle: "গ্রামীণ মানসিক স্বাস্থ্য স্ক্রিনিং ড্যাশবোর্ড রিপোর্ট",
    pdfQuestionnaireLabel: "প্রশ্নমালা",
    pdfDashboardLabel: "ড্যাশবোর্ড",
    pdfRecommendationLabel: "পরামর্শ",
    pdfWhyFlaggedLabel: "{domain} কেন চিহ্নিত হয়েছে",
    pdfTopContributorsLabel: "এই ডোমেইনের জন্য শীর্ষ মডেল অবদানকারী:",
    usableLabel: "ব্যবহারযোগ্য",
    limitedLabel: "সীমিত",
    noModalityNoteLabel: "মডালিটির জন্য কোনো নোট নেই।",
    noAdditionalProcessingStatsLabel: "অতিরিক্ত প্রসেসিং পরিসংখ্যান নেই।",
    whyFlaggedLabel: "{domain} কেন চিহ্নিত হয়েছে",
    topModelContributorsLabel: "এই ডোমেইনের জন্য শীর্ষ মডেল অবদানকারী:",
  },
};

const QUESTION_BANK = [
  { id: "dep_interest", section: "Depression", domain: "depression", prompt: "Little interest or pleasure in daily activities." },
  { id: "dep_down", section: "Depression", domain: "depression", prompt: "Feeling down, hopeless, or emotionally low." },
  { id: "dep_sleep", section: "Depression", domain: "depression", prompt: "Sleep problems making the day harder." },
  { id: "dep_energy", section: "Depression", domain: "depression", prompt: "Low energy or feeling slowed down during the day." },
  { id: "dep_guilt", section: "Depression", domain: "depression", prompt: "Feeling like a burden, a failure, or blaming yourself too much." },
  { id: "dep_focus", section: "Depression", domain: "depression", prompt: "Difficulty focusing, remembering, or making simple decisions." },
  { id: "anx_worry", section: "Anxiety", domain: "anxiety", prompt: "Finding it hard to control worrying." },
  { id: "anx_restless", section: "Anxiety", domain: "anxiety", prompt: "Feeling nervous, restless, or on edge." },
  { id: "anx_fear", section: "Anxiety", domain: "anxiety", prompt: "Feeling afraid that something bad may happen." },
  { id: "anx_body", section: "Anxiety", domain: "anxiety", prompt: "Physical signs of anxiety such as racing heart, trembling, or sweating." },
  { id: "anx_avoid", section: "Anxiety", domain: "anxiety", prompt: "Avoiding people, places, or tasks because they increase anxiety." },
  { id: "anx_reassure", section: "Anxiety", domain: "anxiety", prompt: "Repeatedly needing reassurance before doing normal daily activities." },
  { id: "str_overload", section: "Stress", domain: "stress", prompt: "Daily responsibilities feeling too overwhelming." },
  { id: "str_irritable", section: "Stress", domain: "stress", prompt: "Feeling irritable, tense, or unable to relax." },
  { id: "str_function", section: "Stress", domain: "stress", prompt: "Stress affecting work, home life, or relationships." },
  { id: "str_pressure", section: "Stress", domain: "stress", prompt: "Feeling under constant pressure with too little time or support." },
  { id: "str_recovery", section: "Stress", domain: "stress", prompt: "Finding it hard to calm down or recover after a stressful event." },
  { id: "str_headaches", section: "Stress", domain: "stress", prompt: "Stress showing up as headaches, body pain, or stomach discomfort." },
  { id: "sleep_quality", section: "Sleep Disorder", domain: "sleep_disorder", prompt: "Trouble falling asleep, staying asleep, or waking too early." },
  { id: "sleep_daytime", section: "Sleep Disorder", domain: "sleep_disorder", prompt: "Poor sleep causing tiredness or sleepiness during the day." },
  { id: "sleep_routine", section: "Sleep Disorder", domain: "sleep_disorder", prompt: "An irregular sleep schedule that feels hard to control." },
  { id: "sleep_refresh", section: "Sleep Disorder", domain: "sleep_disorder", prompt: "Waking up feeling unrefreshed even after enough hours in bed." },
  { id: "sleep_worry", section: "Sleep Disorder", domain: "sleep_disorder", prompt: "Worrying about sleep so much that it becomes harder to rest." },
  { id: "sleep_interrupt", section: "Sleep Disorder", domain: "sleep_disorder", prompt: "Sleep frequently interrupted by dreams, worry, pain, or restlessness." },
  { id: "burnout_exhaustion", section: "Burnout", domain: "burnout", prompt: "Feeling emotionally or physically exhausted by responsibilities." },
  { id: "burnout_detachment", section: "Burnout", domain: "burnout", prompt: "Feeling detached, numb, or less motivated toward duties." },
  { id: "burnout_capacity", section: "Burnout", domain: "burnout", prompt: "Feeling unable to keep up with usual responsibilities." },
  { id: "burnout_cynical", section: "Burnout", domain: "burnout", prompt: "Feeling frustrated, cynical, or emotionally distant from your work or caregiving role." },
  { id: "burnout_reward", section: "Burnout", domain: "burnout", prompt: "Feeling that your effort is high but the return, appreciation, or support is low." },
  { id: "burnout_recovery", section: "Burnout", domain: "burnout", prompt: "Even after rest, still feeling drained and not fully recovered." },
  { id: "lonely_isolated", section: "Loneliness", domain: "loneliness", prompt: "Feeling alone or isolated even when people are nearby." },
  { id: "lonely_support", section: "Loneliness", domain: "loneliness", prompt: "Feeling that emotional support is lacking." },
  { id: "lonely_connection", section: "Loneliness", domain: "loneliness", prompt: "Finding it hard to feel connected to people around you." },
  { id: "lonely_belong", section: "Loneliness", domain: "loneliness", prompt: "Feeling that you do not fully belong in your family, workplace, or community." },
  { id: "lonely_share", section: "Loneliness", domain: "loneliness", prompt: "Having few people you can openly share worries or emotions with." },
  { id: "lonely_withdraw", section: "Loneliness", domain: "loneliness", prompt: "Withdrawing from conversations, gatherings, or relationships more than before." },
  { id: "substance_frequency", section: "Substance Abuse", domain: "substance_abuse", prompt: "Using alcohol, tobacco, or substances to cope with stress or emotions." },
  { id: "substance_control", section: "Substance Abuse", domain: "substance_abuse", prompt: "Finding it difficult to reduce or control substance use." },
  { id: "substance_impact", section: "Substance Abuse", domain: "substance_abuse", prompt: "Substance use affecting health, relationships, or responsibilities." },
  { id: "substance_craving", section: "Substance Abuse", domain: "substance_abuse", prompt: "Strong urges or cravings that are difficult to ignore." },
  { id: "substance_tolerance", section: "Substance Abuse", domain: "substance_abuse", prompt: "Needing more of the substance than before to get the same effect." },
  { id: "substance_withdrawal", section: "Substance Abuse", domain: "substance_abuse", prompt: "Feeling unwell, irritable, or restless when trying not to use the substance." },
];

const ADAPTIVE_SECTION_BASE_DIFFICULTY = {
  Depression: -0.2,
  Anxiety: -0.1,
  Stress: 0.0,
  "Sleep Disorder": 0.15,
  Burnout: 0.1,
  Loneliness: -0.05,
  "Substance Abuse": 0.25,
};

const ADAPTIVE_ITEM_OVERRIDES = {
  dep_interest: { a: 1.35, b: -0.25 },
  anx_worry: { a: 1.5, b: -0.1 },
  str_overload: { a: 1.2, b: 0.05 },
  sleep_quality: { a: 1.1, b: 0.2 },
};

const ADAPTIVE_MIN_ITEMS = 4;
const ADAPTIVE_MAX_ITEMS = 10;
const ADAPTIVE_INFO_THRESHOLD = 0.18;
const ADAPTIVE_DOMAIN_BALANCE_WEIGHT = 0.18;
const ADAPTIVE_THETA_PRIOR_SD = 1.5;
const ADAPTIVE_THETA_GRID_MIN = -3.0;
const ADAPTIVE_THETA_GRID_MAX = 3.0;
const ADAPTIVE_THETA_GRID_STEP = 0.05;
const ADAPTIVE_RESPONSE_THRESHOLDS = [-1.0, 0.0, 1.0];

const QUESTION_TRANSLATIONS = {
  dep_interest: { Hindi: "दैनिक गतिविधियों में रुचि या आनंद कम लगना।", Bengali: "দৈনন্দিন কাজে আগ্রহ বা আনন্দ কমে যাওয়া।" },
  dep_down: { Hindi: "उदास, निराश या भावनात्मक रूप से नीचे महसूस करना।", Bengali: "উদাস, নিরাশ বা মানসিকভাবে ভেঙে পড়া অনুভব করা।" },
  dep_sleep: { Hindi: "नींद की समस्या के कारण दिन और कठिन लगना।", Bengali: "ঘুমের সমস্যার কারণে দিন আরও কঠিন লাগা।" },
  dep_energy: { Hindi: "दिन में ऊर्जा कम होना या सुस्त महसूस करना।", Bengali: "দিনে শক্তি কম থাকা বা ধীর অনুভব করা।" },
  dep_guilt: { Hindi: "खुद को बोझ, असफल या बहुत अधिक दोषी महसूस करना।", Bengali: "নিজেকে বোঝা, ব্যর্থ বা অতিরিক্ত দোষী মনে হওয়া।" },
  dep_focus: { Hindi: "ध्यान, याददाश्त या छोटे फैसले लेने में कठिनाई।", Bengali: "মনোযোগ, স্মৃতি বা ছোট সিদ্ধান্ত নিতে অসুবিধা।" },
  anx_worry: { Hindi: "चिंता को नियंत्रित करना कठिन लगना।", Bengali: "দুশ্চিন্তা নিয়ন্ত্রণ করা কঠিন লাগা।" },
  anx_restless: { Hindi: "बेचैन, घबराया हुआ या तनावग्रस्त महसूस करना।", Bengali: "অস্থির, নার্ভাস বা চাপে থাকা অনুভব করা।" },
  anx_fear: { Hindi: "ऐसा डर लगना कि कुछ बुरा होने वाला है।", Bengali: "মনে হওয়া যে কিছু খারাপ ঘটতে পারে।" },
  anx_body: { Hindi: "घबराहट के शारीरिक संकेत जैसे दिल तेज चलना, कांपना या पसीना आना।", Bengali: "উদ্বেগের শারীরিক লক্ষণ যেমন হৃদস্পন্দন বেড়ে যাওয়া, কাঁপা বা ঘাম হওয়া।" },
  anx_avoid: { Hindi: "चिंता बढ़ने के डर से लोगों, जगहों या कामों से बचना।", Bengali: "উদ্বেগ বাড়ে বলে মানুষ, জায়গা বা কাজ এড়িয়ে চলা।" },
  anx_reassure: { Hindi: "साधारण काम करने से पहले बार-बार आश्वासन की जरूरत महसूस होना।", Bengali: "সাধারণ কাজের আগে বারবার আশ্বাসের প্রয়োজন অনুভব করা।" },
  str_overload: { Hindi: "दैनिक जिम्मेदारियाँ बहुत भारी लगना।", Bengali: "দৈনন্দিন দায়িত্ব খুব বেশি চাপের মনে হওয়া।" },
  str_irritable: { Hindi: "चिड़चिड़ापन, तनाव या आराम न कर पाना।", Bengali: "খিটখিটে লাগা, টানটান থাকা বা আরাম করতে না পারা।" },
  str_function: { Hindi: "तनाव का काम, घर या संबंधों पर असर पड़ना।", Bengali: "চাপের কারণে কাজ, বাড়ি বা সম্পর্ক ক্ষতিগ্রস্ত হওয়া।" },
  str_pressure: { Hindi: "लगातार दबाव महसूस होना और समय या समर्थन कम लगना।", Bengali: "নিরন্তর চাপ অনুভব করা এবং সময় বা সহায়তা কম মনে হওয়া।" },
  str_recovery: { Hindi: "तनावपूर्ण घटना के बाद शांत होने या संभलने में कठिनाई।", Bengali: "চাপের ঘটনার পর শান্ত হতে বা সামলাতে কষ্ট হওয়া।" },
  str_headaches: { Hindi: "तनाव का सिरदर्द, शरीर दर्द या पेट की तकलीफ के रूप में दिखना।", Bengali: "চাপের কারণে মাথাব্যথা, শরীর ব্যথা বা পেটের সমস্যা হওয়া।" },
  sleep_quality: { Hindi: "नींद आने, नींद बनाए रखने या बहुत जल्दी जागने में कठिनाई।", Bengali: "ঘুম আসা, ঘুম ধরে রাখা বা খুব তাড়াতাড়ি জেগে ওঠার সমস্যা।" },
  sleep_daytime: { Hindi: "खराब नींद के कारण दिन में थकान या नींद आना।", Bengali: "খারাপ ঘুমের কারণে দিনে ক্লান্তি বা ঘুম ঘুম ভাব হওয়া।" },
  sleep_routine: { Hindi: "अनियमित नींद का समय जिसे नियंत्रित करना मुश्किल हो।", Bengali: "অনিয়মিত ঘুমের সময়সূচি যা নিয়ন্ত্রণ করা কঠিন।" },
  sleep_refresh: { Hindi: "काफी समय बिस्तर पर रहने के बाद भी तरोताजा महसूस न होना।", Bengali: "যথেষ্ট সময় ঘুমিয়েও সতেজ না লাগা।" },
  sleep_worry: { Hindi: "नींद को लेकर इतनी चिंता होना कि आराम और मुश्किल हो जाए।", Bengali: "ঘুম নিয়ে এত দুশ্চিন্তা হওয়া যে বিশ্রাম আরও কঠিন হয়ে যায়।" },
  sleep_interrupt: { Hindi: "सपनों, चिंता, दर्द या बेचैनी से बार-बार नींद टूटना।", Bengali: "স্বপ্ন, দুশ্চিন্তা, ব্যথা বা অস্থিরতায় বারবার ঘুম ভাঙা।" },
  burnout_exhaustion: { Hindi: "जिम्मेदारियों के कारण भावनात्मक या शारीरिक थकान महसूस करना।", Bengali: "দায়িত্বের কারণে মানসিক বা শারীরিক ক্লান্তি অনুভব করা।" },
  burnout_detachment: { Hindi: "जिम्मेदारियों से अलगाव, सुन्नपन या प्रेरणा कम लगना।", Bengali: "দায়িত্ব থেকে বিচ্ছিন্ন, নিস্তেজ বা অনুপ্রেরণাহীন লাগা।" },
  burnout_capacity: { Hindi: "सामान्य जिम्मेदारियों को निभा पाने में असमर्थ महसूस करना।", Bengali: "সাধারণ দায়িত্ব সামলাতে না পারার মতো অনুভব করা।" },
  burnout_cynical: { Hindi: "काम या देखभाल की भूमिका के प्रति चिड़चिड़ापन, निराशा या दूरी महसूस करना।", Bengali: "কাজ বা যত্নের ভূমিকার প্রতি বিরক্তি, হতাশা বা দূরত্ব অনুভব করা।" },
  burnout_reward: { Hindi: "लगना कि मेहनत ज़्यादा है लेकिन सराहना, लाभ या समर्थन कम है।", Bengali: "মনে হওয়া যে পরিশ্রম বেশি কিন্তু মূল্যায়ন, ফল বা সহায়তা কম।" },
  burnout_recovery: { Hindi: "आराम के बाद भी पूरी तरह ठीक या तरोताजा महसूस न होना।", Bengali: "বিশ্রামের পরও পুরোপুরি সুস্থ বা সতেজ না লাগা।" },
  lonely_isolated: { Hindi: "लोगों के पास होने पर भी अकेला या अलग-थलग महसूस करना।", Bengali: "মানুষ কাছে থাকলেও একা বা বিচ্ছিন্ন লাগা।" },
  lonely_support: { Hindi: "भावनात्मक समर्थन की कमी महसूस होना।", Bengali: "মানসিক সহায়তার অভাব অনুভব করা।" },
  lonely_connection: { Hindi: "आसपास के लोगों से जुड़ाव महसूस करना कठिन होना।", Bengali: "চারপাশের মানুষের সাথে সংযোগ অনুভব করতে কষ্ট হওয়া।" },
  lonely_belong: { Hindi: "परिवार, काम या समुदाय में अपनेपन की कमी महसूस होना।", Bengali: "পরিবার, কাজ বা সমাজে নিজের জায়গা না পাওয়ার অনুভূতি।" },
  lonely_share: { Hindi: "ऐसे लोगों की कमी जिनसे खुलकर चिंता या भावनाएँ बाँट सकें।", Bengali: "খোলামেলা ভাবে দুশ্চিন্তা বা অনুভূতি ভাগ করার মতো মানুষ কম থাকা।" },
  lonely_withdraw: { Hindi: "बातचीत, मेल-मिलाप या रिश्तों से पहले से ज़्यादा दूर होना।", Bengali: "আলোচনা, মেলামেশা বা সম্পর্ক থেকে আগের চেয়ে বেশি সরে যাওয়া।" },
  substance_frequency: { Hindi: "तनाव या भावनाओं से निपटने के लिए शराब, तंबाकू या अन्य पदार्थों का उपयोग करना।", Bengali: "চাপ বা আবেগ সামলাতে মদ, তামাক বা অন্য পদার্থ ব্যবহার করা।" },
  substance_control: { Hindi: "पदार्थ उपयोग कम या नियंत्रित करना कठिन लगना।", Bengali: "পদার্থের ব্যবহার কমানো বা নিয়ন্ত্রণ করা কঠিন লাগা।" },
  substance_impact: { Hindi: "पदार्थ उपयोग का स्वास्थ्य, संबंधों या जिम्मेदारियों पर असर पड़ना।", Bengali: "পদার্থ ব্যবহারের কারণে স্বাস্থ্য, সম্পর্ক বা দায়িত্ব ক্ষতিগ্রস্ত হওয়া।" },
  substance_craving: { Hindi: "तेज़ इच्छा या लालसा जिसे रोकना कठिन हो।", Bengali: "তীব্র চাহিদা বা ক্রেভিং যা নিয়ন্ত্রণ করা কঠিন।" },
  substance_tolerance: { Hindi: "पहले जैसा असर पाने के लिए पहले से अधिक मात्रा की जरूरत होना।", Bengali: "আগের মতো প্রভাব পেতে আগের চেয়ে বেশি পরিমাণ দরকার হওয়া।" },
  substance_withdrawal: { Hindi: "उपयोग कम करने पर बेचैनी, चिड़चिड़ापन या अस्वस्थता महसूस होना।", Bengali: "ব্যবহার কমালে অস্বস্তি, খিটখিটে ভাব বা অস্থিরতা অনুভব করা।" },
};

const SECTION_TRANSLATIONS = {
  Depression: { Hindi: "डिप्रेशन", Bengali: "বিষণ্নতা" },
  Anxiety: { Hindi: "एंग्जायटी", Bengali: "উদ্বেগ" },
  Stress: { Hindi: "स्ट्रेस", Bengali: "স্ট্রেস" },
  "Sleep Disorder": { Hindi: "नींद संबंधी समस्या", Bengali: "ঘুমের সমস্যা" },
  Burnout: { Hindi: "बर्नआउट", Bengali: "বার্নআউট" },
  Loneliness: { Hindi: "अकेलापन", Bengali: "একাকীত্ব" },
  "Substance Abuse": { Hindi: "पदार्थ दुरुपयोग", Bengali: "পদার্থের অপব্যবহার" },
};

const NEGATIVE_WORDS = new Set(["sad", "hopeless", "worried", "anxious", "tired", "nervous", "stressed", "lonely", "empty", "afraid", "panic", "overwhelmed", "helpless", "worthless"]);
const POSITIVE_WORDS = new Set(["better", "hopeful", "calm", "good", "safe", "supported", "strong", "improving"]);
const SELF_HARM_KEYWORDS = [
  "kill myself",
  "end my life",
  "do not want to live",
  "don't want to live",
  "suicide",
  "self harm",
  "harm myself",
  "hurt myself",
  "want to die",
  "better off dead",
  "life is not worth living",
];
const EMOTION_KEYWORDS = {
  sadness: ["sad", "down", "empty", "hopeless", "crying", "unhappy"],
  fear: ["afraid", "fear", "panic", "scared", "nervous", "terrified"],
  anger: ["angry", "irritated", "frustrated", "annoyed", "furious"],
  joy: ["happy", "relieved", "calm", "hopeful", "better", "good"],
  loneliness: ["alone", "isolated", "lonely", "disconnected", "abandoned"],
  exhaustion: ["tired", "drained", "burned", "burnout", "exhausted", "sleepy"],
};

const state = {
  allResults: [],
  filteredResults: [],
  selectedRecord: null,
  currentPage: 1,
  latestCreatedRecord: null,
  adaptiveResponses: {},
  adaptiveSelectedAnswer: "",
  adaptiveCurrentQuestion: null,
  adaptiveProgress: null,
  adaptiveCompleted: false,
  adaptiveLastRecord: null,
  adaptiveLoading: false,
  adaptiveRequestId: 0,
  adaptiveSessionStarted: false,
  draftRecord: null,
  draftPreviewLoading: false,
  draftPreviewTimer: null,
  draftPreviewRequestId: 0,
  draftPreviewAbortController: null,
  draftPreviewSignature: "",
  assessmentSaveInFlight: false,
  recordedAudioFile: null,
  capturedImageFile: null,
  mediaRecorder: null,
  mediaChunks: [],
  webcamStream: null,
  networkOnline: navigator.onLine,
  pendingSyncCount: 0,
  serviceWorkerReady: false,
};

const elements = {
  tabButtons: [...document.querySelectorAll(".tab-btn")],
  viewSections: [...document.querySelectorAll(".view-section")],
  dashboardLanguage: document.getElementById("dashboardLanguage"),
  offlineStatus: document.getElementById("offlineStatus"),
  applyLanguageBtn: document.getElementById("applyLanguageBtn"),
  questionnaireContainer: document.getElementById("questionnaireContainer"),
  assessmentForm: document.getElementById("assessmentForm"),
  adaptiveForm: document.getElementById("adaptiveForm"),
  saveAssessmentBtn: document.getElementById("saveAssessmentBtn"),
  resetAssessmentBtn: document.getElementById("resetAssessmentBtn"),
  adaptiveStartBtn: document.getElementById("adaptiveStartBtn"),
  adaptiveNextBtn: document.getElementById("adaptiveNextBtn"),
  adaptiveResetBtn: document.getElementById("adaptiveResetBtn"),
  adaptiveStatus: document.getElementById("adaptiveStatus"),
  adaptiveQuestionPrompt: document.getElementById("adaptiveQuestionPrompt"),
  adaptiveQuestionMeta: document.getElementById("adaptiveQuestionMeta"),
  adaptiveAnswerOptions: document.getElementById("adaptiveAnswerOptions"),
  adaptiveAnswerHint: document.getElementById("adaptiveAnswerHint"),
  adaptiveFullName: document.getElementById("adaptiveFullName"),
  adaptiveAge: document.getElementById("adaptiveAge"),
  adaptiveGender: document.getElementById("adaptiveGender"),
  adaptiveVillage: document.getElementById("adaptiveVillage"),
  adaptiveAssessor: document.getElementById("adaptiveAssessor"),
  adaptiveLanguage: document.getElementById("adaptiveLanguage"),
  adaptiveConsent: document.getElementById("adaptiveConsent"),
  adaptiveTextNarrative: document.getElementById("adaptiveTextNarrative"),
  workspaceStatus: document.getElementById("workspaceStatus"),
  workspacePrediction: document.getElementById("workspacePrediction"),
  workspaceNlp: document.getElementById("workspaceNlp"),
  workspaceReadiness: document.getElementById("workspaceReadiness"),
  fullName: document.getElementById("fullName"),
  age: document.getElementById("age"),
  gender: document.getElementById("gender"),
  village: document.getElementById("village"),
  phone: document.getElementById("phone"),
  assessor: document.getElementById("assessor"),
  language: document.getElementById("language"),
  consent: document.getElementById("consent"),
  textNarrative: document.getElementById("textNarrative"),
  startRecordingBtn: document.getElementById("startRecordingBtn"),
  stopRecordingBtn: document.getElementById("stopRecordingBtn"),
  clearRecordingBtn: document.getElementById("clearRecordingBtn"),
  recordingStatus: document.getElementById("recordingStatus"),
  audioFile: document.getElementById("audioFile"),
  startCameraBtn: document.getElementById("startCameraBtn"),
  capturePhotoBtn: document.getElementById("capturePhotoBtn"),
  stopCameraBtn: document.getElementById("stopCameraBtn"),
  clearCapturedPhotoBtn: document.getElementById("clearCapturedPhotoBtn"),
  cameraPreview: document.getElementById("cameraPreview"),
  capturedPhotoPreview: document.getElementById("capturedPhotoPreview"),
  captureCanvas: document.getElementById("captureCanvas"),
  cameraStatus: document.getElementById("cameraStatus"),
  imageFile: document.getElementById("imageFile"),
  analysisStatusBanner: document.getElementById("analysisStatusBanner"),
  statusBanner: document.getElementById("statusBanner"),
  analysisAssessmentId: document.getElementById("analysisAssessmentId"),
  analysisConfidence: document.getElementById("analysisConfidence"),
  analysisStrongestDomain: document.getElementById("analysisStrongestDomain"),
  analysisCoverage: document.getElementById("analysisCoverage"),
  analysisSubmissionTime: document.getElementById("analysisSubmissionTime"),
  analysisTrajectory: document.getElementById("analysisTrajectory"),
  analysisOverallRisk: document.getElementById("analysisOverallRisk"),
  riskDistribution: document.getElementById("riskDistribution"),
  submissionTrend: document.getElementById("submissionTrend"),
  riskHotspots: document.getElementById("riskHotspots"),
  nlpTrends: document.getElementById("nlpTrends"),
  trajectoryModel: document.getElementById("trajectoryModel"),
  trajectorySummary: document.getElementById("trajectorySummary"),
  villageSummary: document.getElementById("villageSummary"),
  assessorSummary: document.getElementById("assessorSummary"),
  recordLookup: document.getElementById("recordLookup"),
  fetchRecordBtn: document.getElementById("fetchRecordBtn"),
  downloadSelectedPdfBtn: document.getElementById("downloadSelectedPdfBtn"),
  resultsTableBody: document.getElementById("resultsTableBody"),
  prevPageBtn: document.getElementById("prevPageBtn"),
  nextPageBtn: document.getElementById("nextPageBtn"),
  pageStatus: document.getElementById("pageStatus"),
  selectedAssessment: document.getElementById("selectedAssessment"),
  scoreComparison: document.getElementById("scoreComparison"),
  modalityBreakdown: document.getElementById("modalityBreakdown"),
  featureSnapshot: document.getElementById("featureSnapshot"),
  patientHistory: document.getElementById("patientHistory"),
  domainTrajectory: document.getElementById("domainTrajectory"),
};

function openOfflineDb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(OFFLINE_DB_NAME, OFFLINE_DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(OFFLINE_RECORDS_STORE)) {
        db.createObjectStore(OFFLINE_RECORDS_STORE, { keyPath: "assessment_id" });
      }
      if (!db.objectStoreNames.contains(OFFLINE_PENDING_STORE)) {
        db.createObjectStore(OFFLINE_PENDING_STORE, { keyPath: "client_queue_id" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function offlineStorePut(storeName, value) {
  const db = await openOfflineDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, "readwrite");
    tx.objectStore(storeName).put(value);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function offlineStoreDelete(storeName, key) {
  const db = await openOfflineDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, "readwrite");
    tx.objectStore(storeName).delete(key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function offlineStoreGetAll(storeName) {
  const db = await openOfflineDb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, "readonly");
    const request = tx.objectStore(storeName).getAll();
    request.onsuccess = () => resolve(request.result || []);
    request.onerror = () => reject(request.error);
  });
}

function makeOfflineAssessmentId() {
  return `MHS-LOCAL-${Math.random().toString(16).slice(2, 8).toUpperCase()}`;
}

function uniqueRecords(records) {
  const seen = new Map();
  safeRecords(records).forEach((record) => {
    const normalized = normalizeRecord(record);
    seen.set(normalized.assessment_id, normalized);
  });
  return [...seen.values()].sort((left, right) => new Date(right.created_at) - new Date(left.created_at));
}

function updateOfflineStatus() {
  if (!elements.offlineStatus) return;
  const online = state.networkOnline;
  const pending = Number(state.pendingSyncCount || 0);
  let label = online ? t("onlineSyncReadyLabel") : t("offlineModeActiveLabel");
  let className = online ? "offline-pill online" : "offline-pill offline";
  if (online && pending > 0) {
    label = `Sync pending: ${pending} assessment${pending === 1 ? "" : "s"}`;
    className = "offline-pill syncing";
  } else if (!online && pending > 0) {
    label = t("offlineModeQueuedLabel", { count: pending });
    className = "offline-pill offline";
  }
  elements.offlineStatus.className = className;
  elements.offlineStatus.textContent = label;
}

async function refreshPendingSyncCount() {
  try {
    state.pendingSyncCount = (await offlineStoreGetAll(OFFLINE_PENDING_STORE)).length;
  } catch (error) {
    console.error("Could not refresh pending sync count", error);
    state.pendingSyncCount = 0;
  }
  updateOfflineStatus();
}

function safeRecords(payload) {
  return Array.isArray(payload) ? payload : [];
}

function emptyScores() {
  return Object.fromEntries(DOMAINS.map((domain) => [domain, 0]));
}

function emptyRisks() {
  return Object.fromEntries(DOMAINS.map((domain) => [domain, "unknown"]));
}

function isDemoRecord(record) {
  const assessmentId = String(record?.assessment_id || "").toUpperCase();
  return assessmentId.startsWith("MHS-DEMO") || record?.record_origin === "demo";
}

function visibleUserRecords(records) {
  return safeRecords(records).filter((record) => {
    if (isDemoRecord(record)) return false;
    return String(record?.record_origin || "").toLowerCase() === "test";
  });
}

function normalizeRecord(record) {
  const safeRecord = record || {};
  const questionnaire = safeRecord.questionnaire || {};
  const overall = safeRecord.multimodal?.overall || {};
  const scores = overall.scores || {};
  const explicitOrigin = String(safeRecord.record_origin || safeRecord.profile?.record_origin || "").toLowerCase();
  const inferredOrigin = explicitOrigin || (String(safeRecord.assessment_id || "").toUpperCase().startsWith("MHS-DEMO") ? "demo" : "");
  const normalizedQuestionnaire = {
    available: questionnaire.available ?? true,
    overall_score: Number(questionnaire.overall_score || 0),
    notes: questionnaire.notes || t("noQuestionnaireNotesLabel"),
  };
  DOMAINS.forEach((domain) => {
    normalizedQuestionnaire[`${domain}_score`] = Number(questionnaire[`${domain}_score`] || 0);
    normalizedQuestionnaire[`${domain}_risk`] = questionnaire[`${domain}_risk`] || riskLevel(normalizedQuestionnaire[`${domain}_score`]);
  });

  const normalizedOverall = {
    ...emptyRisks(),
    confidence: Number(overall.confidence || 0),
    scores: { ...emptyScores() },
  };
  DOMAINS.forEach((domain) => {
    normalizedOverall[domain] = overall[domain] || riskLevel(Number(scores[domain] || 0));
    normalizedOverall.scores[domain] = Number(scores[domain] || 0);
  });

  const normalizeModality = (payload, modality) => {
    const safePayload = payload || {};
    const result = {
      available: Boolean(safePayload.available),
      modality,
      confidence: Number(safePayload.confidence || 0),
      notes: safePayload.notes || "No notes available.",
      features: safePayload.features || {},
    };
    DOMAINS.forEach((domain) => {
      result[`${domain}_score`] = Number(safePayload[`${domain}_score`] || 0);
    });
    return result;
  };

  return {
    assessment_id: safeRecord.assessment_id || `MHS-${Math.random().toString(16).slice(2, 10).toUpperCase()}`,
    created_at: safeRecord.created_at || new Date().toISOString(),
    sync_status: safeRecord.sync_status || "synced",
    patient_key: safeRecord.patient_key || "",
    record_origin: inferredOrigin || (String(safeRecord.sync_status || "").toLowerCase() === "pending" ? "test" : "backend"),
    profile: {
      full_name: safeRecord.profile?.full_name || "",
      age: Number(safeRecord.profile?.age || 0),
      gender: safeRecord.profile?.gender || "Prefer not to say",
      village: safeRecord.profile?.village || "",
      phone: safeRecord.profile?.phone || "",
      assessor: safeRecord.profile?.assessor || "",
      language: normalizeLanguage(safeRecord.profile?.language || "English"),
      record_origin: safeRecord.profile?.record_origin || inferredOrigin || (String(safeRecord.sync_status || "").toLowerCase() === "pending" ? "test" : "backend"),
    },
    questionnaire: normalizedQuestionnaire,
    multimodal: {
      text: normalizeModality(safeRecord.multimodal?.text, "text"),
      audio: normalizeModality(safeRecord.multimodal?.audio, "audio"),
      image: normalizeModality(safeRecord.multimodal?.image, "image"),
      overall: normalizedOverall,
      model_stats: safeRecord.multimodal?.model_stats || {},
      recommendation: safeRecord.multimodal?.recommendation || "No recommendation available.",
      disclaimer: safeRecord.multimodal?.disclaimer || "No disclaimer available.",
    },
    trajectory: safeRecord.trajectory || null,
  };
}

function normalizeText(value) {
  return String(value || "").trim().toLowerCase();
}

function normalizeLanguage(value) {
  const language = normalizeText(value);
  if (language === "hindi" || language === "hi" || language === "हिंदी") {
    return "Hindi";
  }
  if (language === "bengali" || language === "bangla" || language === "bn" || language === "বাংলা" || language === "বাঙলা") {
    return "Bengali";
  }
  return "English";
}

function currentLanguage() {
  return normalizeLanguage(elements.dashboardLanguage?.value || elements.language?.value || "English");
}

function t(key) {
  const language = currentLanguage();
  return UI_TRANSLATIONS[language]?.[key] || UI_TRANSLATIONS.English[key] || key;
}

function tf(key, replacements = {}) {
  let value = t(key);
  Object.entries(replacements).forEach(([name, replacement]) => {
    value = value.replace(`{${name}}`, replacement);
  });
  return value;
}

function questionPrompt(question, language = currentLanguage()) {
  if (question?.language === language && question.prompt_localized) {
    return question.prompt_localized;
  }
  return QUESTION_TRANSLATIONS[question.id]?.[language]
    || question.prompt_en
    || question.prompt;
}

function questionSectionLabel(section) {
  return SECTION_TRANSLATIONS[section]?.[currentLanguage()] || section;
}

function currentAdaptiveLanguage() {
  return normalizeLanguage(elements.adaptiveLanguage?.value || elements.language?.value || currentLanguage());
}

function adaptiveLanguageCopy(english, hindi, bengali) {
  const language = currentAdaptiveLanguage();
  if (language === "Hindi") return hindi;
  if (language === "Bengali") return bengali;
  return english;
}

function adaptiveText(key, replacements = {}, language = currentAdaptiveLanguage()) {
  const template = ADAPTIVE_UI_TRANSLATIONS[language]?.[key]
    || ADAPTIVE_UI_TRANSLATIONS.English[key]
    || "";
  return template.replace(/\{(\w+)\}/g, (_, token) => {
    const replacement = replacements[token];
    return replacement === undefined || replacement === null ? `{${token}}` : String(replacement);
  });
}

function adaptiveChooseOneLabel(progress = state.adaptiveProgress, language = currentAdaptiveLanguage()) {
  if (progress?.language === language && progress?.choose_one_label) {
    return progress.choose_one_label;
  }
  return adaptiveText("chooseOne", {}, language)
    || ADAPTIVE_CHOOSE_ONE_TRANSLATIONS[language]
    || ADAPTIVE_CHOOSE_ONE_TRANSLATIONS.English;
}

function adaptiveSectionLabel(section, language = currentAdaptiveLanguage()) {
  return SECTION_TRANSLATIONS[section]?.[language] || section;
}

function adaptiveResponseOptions(progress = state.adaptiveProgress, language = currentAdaptiveLanguage()) {
  if (progress?.language === language && Array.isArray(progress.response_options) && progress.response_options.length) {
    return progress.response_options.map((option) => ({
      label: String(option.label ?? ""),
      value: String(option.value ?? ""),
    }));
  }
  const labels = RESPONSE_OPTION_TRANSLATIONS[language] || RESPONSE_OPTION_TRANSLATIONS.English;
  return RESPONSE_OPTIONS.map((option, index) => ({
    label: labels[index] || option.label,
    value: String(option.value),
  }));
}

function setNodeText(selector, text) {
  const node = document.querySelector(selector);
  if (node) node.textContent = text;
}

function setLabelText(inputElement, text) {
  const label = inputElement?.closest("label");
  if (!label) return;
  const firstNode = [...label.childNodes].find((node) => node.nodeType === Node.TEXT_NODE);
  if (firstNode) {
    firstNode.textContent = `${text} `;
  }
}

function setCheckboxLabel(inputElement, text) {
  const label = inputElement?.closest("label");
  if (!label) return;
  const textNodes = [...label.childNodes].filter((node) => node.nodeType === Node.TEXT_NODE);
  if (textNodes.length) {
    textNodes[textNodes.length - 1].textContent = ` ${text}`;
    return;
  }
  label.append(` ${text}`);
}

function setSelectOptionLabels(selectElement, labels) {
  if (!selectElement?.options) return;
  [...selectElement.options].forEach((option, index) => {
    if (labels[index] !== undefined) {
      option.textContent = labels[index];
    }
  });
}

function applyLanguage() {
  document.documentElement.lang = currentLanguage() === "Hindi" ? "hi" : currentLanguage() === "Bengali" ? "bn" : "en";
  if (elements.language && elements.language.value !== currentLanguage()) {
    elements.language.value = currentLanguage();
  }
  if (elements.dashboardLanguage && elements.dashboardLanguage.value !== currentLanguage()) {
    elements.dashboardLanguage.value = currentLanguage();
  }
  if (elements.adaptiveLanguage && elements.adaptiveLanguage.value !== currentLanguage()) {
    elements.adaptiveLanguage.value = currentLanguage();
  }
  setNodeText("#heroEyebrow", t("heroEyebrow"));
  setNodeText("#heroTitle", t("heroTitle"));
  setNodeText("#heroText", t("heroText"));
  setNodeText("#heroMetricRisk", t("heroMetricRisk"));
  setNodeText("#heroMetricModalities", t("heroMetricModalities"));
  setNodeText("#heroMetricOffline", t("heroMetricOffline"));
  setNodeText("#dashboardLanguageLabel", t("dashboardLanguageLabel"));
  setNodeText("#applyLanguageBtn", t("applyLanguageBtn"));
  setNodeText("#signalNarrativeLabel", currentLanguage() === "Hindi" ? "वर्णन NLP" : currentLanguage() === "Bengali" ? "বর্ণনা NLP" : "Narrative NLP");
  setNodeText("#signalNarrativeStrong", currentLanguage() === "Hindi" ? "भाव, तनाव, सुरक्षा" : currentLanguage() === "Bengali" ? "সেন্টিমেন্ট, চাপ, নিরাপত্তা" : "Sentiment, stress, safety");
  setNodeText("#signalNarrativeText", currentLanguage() === "Hindi" ? "लाइव टेक्स्ट स्क्रीनिंग संकेत कहानी लिखते समय अपडेट होते हैं।" : currentLanguage() === "Bengali" ? "গল্পটি লিখতে লিখতে লাইভ টেক্সট স্ক্রিনিং সংকেত আপডেট হয়।" : "Live text screening signals update while the story is being entered.");
  setNodeText("#signalSpeechLabel", currentLanguage() === "Hindi" ? "भाषण संकेत" : currentLanguage() === "Bengali" ? "কথন সংকেত" : "Speech cues");
  setNodeText("#signalSpeechStrong", currentLanguage() === "Hindi" ? "आवाज़ की ऊर्जा और गति" : currentLanguage() === "Bengali" ? "কণ্ঠের শক্তি ও গতি" : "Voice energy and pacing");
  setNodeText("#signalSpeechText", currentLanguage() === "Hindi" ? "जब नमूना उपलब्ध हो, ऑडियो मार्कर कॉन्फिडेंस बैंड को मजबूत करते हैं।" : currentLanguage() === "Bengali" ? "নমুনা থাকলে অডিও মার্কার কনফিডেন্স ব্যান্ডকে শক্তিশালী করে।" : "Audio markers strengthen the confidence band when a sample is present.");
  setNodeText("#signalFaceLabel", currentLanguage() === "Hindi" ? "चेहरे का स्नैपशॉट" : currentLanguage() === "Bengali" ? "মুখের স্ন্যাপশট" : "Face snapshot");
  setNodeText("#signalFaceStrong", currentLanguage() === "Hindi" ? "अभिव्यक्ति समर्थन" : currentLanguage() === "Bengali" ? "অভিব্যক্তি সহায়তা" : "Expression support");
  setNodeText("#signalFaceText", currentLanguage() === "Hindi" ? "इमेज-आधारित संकेत क्षेत्रकर्मियों के लिए बहु-मोडल चित्र को समृद्ध करते हैं।" : currentLanguage() === "Bengali" ? "ছবিভিত্তিক সংকেত মাঠকর্মীদের জন্য মাল্টিমোডাল চিত্রকে সমৃদ্ধ করে।" : "Image-based cues enrich the multimodal picture for field workers.");
  setNodeText("#signalPulseLabel", currentLanguage() === "Hindi" ? "लाइव जोखिम पल्स" : currentLanguage() === "Bengali" ? "লাইভ ঝুঁকির পালস" : "Live risk pulse");
  setNodeText("#signalPulseStatus", currentLanguage() === "Hindi" ? "अद्यतन" : currentLanguage() === "Bengali" ? "আপডেটেড" : "updated");
  setNodeText("#workspaceTabBtn", t("workspaceTab"));
  setNodeText("#adaptiveTabBtn", t("adaptiveTab"));
  setNodeText("#analyticsTabBtn", t("analyticsTab"));
  setNodeText("#recordsTabBtn", t("recordsTab"));
  const languageOptionLabels = LANGUAGE_OPTION_LABELS[currentLanguage()] || LANGUAGE_OPTION_LABELS.English;
  const genderOptionLabels = GENDER_OPTION_LABELS[currentLanguage()] || GENDER_OPTION_LABELS.English;
  setSelectOptionLabels(elements.dashboardLanguage, [
    languageOptionLabels.English,
    languageOptionLabels.Hindi,
    languageOptionLabels.Bengali,
  ]);
  setSelectOptionLabels(elements.language, [
    languageOptionLabels.English,
    languageOptionLabels.Hindi,
    languageOptionLabels.Bengali,
    languageOptionLabels.Other,
  ]);
  setSelectOptionLabels(elements.adaptiveLanguage, [
    languageOptionLabels.English,
    languageOptionLabels.Hindi,
    languageOptionLabels.Bengali,
    languageOptionLabels.Other,
  ]);
  setSelectOptionLabels(elements.gender, genderOptionLabels);
  setSelectOptionLabels(elements.adaptiveGender, genderOptionLabels);
  const numericLang = currentLanguage() === "Bengali" ? "bn" : currentLanguage() === "Hindi" ? "hi" : "en";
  if (elements.age) elements.age.lang = numericLang;
  if (elements.adaptiveAge) elements.adaptiveAge.lang = numericLang;
  setNodeText(".intake-card-strong h3", t("intakeFlowTitle"));
  setNodeText(".intake-card-strong p:last-child", t("intakeFlowText"));
  setNodeText(".intake-strip .intake-card:nth-child(2) h3", t("step1Title"));
  setNodeText(".intake-strip .intake-card:nth-child(2) p:last-child", t("step1Text"));
  setNodeText(".intake-strip .intake-card:nth-child(3) h3", t("step2Title"));
  setNodeText(".intake-strip .intake-card:nth-child(3) p:last-child", t("step2Text"));
  setNodeText(".intake-strip .intake-card:nth-child(4) h3", t("step3Title"));
  setNodeText(".intake-strip .intake-card:nth-child(4) p:last-child", t("step3Text"));
  setNodeText(".intake-strip .intake-card:nth-child(5) h3", t("step4Title"));
  setNodeText(".intake-strip .intake-card:nth-child(5) p:last-child", t("step4Text"));
  setNodeText(".form-card h3", t("candidateProfileTitle"));
  setNodeText(".form-grid .form-card:nth-child(2) h3", t("freeTextTitle"));
  setNodeText("#adaptiveSectionTitle", t("adaptiveTitle"));
  setNodeText("#adaptiveSectionText", t("adaptiveSubtitle"));
  setNodeText("#adaptiveIntroFlowTitle", t("adaptiveIntroFlowTitle"));
  setNodeText("#adaptiveIntroFlowHeading", t("adaptiveIntroFlowHeading"));
  setNodeText("#adaptiveIntroFlowText", t("adaptiveIntroFlowText"));
  setNodeText("#adaptiveIntroLanguageTitle", t("adaptiveIntroLanguageTitle"));
  setNodeText("#adaptiveIntroLanguageHeading", t("adaptiveIntroLanguageHeading"));
  setNodeText("#adaptiveIntroLanguageText", t("adaptiveIntroLanguageText"));
  setNodeText("#adaptiveIntroSharedTitle", t("adaptiveIntroSharedTitle"));
  setNodeText("#adaptiveIntroSharedHeading", t("adaptiveIntroSharedHeading"));
  setNodeText("#adaptiveIntroSharedText", t("adaptiveIntroSharedText"));
  setNodeText("#adaptiveProfileTitle", t("adaptiveProfileTitle"));
  setNodeText("#adaptiveQuestionTitle", t("adaptiveQuestionTitle"));
  setNodeText("#adaptiveNarrativeTitle", t("adaptiveNarrativeTitle"));
  setNodeText("#adaptiveNarrativeText", adaptiveText("narrativeSubtitle"));
  setNodeText("#adaptiveQuestionPrompt", t("adaptiveQuestionHint"));
  setNodeText("#adaptiveQuestionMeta", adaptiveText("idleMeta"));
  setNodeText("#adaptiveAnswerLabel", adaptiveText("answerLabel"));
  setNodeText("#adaptiveAnswerHint", adaptiveText("answerHelp"));
  setNodeText("#adaptiveStartBtn", t("adaptiveStartBtn"));
  setNodeText("#adaptiveNextBtn", t("adaptiveNextBtn"));
  setNodeText("#adaptiveResetBtn", t("adaptiveResetBtn"));
  setLabelText(elements.fullName, t("fullNameLabel"));
  setLabelText(elements.age, t("ageLabel"));
  setLabelText(elements.gender, t("genderLabel"));
  setLabelText(elements.village, t("villageLabel"));
  setLabelText(elements.phone, t("phoneLabel"));
  setLabelText(elements.assessor, t("assessorLabel"));
  setLabelText(elements.language, t("languageLabel"));
  setLabelText(elements.adaptiveLanguage, t("languageLabel"));
  setCheckboxLabel(elements.consent, t("consentLabel"));
  setLabelText(elements.adaptiveFullName, t("fullNameLabel"));
  setLabelText(elements.adaptiveAge, t("ageLabel"));
  setLabelText(elements.adaptiveGender, t("genderLabel"));
  setLabelText(elements.adaptiveVillage, t("villageLabel"));
  setLabelText(elements.adaptiveAssessor, t("assessorLabel"));
  setCheckboxLabel(elements.adaptiveConsent, t("consentLabel"));
  setLabelText(elements.textNarrative, t("narrativeLabel"));
  setLabelText(elements.adaptiveTextNarrative, t("narrativeLabel"));
  elements.fullName.placeholder = t("fullNamePlaceholder");
  elements.village.placeholder = t("villagePlaceholder");
  elements.assessor.placeholder = t("assessorPlaceholder");
  elements.adaptiveFullName.placeholder = t("fullNamePlaceholder");
  elements.adaptiveVillage.placeholder = t("villagePlaceholder");
  elements.adaptiveAssessor.placeholder = t("assessorPlaceholder");
  elements.textNarrative.placeholder = t("narrativePlaceholder");
  elements.adaptiveTextNarrative.placeholder = t("narrativePlaceholder");
  setNodeText(".form-grid .form-card:nth-child(2) .capture-card:nth-of-type(1) .capture-head strong", t("guidedSpeechTitle"));
  setNodeText(".form-grid .form-card:nth-child(2) .capture-card:nth-of-type(1) .capture-head .capture-topic", t("guidedSpeechTopic"));
  setLabelText(elements.audioFile, t("audioFileLabel"));
  setNodeText(".form-grid .form-card:nth-child(2) .capture-card:nth-of-type(2) .capture-head strong", t("liveFaceTitle"));
  setNodeText(".form-grid .form-card:nth-child(2) .capture-card:nth-of-type(2) .capture-head .capture-topic", t("liveFaceTopic"));
  setLabelText(elements.imageFile, t("imageFileLabel"));
  setNodeText("#questionnaireTitle", t("questionnaireTitle"));
  setNodeText("#questionnaireSubtitle", t("questionnaireSubtitle"));
  setNodeText("#saveAssessmentBtn", t("saveAssessmentBtn"));
  setNodeText("#resetAssessmentBtn", t("resetAssessmentBtn"));
  setNodeText("#workspaceTitle", t("workspaceTab"));
  setNodeText("#workspaceText", currentLanguage() === "Hindi" ? "डैशबोर्ड से सीधे नया स्क्रीनिंग रिकॉर्ड बनाएं।" : currentLanguage() === "Bengali" ? "ড্যাশবোর্ড থেকেই নতুন স্ক্রিনিং রেকর্ড তৈরি করুন।" : "Create a new screening record directly from the dashboard.");
  setNodeText("#workspacePredictionTitle", t("workspacePredictionTitle"));
  setNodeText("#workspacePredictionText", t("workspacePredictionText"));
  setNodeText("#workspaceNlpTitle", t("workspaceNlpTitle"));
  setNodeText("#workspaceNlpText", t("workspaceNlpText"));
  setNodeText("#workspaceReadinessTitle", t("workspaceReadinessTitle"));
  setNodeText("#workspaceReadinessText", t("workspaceReadinessText"));
  setNodeText("#analyticsTitle", t("analyticsTab"));
  setNodeText("#analyticsText", t("detailAnalysisTitle"));
  setNodeText("#recordsSectionTitle", t("recordsTab"));
  setNodeText("#recordsSectionText", t("recordsHeadingText"));
  setNodeText("#fetchRecordBtn", t("fetchRecordBtn"));
  setNodeText("#downloadSelectedPdfBtn", t("downloadPdfBtn"));
  elements.recordLookup.placeholder = t("recordLookupPlaceholder");
  setNodeText("#analysisAssessmentIdLabel", t("assessmentIdLabel"));
  setNodeText("#analysisConfidenceLabel", t("overallConfidenceLabel"));
  setNodeText("#analysisOverallRiskLabel", t("overallRiskLabel"));
  setNodeText("#recordsTableAssessmentIdHeader", t("assessmentIdLabel"));
  setNodeText("#recordsTableNameHeader", t("candidateLabel"));
  setNodeText("#recordsTableVillageHeader", t("villageShortLabel"));
  setNodeText("#recordsTableAssessorHeader", t("assessorShortLabel"));
  setNodeText("#recordsTableSubmittedHeader", t("createdAtLabel"));
  setNodeText("#recordsTableRiskHeader", t("riskLabel"));
  setNodeText("#recordsTableConfidenceHeader", t("confidenceLabel"));
  setNodeText("#prevPageBtn", t("previousLabel"));
  setNodeText("#nextPageBtn", t("nextLabel"));
  setNodeText("#analyticsView .analytics-intro .info-card:nth-child(1) h3", t("analyticsIntroCurrent"));
  setNodeText("#analyticsView .analytics-intro .info-card:nth-child(1) p:last-child", t("analyticsIntroCurrentText"));
  setNodeText("#analyticsView .analytics-intro .info-card:nth-child(2) p.intake-kicker", t("analyticsIntroModel"));
  setNodeText("#analyticsView .analytics-intro .info-card:nth-child(2) p:last-child", t("analyticsIntroModelText"));
  setNodeText("#analyticsView .analytics-intro .info-card:nth-child(3) p.intake-kicker", t("analyticsIntroScope"));
  setNodeText("#analyticsView .analytics-intro .info-card:nth-child(3) p:last-child", t("analyticsIntroScopeText"));
  setNodeText("#analyticsView .analytics-grid-primary .panel:nth-child(1) .section-heading h2", t("domainAnalysisTitle"));
  setNodeText("#analyticsView .analytics-grid-primary .panel:nth-child(1) .section-heading p", t("domainAnalysisText"));
  setNodeText("#analyticsView .analytics-grid-primary .panel:nth-child(2) .section-heading h2", t("componentContributionTitle"));
  setNodeText("#analyticsView .analytics-grid-primary .panel:nth-child(2) .section-heading p", t("componentContributionText"));
  setNodeText("#analyticsView .analytics-grid-secondary:nth-of-type(4) .panel:nth-child(1) .section-heading h2", t("modelStatisticsTitle"));
  setNodeText("#analyticsView .analytics-grid-secondary:nth-of-type(4) .panel:nth-child(1) .section-heading p", t("modelStatisticsText"));
  setNodeText("#analyticsView .analytics-grid-secondary:nth-of-type(4) .panel:nth-child(2) .section-heading h2", t("nlpSafetyTitle"));
  setNodeText("#analyticsView .analytics-grid-secondary:nth-of-type(4) .panel:nth-child(2) .section-heading p", t("nlpSafetyText"));
  setNodeText("#analyticsView .analytics-grid-secondary:nth-of-type(5) .panel:nth-child(1) .section-heading h2", t("modalityQualityTitle"));
  setNodeText("#analyticsView .analytics-grid-secondary:nth-of-type(5) .panel:nth-child(1) .section-heading p", t("modalityQualityText"));
  setNodeText("#analyticsView .analytics-grid-secondary:nth-of-type(5) .panel:nth-child(2) .section-heading h2", t("recommendationTitle"));
  setNodeText("#analyticsView .analytics-grid-secondary:nth-of-type(5) .panel:nth-child(2) .section-heading p", t("recommendationText"));
  setNodeText("#recordsExplorerTitle", t("recordsExplorerTitle"));
  setNodeText("#recordsExplorerText", t("recordsExplorerText"));
  setNodeText("#assessmentDetailTitle", t("assessmentDetailTitle"));
  setNodeText("#assessmentDetailText", t("assessmentDetailText"));
  setNodeText("#scoreComparisonTitle", t("scoreComparisonTitle"));
  setNodeText("#scoreComparisonText", t("scoreComparisonText"));
  setNodeText("#modalityBreakdownTitle", t("modalityBreakdownTitle"));
  setNodeText("#modalityBreakdownText", t("modalityBreakdownText"));
  setNodeText("#featureSnapshotTitle", t("featureSnapshotTitle"));
  setNodeText("#featureSnapshotText", t("featureSnapshotText"));
  setNodeText("#patientHistoryTitle", t("patientHistoryTitle"));
  setNodeText("#patientHistoryText", t("patientHistoryText"));
  setNodeText("#domainTrajectoryTitle", t("domainTrajectoryTitle"));
  setNodeText("#domainTrajectoryText", t("domainTrajectoryText"));
  setNodeText("#trajectoryModelTitle", t("trajectoryModelTitle"));
  setNodeText("#trajectoryModelText", t("trajectoryModelText"));
  setNodeText("#trajectorySummaryTitle", t("trajectorySummaryTitle"));
  setNodeText("#trajectorySummaryText", t("trajectorySummaryText"));
}

function applyDashboardLanguageSelection() {
  buildQuestionnaire();
  wireQuestionnaireEvents();
  applyLanguage();
  renderAdaptiveQuestion();
  if (state.adaptiveLoading) {
    renderAdaptiveStatus(t("adaptiveStatusLoading"), "neutral");
  } else if (state.adaptiveCompleted) {
    renderAdaptiveStatus(t("adaptiveStatusComplete"), "success");
  } else {
    renderAdaptiveStatus(t("adaptiveStatusIdle"), "neutral");
  }
  renderWorkspacePanels();
  renderDashboard();
}

function formatPercent(value) {
  return `${Math.round((Number(value) || 0) * 100)}%`;
}

function formatDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Unknown" : date.toLocaleString();
}

function slugify(text) {
  return String(text || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
}

function clamp01(value) {
  return Math.max(0, Math.min(1, Number(value) || 0));
}

function riskLevel(score) {
  if (score < 0.33) return "low";
  if (score < 0.66) return "moderate";
  return "high";
}

function average(values) {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function setActiveResults(records, { focusLatest = false, bannerMessage = "", bannerTone = "success" } = {}) {
  state.allResults = visibleUserRecords(records)
    .map(normalizeRecord)
    .sort((left, right) => new Date(right.created_at) - new Date(left.created_at));
  state.filteredResults = [...state.allResults];
  state.currentPage = 1;
  state.selectedRecord = state.allResults[0] || null;
  applyFilters();
  if (focusLatest && state.allResults[0]) {
    state.latestCreatedRecord = state.allResults[0];
    renderWorkspacePanels();
  }
  if (bannerMessage) {
    setBanner(elements.statusBanner, bannerMessage, bannerTone);
  }
}

function setBanner(element, message, tone = "neutral") {
  if (!element) return;
  element.textContent = message;
  if (tone === "error") {
    element.style.background = "rgba(179, 71, 61, 0.09)";
    element.style.borderColor = "rgba(179, 71, 61, 0.3)";
  } else if (tone === "success") {
    element.style.background = "rgba(80, 121, 61, 0.1)";
    element.style.borderColor = "rgba(80, 121, 61, 0.3)";
  } else {
    element.style.background = "rgba(40, 121, 112, 0.08)";
    element.style.borderColor = "rgba(40, 121, 112, 0.28)";
  }
}

function setAssessmentActionState(isBusy) {
  state.assessmentSaveInFlight = Boolean(isBusy);
  if (elements.saveAssessmentBtn) {
    elements.saveAssessmentBtn.disabled = state.assessmentSaveInFlight;
    elements.saveAssessmentBtn.textContent = state.assessmentSaveInFlight
      ? (currentLanguage() === "Bengali" ? "সংরক্ষণ করা হচ্ছে..." : currentLanguage() === "Hindi" ? "सहेजा जा रहा है..." : "Saving...")
      : t("saveAssessmentBtn");
  }
  if (elements.resetAssessmentBtn) {
    elements.resetAssessmentBtn.disabled = state.assessmentSaveInFlight;
  }
}

function cancelDraftPreview() {
  if (state.draftPreviewTimer) {
    clearTimeout(state.draftPreviewTimer);
    state.draftPreviewTimer = null;
  }
  if (state.draftPreviewAbortController) {
    state.draftPreviewAbortController.abort();
    state.draftPreviewAbortController = null;
  }
  state.draftPreviewLoading = false;
}

function previewSignature(payload) {
  return JSON.stringify({
    profile: {
      full_name: payload.profile?.full_name || "",
      village: payload.profile?.village || "",
      assessor: payload.profile?.assessor || "",
      language: payload.profile?.language || "",
      consent_received: Boolean(payload.profile?.consent_received),
    },
    questionnaire: payload.questionnaire || {},
    text_input: payload.text_input || "",
    audio_metadata: payload.audio_metadata || null,
    image_metadata: payload.image_metadata || null,
  });
}

async function apiJson(url, options = {}, { timeoutMs = 30000 } = {}) {
  const controller = options.signal ? null : new AbortController();
  const signal = options.signal || controller.signal;
  const timeoutId = controller ? setTimeout(() => controller.abort(), timeoutMs) : null;
  try {
    const response = await fetch(url, { cache: "no-store", ...options, signal });
    const contentType = response.headers.get("content-type") || "";
    const body = contentType.includes("application/json")
      ? await response.json().catch(() => ({}))
      : await response.text().catch(() => "");
    if (!response.ok) {
      const error = new Error(typeof body === "object" && body?.error ? body.error : `HTTP ${response.status}`);
      error.status = response.status;
      error.payload = body;
      throw error;
    }
    return body;
  } finally {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  }
}

async function fetchAdaptiveQuestionState(responses, language) {
  return apiJson("/api/adaptive/next", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ responses, language }),
  }, { timeoutMs: 15000 });
}

function modalityReadinessMessage(kind, payload, file) {
  const label = kind === "audio" ? "Audio" : "Image";
  const isPreviewPending = state.draftPreviewLoading && !payload?.features?.upload_received && !payload?.available;
  if (!file) {
    return { ready: true, tone: "neutral", text: `${label}: optional input not provided.` };
  }
  if (isPreviewPending) {
    return {
      ready: true,
      tone: "neutral",
      text: `${label}: uploaded and waiting for backend analysis.`,
    };
  }
  if (payload?.available) {
    if (kind === "audio") {
      return {
        ready: true,
        tone: "success",
        text: `${label}: analyzed successfully from ${payload?.features?.file_name || file.name}.`,
      };
    }
    return {
      ready: true,
      tone: "success",
      text: `${label}: face photo analyzed successfully from ${payload?.features?.file_name || file.name}.`,
    };
  }
  if (payload?.features?.upload_received) {
    const note = payload?.notes || "upload received, but no usable backend inference was produced.";
    return {
      ready: false,
      tone: "error",
      text: `${label}: ${note}`,
    };
  }
  return {
    ready: true,
    tone: "neutral",
    text: `${label}: selected and ready for backend analysis.`,
  };
}

function getCurrentAudioFile() {
  return state.recordedAudioFile || elements.audioFile.files[0] || null;
}

function getCurrentImageFile() {
  return state.capturedImageFile || elements.imageFile.files[0] || null;
}

function updateCaptureUi() {
  const hasRecording = Boolean(state.recordedAudioFile);
  const recorderActive = Boolean(state.mediaRecorder && state.mediaRecorder.state === "recording");
  elements.startRecordingBtn.disabled = recorderActive;
  elements.stopRecordingBtn.disabled = !recorderActive;
  elements.clearRecordingBtn.disabled = !hasRecording && !recorderActive;
  elements.recordingStatus.textContent = hasRecording
    ? `Speech recording ready: ${state.recordedAudioFile.name}`
    : recorderActive
      ? "Recording in progress..."
      : "No speech recording captured yet.";

  const streamActive = Boolean(state.webcamStream);
  const hasPhoto = Boolean(state.capturedImageFile);
  elements.startCameraBtn.disabled = streamActive;
  elements.capturePhotoBtn.disabled = !streamActive;
  elements.stopCameraBtn.disabled = !streamActive;
  elements.clearCapturedPhotoBtn.disabled = !hasPhoto;
  elements.cameraPreview.classList.toggle("is-hidden", !streamActive);
  elements.capturedPhotoPreview.classList.toggle("is-hidden", !hasPhoto);
  elements.cameraStatus.textContent = hasPhoto
    ? `Captured photo ready: ${state.capturedImageFile.name}`
    : streamActive
      ? "Camera is open. Capture a clear front-facing photo."
      : "No live photo captured yet.";
}

function clearUploadedMediaInputs() {
  elements.audioFile.value = "";
  elements.imageFile.value = "";
}

async function startSpeechRecording() {
  if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
    setBanner(elements.workspaceStatus, "This browser does not support live speech recording.", "error");
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
      ? "audio/webm;codecs=opus"
      : MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "";
    state.mediaChunks = [];
    state.mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
    state.mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data && event.data.size > 0) state.mediaChunks.push(event.data);
    });
    state.mediaRecorder.addEventListener("stop", () => {
      const finalMime = state.mediaRecorder?.mimeType || mimeType || "audio/webm";
      const blob = new Blob(state.mediaChunks, { type: finalMime });
      const extension = finalMime.includes("mp4") ? "mp4" : finalMime.includes("ogg") ? "ogg" : "webm";
      state.recordedAudioFile = new File([blob], `guided-speech.${extension}`, { type: finalMime });
      stream.getTracks().forEach((track) => track.stop());
      state.mediaRecorder = null;
      state.mediaChunks = [];
      updateCaptureUi();
      updateDraftPreview();
    });
    state.recordedAudioFile = null;
    elements.audioFile.value = "";
    state.mediaRecorder.start();
    updateCaptureUi();
  } catch (error) {
    console.error("Speech recording failed", error);
    setBanner(elements.workspaceStatus, "Microphone access is required for live speech recording.", "error");
  }
}

function stopSpeechRecording() {
  if (state.mediaRecorder && state.mediaRecorder.state === "recording") {
    state.mediaRecorder.stop();
  }
}

function clearSpeechRecording() {
  if (state.mediaRecorder && state.mediaRecorder.state === "recording") {
    state.mediaRecorder.stop();
  }
  state.recordedAudioFile = null;
  state.mediaChunks = [];
  updateCaptureUi();
  updateDraftPreview();
}

async function startWebcam() {
  if (!navigator.mediaDevices?.getUserMedia) {
    setBanner(elements.workspaceStatus, "This browser does not support webcam capture.", "error");
    return;
  }
  try {
    if (elements.capturedPhotoPreview.src) {
      URL.revokeObjectURL(elements.capturedPhotoPreview.src);
      elements.capturedPhotoPreview.removeAttribute("src");
    }
    state.capturedImageFile = null;
    elements.imageFile.value = "";
    state.webcamStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
    elements.cameraPreview.srcObject = state.webcamStream;
    updateCaptureUi();
  } catch (error) {
    console.error("Webcam access failed", error);
    setBanner(elements.workspaceStatus, "Camera access is required for live face capture.", "error");
  }
}

function stopWebcam() {
  if (state.webcamStream) {
    state.webcamStream.getTracks().forEach((track) => track.stop());
    state.webcamStream = null;
  }
  elements.cameraPreview.srcObject = null;
  updateCaptureUi();
}

function captureWebcamPhoto() {
  if (!state.webcamStream) return;
  const video = elements.cameraPreview;
  const canvas = elements.captureCanvas;
  const width = video.videoWidth || 640;
  const height = video.videoHeight || 480;
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, width, height);
  canvas.toBlob((blob) => {
    if (!blob) return;
    if (elements.capturedPhotoPreview.src) {
      URL.revokeObjectURL(elements.capturedPhotoPreview.src);
    }
    state.capturedImageFile = new File([blob], "captured-face.jpg", { type: "image/jpeg" });
    elements.capturedPhotoPreview.src = URL.createObjectURL(blob);
    stopWebcam();
    updateCaptureUi();
    updateDraftPreview();
  }, "image/jpeg", 0.92);
}

function clearCapturedPhoto() {
  if (elements.capturedPhotoPreview.src) {
    URL.revokeObjectURL(elements.capturedPhotoPreview.src);
  }
  elements.capturedPhotoPreview.removeAttribute("src");
  state.capturedImageFile = null;
  updateCaptureUi();
  updateDraftPreview();
}

function buildQuestionnaire() {
  const responses = collectQuestionnaireResponses();
  let currentSection = "";
  const blocks = [];
  QUESTION_BANK.forEach((question) => {
    if (question.section !== currentSection) {
      if (currentSection) {
        blocks.push("</div></section>");
      }
      currentSection = question.section;
      blocks.push(`<section class="question-group"><h4>${questionSectionLabel(currentSection)}</h4><div class="question-list">`);
    }
    const choiceLabels = RESPONSE_OPTION_TRANSLATIONS[currentLanguage()] || RESPONSE_OPTION_TRANSLATIONS.English;
    const choices = RESPONSE_OPTIONS.map((option, index) => `
      <label class="choice-pill">
        <input type="radio" name="${question.id}" value="${option.value}" ${responses[question.id] === option.value || (!responses[question.id] && option.value === 0) ? "checked" : ""}>
        <span>${choiceLabels[index] || option.label}</span>
      </label>
    `).join("");
    blocks.push(`
      <div class="question-item">
        <p>${questionPrompt(question, currentLanguage())}</p>
        <div class="choice-row">${choices}</div>
      </div>
    `);
  });
  blocks.push("</div></section>");
  elements.questionnaireContainer.innerHTML = blocks.join("");
}

function wireQuestionnaireEvents() {
  QUESTION_BANK.forEach((question) => {
    document.querySelectorAll(`input[name="${question.id}"]`).forEach((radio) => {
      radio.addEventListener("change", updateDraftPreview);
    });
  });
}

function readDashboardRecords() {
  return [...state.allResults];
}

function collectQuestionnaireResponses() {
  const responses = {};
  QUESTION_BANK.forEach((question) => {
    const selected = document.querySelector(`input[name="${question.id}"]:checked`);
    responses[question.id] = Number(selected?.value || 0);
  });
  return responses;
}

function scoreQuestionnaire(responses) {
  const result = { available: true };
  DOMAINS.forEach((domain) => {
    const scores = QUESTION_BANK
      .filter((question) => question.domain === domain)
      .map((question) => (responses[question.id] || 0) / 3);
    const score = average(scores);
    result[`${domain}_score`] = clamp01(score);
    result[`${domain}_risk`] = riskLevel(score);
  });
  result.overall_score = average(DOMAINS.map((domain) => result[`${domain}_score`]));
  result.notes = t("questionnaireNotes");
  return result;
}

function detectEmotionScores(words) {
  const counts = Object.fromEntries(Object.keys(EMOTION_KEYWORDS).map((key) => [key, 0]));
  words.forEach((word) => {
    Object.entries(EMOTION_KEYWORDS).forEach(([emotion, keywords]) => {
      if (keywords.includes(word)) {
        counts[emotion] += 1;
      }
    });
  });
  const total = Object.values(counts).reduce((sum, value) => sum + value, 0) || 1;
  const scores = {};
  Object.entries(counts).forEach(([emotion, count]) => {
    scores[emotion] = count / total;
  });
  return scores;
}

function extractTextNlp(text) {
  const clean = normalizeText(text);
  const words = clean.split(/\s+/).filter(Boolean);
  const negativeWordCount = words.filter((word) => NEGATIVE_WORDS.has(word)).length;
  const positiveWordCount = words.filter((word) => POSITIVE_WORDS.has(word)).length;
  const negativeDensity = negativeWordCount / Math.max(1, words.length);
  const positiveDensity = positiveWordCount / Math.max(1, words.length);
  const sentimentCompound = clamp01(0.5 + positiveDensity - negativeDensity) * 2 - 1;
  const sentimentLabel = sentimentCompound >= 0 ? "positive" : "negative";
  const emotionScores = detectEmotionScores(words);
  const dominantEmotion = Object.entries(emotionScores).sort((a, b) => b[1] - a[1])[0]?.[0] || "neutral";
  const selfHarmMatches = SELF_HARM_KEYWORDS.filter((keyword) => clean.includes(keyword));
  const selfHarmRiskScore = clamp01(selfHarmMatches.length / 2);
  return {
    available: Boolean(clean),
    word_count: words.length,
    negative_word_count: negativeWordCount,
    positive_word_count: positiveWordCount,
    sentiment_compound: sentimentCompound,
    sentiment_label: sentimentLabel,
    sentiment_model: "dashboard-heuristic",
    sentiment_confidence: Math.abs(sentimentCompound),
    dominant_emotion: dominantEmotion,
    emotion_scores: emotionScores,
    emotion_model: "keyword-heuristic",
    self_harm_keyword_detected: selfHarmMatches.length > 0,
    self_harm_keyword_matches: selfHarmMatches,
    self_harm_risk_score: selfHarmRiskScore,
    lexical_diversity: new Set(words).size / Math.max(1, words.length),
    question_ratio: (text.match(/\?/g) || []).length / Math.max(1, words.length),
    exclamation_ratio: (text.match(/!/g) || []).length / Math.max(1, words.length),
    emotion_intensity: Math.abs(sentimentCompound),
    transformer_model: "dashboard-transformer-ready",
  };
}

function scoreDashboardText(textFeatures) {
  if (!textFeatures.available) {
    return { available: false };
  }

  const negativeDensity = textFeatures.negative_word_count / Math.max(1, textFeatures.word_count);
  const positiveDensity = textFeatures.positive_word_count / Math.max(1, textFeatures.word_count);
  const sadness = textFeatures.emotion_scores.sadness || 0;
  const fear = textFeatures.emotion_scores.fear || 0;
  const anger = textFeatures.emotion_scores.anger || 0;
  const lonelinessEmotion = textFeatures.emotion_scores.loneliness || 0;
  const exhaustion = textFeatures.emotion_scores.exhaustion || 0;
  const selfHarm = textFeatures.self_harm_risk_score || 0;

  const domainScores = {
    depression: clamp01(0.45 + negativeDensity + sadness + (selfHarm * 0.4) - (positiveDensity * 0.5)),
    anxiety: clamp01(0.2 + (negativeDensity * 1.1) + fear + (textFeatures.question_ratio * 2)),
    stress: clamp01(0.24 + (negativeDensity * 0.9) + anger + exhaustion + textFeatures.emotion_intensity * 0.4),
    sleep_disorder: clamp01(0.2 + exhaustion + (negativeDensity * 0.8)),
    burnout: clamp01(0.22 + exhaustion + anger * 0.3 + negativeDensity),
    loneliness: clamp01(0.18 + lonelinessEmotion + (1 - positiveDensity) * 0.2 + negativeDensity * 0.7),
    substance_abuse: clamp01(0.1 + anger * 0.2 + selfHarm * 0.2 + negativeDensity * 0.4),
  };

  const result = {
    available: true,
    modality: "text",
    confidence: clamp01(Math.min(textFeatures.word_count / 24, 1)),
    notes: "Dashboard text analysis uses browser-side heuristics for sentiment, emotions, and safety language.",
    features: {
      word_count: textFeatures.word_count,
      negative_word_count: textFeatures.negative_word_count,
      positive_word_count: textFeatures.positive_word_count,
      sentiment_label: textFeatures.sentiment_label,
      sentiment_model: textFeatures.sentiment_model,
      dominant_emotion: textFeatures.dominant_emotion,
      emotion_model: textFeatures.emotion_model,
      self_harm_keyword_detected: textFeatures.self_harm_keyword_detected,
      self_harm_keyword_matches: textFeatures.self_harm_keyword_matches,
      self_harm_risk_score: Number(textFeatures.self_harm_risk_score.toFixed(2)),
      transformer_model: textFeatures.transformer_model,
    },
  };

  DOMAINS.forEach((domain) => {
    result[`${domain}_score`] = domainScores[domain];
  });
  return result;
}

function buildMetadataModality(type, file) {
  if (!file) {
    return { available: false };
  }
  const result = {
    available: true,
    modality: type,
    confidence: 0.2,
    notes: `Dashboard captured ${type} upload metadata for ${file.name}. No browser-side ${type} model inference was run.`,
    features: {
      file_name: file.name,
      file_size_kb: Math.round(file.size / 1024),
      mime_type: file.type || "unknown",
    },
  };
  DOMAINS.forEach((domain) => {
    result[`${domain}_score`] = 0;
  });
  return result;
}

function buildOfflineMultimodal(payload) {
  const textFeatures = extractTextNlp(payload.text_input || "");
  const textResult = scoreDashboardText(textFeatures);
  const audioResult = buildMetadataModality("audio", payload.audio_file || null);
  const imageResult = buildMetadataModality("image", payload.image_file || null);
  const modalities = [textResult, audioResult, imageResult];
  const availableModalities = modalities.filter((item) => item.available);
  const overallScores = {};

  DOMAINS.forEach((domain) => {
    const questionnaireScore = Number(payload.questionnaire?.[`${domain}_score`] || 0);
    const modalityScores = availableModalities
      .map((item) => Number(item[`${domain}_score`] || 0))
      .filter((value) => value > 0);
    const combined = modalityScores.length
      ? average([questionnaireScore, average(modalityScores)])
      : questionnaireScore;
    overallScores[domain] = clamp01(combined);
  });

  const overall = {
    confidence: clamp01(
      (availableModalities.reduce((sum, item) => sum + Number(item.confidence || 0), 0) / Math.max(1, availableModalities.length)) * 0.6
      + 0.4
    ),
    scores: overallScores,
  };
  DOMAINS.forEach((domain) => {
    overall[domain] = riskLevel(overallScores[domain]);
  });

  const highestDomain = DOMAINS
    .map((domain) => ({ domain, score: overallScores[domain] }))
    .sort((left, right) => right.score - left.score)[0];
  const recommendation = highestDomain && highestDomain.score >= 0.66
    ? t("offlineScreeningElevatedLabel", { domain: localizedDomainLabel(highestDomain.domain) })
    : t("offlineScreeningCompletedLabel");

  return {
    text: textResult,
    audio: audioResult,
    image: imageResult,
    overall,
    model_stats: {
      offline_pwa: {
        source: "browser_offline_heuristic",
        service_worker: state.serviceWorkerReady,
      },
    },
    recommendation,
    disclaimer: "Offline-first preview used browser-side heuristics and local storage. Sync with the backend for a full server-side record.",
  };
}

function buildOfflineAssessmentRecord(payload) {
  return normalizeRecord({
    assessment_id: makeOfflineAssessmentId(),
    created_at: new Date().toISOString(),
    sync_status: "pending",
    profile: payload.profile,
    questionnaire: payload.questionnaire,
    multimodal: buildOfflineMultimodal(payload),
  });
}

function buildUploadMetadata(file) {
  if (!file) {
    return null;
  }
  return {
    file_name: file.name,
    file_size_kb: Math.round(file.size / 1024),
    mime_type: file.type || "unknown",
  };
}

function buildProfilePayload() {
  return {
    full_name: elements.fullName.value.trim(),
    age: Number(elements.age.value || 0),
    gender: elements.gender.value,
    village: elements.village.value.trim(),
    phone: elements.phone.value.trim(),
    assessor: elements.assessor.value.trim(),
    language: normalizeLanguage(elements.language.value),
    consent_received: elements.consent.checked,
    record_origin: "test",
  };
}

function buildAssessmentPayload() {
  const questionnaireResponses = collectQuestionnaireResponses();
  const questionnaire = scoreQuestionnaire(questionnaireResponses);
  return {
    profile: buildProfilePayload(),
    questionnaire,
    text_input: elements.textNarrative.value,
    audio_file: getCurrentAudioFile(),
    image_file: getCurrentImageFile(),
    audio_metadata: buildUploadMetadata(getCurrentAudioFile()),
    image_metadata: buildUploadMetadata(getCurrentImageFile()),
  };
}

function buildAssessmentFormData(payload) {
  const formData = new FormData();
  formData.append("profile", JSON.stringify(payload.profile));
  formData.append("questionnaire", JSON.stringify(payload.questionnaire));
  formData.append("text_input", payload.text_input || "");
  if (payload.audio_file) {
    formData.append("audio_file", payload.audio_file);
  }
  if (payload.image_file) {
    formData.append("image_file", payload.image_file);
  }
  return formData;
}

function buildAssessmentRecordFromAnalysis(payload, multimodal, assessmentId = "Draft Preview") {
  return {
    assessment_id: assessmentId,
    created_at: new Date().toISOString(),
    profile: payload.profile,
    questionnaire: payload.questionnaire,
    multimodal: {
      ...multimodal,
      disclaimer: "Preview only. Final saved record will be stored when the assessment is submitted.",
    },
  };
}

function createPdfBytes(record) {
  const lines = [
    t("pdfReportTitle"),
    `${t("assessmentIdLabel")}: ${record.assessment_id}`,
    `${t("createdAtLabel")}: ${record.created_at}`,
    `${t("candidateLabel")}: ${record.profile.full_name || t("unknownUserLabel")}`,
    `${t("villageShortLabel")}: ${record.profile.village || t("unknownLabel")}`,
    `${t("assessorShortLabel")}: ${record.profile.assessor || t("unknownLabel")}`,
    "",
  ];
  DOMAINS.forEach((domain) => {
    lines.push(`${localizedDomainLabel(domain)} ${t("pdfQuestionnaireLabel")}: ${localizedRiskLevel(record.questionnaire[`${domain}_risk`])}`);
    lines.push(`${localizedDomainLabel(domain)} ${t("pdfDashboardLabel")}: ${localizedRiskLevel(record.multimodal.overall[domain])}`);
  });
  lines.push("");
  lines.push(`${t("pdfRecommendationLabel")}: ${record.multimodal.recommendation}`);

  const textOps = ["BT", "/F1 11 Tf", "40 800 Td"];
  lines.forEach((line) => {
    const escaped = line.replace(/\\/g, "\\\\").replace(/\(/g, "\\(").replace(/\)/g, "\\)");
    textOps.push(`(${escaped}) Tj`);
    textOps.push("0 -16 Td");
  });
  textOps.push("ET");
  const content = textOps.join("\n");
  const encoder = new TextEncoder();
  const contentBytes = encoder.encode(content);
  const parts = [];
  parts.push("%PDF-1.4\n");
  const offsets = [0];
  const objects = [
    "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
    "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
    "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n",
    `4 0 obj << /Length ${contentBytes.length} >> stream\n${content}\nendstream endobj\n`,
    "5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
  ];
  let position = parts[0].length;
  objects.forEach((object) => {
    offsets.push(position);
    parts.push(object);
    position += object.length;
  });
  const xrefStart = position;
  parts.push(`xref\n0 ${offsets.length}\n`);
  parts.push("0000000000 65535 f \n");
  offsets.slice(1).forEach((offset) => {
    parts.push(`${String(offset).padStart(10, "0")} 00000 n \n`);
  });
  parts.push(`trailer << /Size ${offsets.length} /Root 1 0 R >>\nstartxref\n${xrefStart}\n%%EOF`);
  return new Blob(parts, { type: "application/pdf" });
}

function downloadPdfForRecord(record) {
  if (!record) return;
  const link = document.createElement("a");
  link.href = `/api/assessments/${encodeURIComponent(record.assessment_id)}/report.pdf`;
  link.download = `${record.assessment_id}_dashboard_report.pdf`;
  link.click();
}

function loadResults(records, sourceLabel, focusLatest = false) {
  setActiveResults(records, {
    focusLatest,
    bannerTone: "success",
  });
}

async function persistLocalRecord(record) {
  await offlineStorePut(OFFLINE_RECORDS_STORE, normalizeRecord(record));
}

async function removeLocalRecord(assessmentId) {
  await offlineStoreDelete(OFFLINE_RECORDS_STORE, assessmentId);
}

async function queueAssessmentForSync(payload, localRecord) {
  await offlineStorePut(OFFLINE_PENDING_STORE, {
    client_queue_id: localRecord.assessment_id,
    created_at: new Date().toISOString(),
    payload,
  });
  await persistLocalRecord(localRecord);
  await refreshPendingSyncCount();
}

async function loadOfflineRecords() {
  try {
    return uniqueRecords(await offlineStoreGetAll(OFFLINE_RECORDS_STORE));
  } catch (error) {
    console.error("Could not load offline records", error);
    return [];
  }
}

async function syncPendingAssessments() {
  if (!state.networkOnline) {
    await refreshPendingSyncCount();
    return;
  }

  let pendingEntries = [];
  try {
    pendingEntries = await offlineStoreGetAll(OFFLINE_PENDING_STORE);
  } catch (error) {
    console.error("Could not load pending assessments", error);
    return;
  }
  if (!pendingEntries.length) {
    await refreshPendingSyncCount();
    return;
  }

  for (const entry of pendingEntries) {
    try {
      const response = await fetch("/api/assessments", {
        method: "POST",
        body: buildAssessmentFormData(entry.payload),
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const savedRecord = normalizeRecord(await response.json());
      await persistLocalRecord(savedRecord);
      await removeLocalRecord(entry.client_queue_id);
      await offlineStoreDelete(OFFLINE_PENDING_STORE, entry.client_queue_id);
    } catch (error) {
      console.error("Pending assessment sync failed", error);
    }
  }

  const offlineRecords = await loadOfflineRecords();
  if (offlineRecords.length) {
    setActiveResults(offlineRecords, {
      focusLatest: true,
      bannerMessage: "Offline queue synced where possible and local records were refreshed.",
      bannerTone: "success",
    });
  }
  await refreshPendingSyncCount();
}

function populateFilterOptions() {
  return;
}

function getOverallLevels(record) {
  const overall = record?.multimodal?.overall || {};
  return DOMAINS.map((domain) => overall[domain] || "low");
}

function dominantRisk(record) {
  const overall = record?.multimodal?.overall || {};
  return DOMAINS.find((domain) => overall[domain] === "high")
    || DOMAINS.find((domain) => overall[domain] === "moderate")
    || DOMAINS[0];
}

function matchesRiskFilter(record, filterValue) {
  const levels = getOverallLevels(record);
  if (filterValue === "all") return true;
  if (filterValue === "high") return levels.includes("high");
  if (filterValue === "moderate") return levels.includes("moderate") || levels.includes("high");
  if (filterValue === "low") return levels.every((level) => level === "low");
  return true;
}

function sortResults(results) {
  const mode = "latest";
  return [...results].sort((left, right) => {
    if (mode === "oldest") return new Date(left.created_at) - new Date(right.created_at);
    if (mode === "confidence") return (right.multimodal?.overall?.confidence || 0) - (left.multimodal?.overall?.confidence || 0);
    if (mode === "name") return normalizeText(left.profile?.full_name).localeCompare(normalizeText(right.profile?.full_name));
    return new Date(right.created_at) - new Date(left.created_at);
  });
}

function applyFilters() {
  state.filteredResults = sortResults([...state.allResults]);

  if (!state.filteredResults.length) {
    state.selectedRecord = null;
  } else if (!state.selectedRecord || !state.filteredResults.some((record) => record.assessment_id === state.selectedRecord.assessment_id)) {
    state.selectedRecord = state.filteredResults[0];
  }

  state.currentPage = Math.min(state.currentPage, Math.max(1, Math.ceil(state.filteredResults.length / 10)));
  renderDashboard();
}

function getAnalysisRecord() {
  return state.selectedRecord || state.latestCreatedRecord || null;
}

function strongestDomain(record) {
  if (!record) return null;
  return DOMAINS
    .map((domain) => ({ domain, score: Number(record.multimodal?.overall?.scores?.[domain] || 0) }))
    .sort((left, right) => right.score - left.score)[0]?.domain || null;
}

function overallRiskLabel(record) {
  if (!record) return t("noDataLabel");
  const levels = DOMAINS.map((domain) => record.multimodal?.overall?.[domain] || "low");
  if (levels.includes("high")) return localizedRiskLevel("high");
  if (levels.includes("moderate")) return localizedRiskLevel("moderate");
  return localizedRiskLevel("low");
}

function normalizeIdentityValue(value) {
  return String(value || "").trim().toLowerCase().replace(/\s+/g, " ");
}

function normalizePhone(value) {
  return String(value || "").replace(/\D+/g, "");
}

function patientKeyFromProfile(profile = {}) {
  const explicit = normalizeIdentityValue(profile.patient_id);
  if (explicit) return `patient_id:${explicit}`;
  const phone = normalizePhone(profile.phone);
  if (phone.length >= 6) return `phone:${phone}`;
  const parts = [
    normalizeIdentityValue(profile.full_name),
    normalizeIdentityValue(profile.village),
    String(profile.age || "").trim(),
    normalizeIdentityValue(profile.gender),
  ].filter(Boolean);
  return parts.length ? `profile:${parts.join("|")}` : "unknown";
}

function averageOverallScore(record) {
  return average(DOMAINS.map((domain) => Number(record?.multimodal?.overall?.scores?.[domain] || 0)));
}

function linearSlope(points) {
  if (!Array.isArray(points) || points.length < 2) return 0;
  const meanX = average(points.map((point) => Number(point.x || 0)));
  const meanY = average(points.map((point) => Number(point.y || 0)));
  const denominator = points.reduce((sum, point) => sum + ((Number(point.x || 0) - meanX) ** 2), 0);
  if (!denominator) return 0;
  const numerator = points.reduce(
    (sum, point) => sum + ((Number(point.x || 0) - meanX) * (Number(point.y || 0) - meanY)),
    0,
  );
  return numerator / denominator;
}

function trajectoryStatusLabel(status) {
  return localizedTrajectoryStatus(status);
}

function buildLocalTrajectory(record) {
  if (!record) return null;
  const patientKey = record.patient_key || patientKeyFromProfile(record.profile);
  const history = state.allResults
    .filter((item) => (item.patient_key || patientKeyFromProfile(item.profile)) === patientKey)
    .sort((left, right) => new Date(left.created_at) - new Date(right.created_at));
  if (!history.length) return null;

  const points = history.map((item, index) => {
    const overallScore = averageOverallScore(item);
    const scores = Object.fromEntries(DOMAINS.map((domain) => [domain, Number(item.multimodal?.overall?.scores?.[domain] || 0)]));
    const strongest = DOMAINS
      .map((domain) => ({ domain, score: scores[domain] }))
      .sort((left, right) => right.score - left.score)[0]?.domain || DOMAINS[0];
    return {
      assessment_id: item.assessment_id,
      created_at: item.created_at,
      sequence: index + 1,
      overall_score: overallScore,
      overall_risk: item.multimodal?.overall?.[strongest] || "low",
      confidence: Number(item.multimodal?.overall?.confidence || 0),
      scores,
      strongest_domain: strongest,
      elapsed_days: index,
    };
  });

  const baseline = points[0];
  const latest = points[points.length - 1];
  const previous = points[points.length - 2] || points[0];
  const overallSlope = linearSlope(points.map((point, index) => ({ x: index, y: point.overall_score })));
  const changeFromBaseline = latest.overall_score - baseline.overall_score;
  const changeFromPrevious = latest.overall_score - previous.overall_score;
  const stepChanges = points.slice(1).map((point, index) => Math.abs(point.overall_score - points[index].overall_score));
  const volatility = stepChanges.length ? average(stepChanges) : 0;

  const domains = Object.fromEntries(DOMAINS.map((domain) => {
    const slope = linearSlope(points.map((point, index) => ({ x: index, y: point.scores[domain] })));
    const direction = slope >= 0.035 ? "worsening" : slope <= -0.035 ? "improving" : "stable";
    return [domain, {
      latest_score: latest.scores[domain],
      baseline_score: baseline.scores[domain],
      change_from_baseline: latest.scores[domain] - baseline.scores[domain],
      slope_per_day: slope,
      direction,
    }];
  }));

  let status = "stable";
  if (points.length < 2) {
    status = "insufficient_history";
  } else if (volatility >= 0.16 && Math.abs(overallSlope) < 0.03) {
    status = "volatile";
  } else if (overallSlope >= 0.035 || changeFromPrevious >= 0.12) {
    status = latest.overall_risk === "high" || changeFromBaseline >= 0.2 ? "escalating" : "worsening";
  } else if (overallSlope <= -0.035 || changeFromPrevious <= -0.12) {
    status = "improving";
  }

  const summary = localizedTrajectorySummary(status);

  return {
    patient_key: patientKey,
    history_count: points.length,
    status,
    status_label: trajectoryStatusLabel(status),
    summary,
    latest_assessment_id: latest.assessment_id,
    baseline_assessment_id: baseline.assessment_id,
    latest_overall_score: latest.overall_score,
    baseline_overall_score: baseline.overall_score,
    change_from_baseline: changeFromBaseline,
    change_from_previous: changeFromPrevious,
    slope_per_day: overallSlope,
    volatility,
    strongest_domain: latest.strongest_domain,
    domains,
    points,
  };
}

function getTrajectory(record) {
  if (!record) return null;
  if (record.trajectory && typeof record.trajectory === "object") {
    return record.trajectory;
  }
  return buildLocalTrajectory(record);
}

function renderOverview() {
  const record = getAnalysisRecord();
  if (!record) {
    elements.analysisAssessmentId.textContent = t("noDataLabel");
    elements.analysisConfidence.textContent = "0%";
    elements.analysisStrongestDomain.textContent = t("noDataLabel");
    elements.analysisCoverage.textContent = "0/3";
    elements.analysisSubmissionTime.textContent = t("noDataLabel");
    if (elements.analysisTrajectory) elements.analysisTrajectory.textContent = t("noDataLabel");
    elements.analysisOverallRisk.textContent = t("noDataLabel");
    setBanner(elements.analysisStatusBanner, t("analyticsBannerDefault"), "neutral");
    return;
  }

  const modalitiesUsed = ["text", "audio", "image"].filter((key) => record.multimodal?.[key]?.available).length;
  const dominant = strongestDomain(record);
  const trajectory = getTrajectory(record);
  elements.analysisAssessmentId.textContent = record.assessment_id;
  elements.analysisConfidence.textContent = formatPercent(record.multimodal?.overall?.confidence || 0);
  elements.analysisStrongestDomain.textContent = dominant ? localizedDomainLabel(dominant) : t("noDataLabel");
  elements.analysisCoverage.textContent = `${modalitiesUsed}/3`;
  elements.analysisSubmissionTime.textContent = formatDate(record.created_at);
  if (elements.analysisTrajectory) {
    elements.analysisTrajectory.textContent = trajectory ? trajectoryStatusLabel(trajectory.status) : t("noMoreDataLabel");
  }
  elements.analysisOverallRisk.textContent = overallRiskLabel(record);
  const comorbidity = record.multimodal?.comorbidity || {};
  const topPair = comorbidity.top_pairs?.[0] || null;
  const comorbidityText = topPair?.domains?.length === 2
    ? ` ${t("topComorbidityLabel")}: ${localizedDomainLabel(topPair.domains[0])} + ${localizedDomainLabel(topPair.domains[1])} (${Number(topPair.probability || 0).toFixed(2)})`
    : "";
  setBanner(elements.analysisStatusBanner, `${record.profile?.full_name || t("currentUserLabel")}: ${t("analyticsReady")}${comorbidityText}`, "success");
}

function formatShortDateLabel(value) {
  if (!value || value === "Unknown") return value || "Unknown";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleDateString([], { month: "short", day: "numeric" });
}

function buildChartCard(title, subtitle, visual, footer = "") {
  return `
    <div class="chart-card">
      <div class="tile-top"><strong>${title}</strong>${subtitle ? `<span class="summary-meta">${subtitle}</span>` : ""}</div>
      ${visual}
      ${footer ? `<p class="chart-note">${footer}</p>` : ""}
    </div>
  `;
}

function formatMetricNumber(value, digits = 2) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return "N/A";
  return numeric.toFixed(digits);
}

function formatCompactPath(value) {
  if (!value) return "Unavailable";
  const parts = String(value).split(/[\\/]+/).filter(Boolean);
  return parts.slice(-2).join("/");
}

function getModelStats(record) {
  return record?.multimodal?.model_stats || {};
}

function getModelComparisonRows(record) {
  const modelStats = getModelStats(record);
  return ["text", "audio", "image"].map((modality) => {
    const summary = modelStats[modality] || null;
    const modalityPayload = record?.multimodal?.[modality] || {};
    const features = modalityPayload.features || {};
    return {
      modality,
      label: modality.charAt(0).toUpperCase() + modality.slice(1),
      source: summary?.model_source || features.model_source || "backend_heuristic",
      macroR2: Number(summary?.macro_r2 ?? features.model_macro_r2 ?? 0),
      confidenceHint: Number(summary?.confidence_hint ?? modalityPayload.confidence ?? 0),
      sampleCount: Number(summary?.sample_count ?? features.trained_samples ?? 0),
      trainedAt: summary?.trained_at || "Unavailable",
      datasetRoot: summary?.dataset_root || "Unavailable",
      manifestPath: summary?.manifest_path || "Unavailable",
      domains: Array.isArray(summary?.domains) ? summary.domains : (Array.isArray(features.trained_domains) ? features.trained_domains : []),
      domainSampleCounts: summary?.sample_counts || features.domain_sample_counts || {},
    };
  });
}

function buildStackedDistributionSvg(items) {
  const width = 720;
  const rowHeight = 36;
  const topPad = 34;
  const leftPad = 130;
  const chartWidth = width - leftPad - 24;
  const height = topPad + (items.length * rowHeight) + 18;
  const legend = `
    <div class="chart-legend">
      <span><i class="legend-swatch low"></i>Low</span>
      <span><i class="legend-swatch moderate"></i>Moderate</span>
      <span><i class="legend-swatch high"></i>High</span>
    </div>
  `;
  const rows = items.map((item, index) => {
    const y = topPad + (index * rowHeight);
    const total = item.low + item.moderate + item.high || 1;
    const lowWidth = (item.low / total) * chartWidth;
    const moderateWidth = (item.moderate / total) * chartWidth;
    const highWidth = (item.high / total) * chartWidth;
    return `
      <text x="8" y="${y + 15}" class="svg-axis-text">${item.label}</text>
      <rect x="${leftPad}" y="${y}" width="${chartWidth}" height="18" rx="9" fill="rgba(107,45,25,0.08)"></rect>
      <rect x="${leftPad}" y="${y}" width="${lowWidth}" height="18" rx="9" fill="#50793d"></rect>
      <rect x="${leftPad + lowWidth}" y="${y}" width="${moderateWidth}" height="18" fill="#bd892e"></rect>
      <rect x="${leftPad + lowWidth + moderateWidth}" y="${y}" width="${highWidth}" height="18" rx="9" fill="#b3473d"></rect>
      <text x="${width - 10}" y="${y + 15}" text-anchor="end" class="svg-value-text">${Math.round((item.high / total) * 100)}% high</text>
    `;
  }).join("");
  return `
    ${legend}
    <svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Risk distribution chart">
      ${rows}
    </svg>
  `;
}

function buildLineTrendSvg(points) {
  const width = 720;
  const height = 240;
  const padLeft = 42;
  const padRight = 16;
  const padTop = 18;
  const padBottom = 36;
  const chartWidth = width - padLeft - padRight;
  const chartHeight = height - padTop - padBottom;
  const maxValue = Math.max(...points.map((item) => item.count), 1);
  const stepX = points.length > 1 ? chartWidth / (points.length - 1) : 0;
  const pointXY = points.map((item, index) => {
    const x = padLeft + (index * stepX);
    const y = padTop + chartHeight - ((item.count / maxValue) * chartHeight);
    return { ...item, x, y };
  });
  const linePath = pointXY.map((point, index) => `${index === 0 ? "M" : "L"} ${point.x} ${point.y}`).join(" ");
  const areaPath = `${linePath} L ${padLeft + chartWidth} ${padTop + chartHeight} L ${padLeft} ${padTop + chartHeight} Z`;
  const grid = Array.from({ length: 4 }, (_, index) => {
    const y = padTop + ((chartHeight / 3) * index);
    return `<line x1="${padLeft}" y1="${y}" x2="${padLeft + chartWidth}" y2="${y}" class="svg-grid-line"></line>`;
  }).join("");
  const labels = pointXY.map((point) => `
    <text x="${point.x}" y="${height - 10}" text-anchor="middle" class="svg-axis-text">${formatShortDateLabel(point.label)}</text>
  `).join("");
  const dots = pointXY.map((point) => `
    <circle cx="${point.x}" cy="${point.y}" r="4.5" fill="#9e4d29"></circle>
    <text x="${point.x}" y="${point.y - 10}" text-anchor="middle" class="svg-value-text">${point.count}</text>
  `).join("");
  return `
    <svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img" aria-label="Submission trend line chart">
      ${grid}
      <path d="${areaPath}" fill="rgba(40, 121, 112, 0.12)"></path>
      <path d="${linePath}" fill="none" stroke="#287970" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></path>
      ${dots}
      ${labels}
    </svg>
  `;
}

function buildHorizontalMetricSvg(items, color) {
  const width = 720;
  const rowHeight = 34;
  const leftPad = 150;
  const topPad = 18;
  const chartWidth = width - leftPad - 20;
  const height = topPad + (items.length * rowHeight) + 10;
  const maxValue = Math.max(...items.map((item) => item.value), 0.01);
  const rows = items.map((item, index) => {
    const y = topPad + (index * rowHeight);
    const barWidth = (item.value / maxValue) * chartWidth;
    return `
      <text x="8" y="${y + 15}" class="svg-axis-text">${item.label}</text>
      <rect x="${leftPad}" y="${y}" width="${chartWidth}" height="16" rx="8" fill="rgba(107,45,25,0.08)"></rect>
      <rect x="${leftPad}" y="${y}" width="${barWidth}" height="16" rx="8" fill="${color}"></rect>
      <text x="${width - 10}" y="${y + 14}" text-anchor="end" class="svg-value-text">${item.display}</text>
    `;
  }).join("");
  return `<svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">${rows}</svg>`;
}

function buildNlpCoverageSvg(sentimentCounts, total, selfHarmHits, textAvailable, audioAvailable, imageAvailable) {
  const width = 720;
  const height = 170;
  const labelY = 30;
  const barY = 48;
  const barHeight = 22;
  const startX = 18;
  const barWidth = 300;
  const positiveWidth = total ? (sentimentCounts.positive / total) * barWidth : 0;
  const negativeWidth = total ? (sentimentCounts.negative / total) * barWidth : 0;
  const coverage = [
    { label: "Text", count: textAvailable, color: "#287970" },
    { label: "Audio", count: audioAvailable, color: "#9e4d29" },
    { label: "Image", count: imageAvailable, color: "#bd892e" },
  ];
  const coverageMarks = coverage.map((item, index) => {
    const x = 380 + (index * 108);
    const heightPx = total ? (item.count / total) * 80 : 0;
    return `
      <rect x="${x}" y="${128 - heightPx}" width="42" height="${heightPx}" rx="10" fill="${item.color}"></rect>
      <text x="${x + 21}" y="145" text-anchor="middle" class="svg-axis-text">${item.label}</text>
      <text x="${x + 21}" y="${120 - heightPx}" text-anchor="middle" class="svg-value-text">${item.count}</text>
    `;
  }).join("");
  return `
    <div class="chart-legend">
      <span><i class="legend-swatch low"></i>Positive</span>
      <span><i class="legend-swatch high"></i>Negative</span>
      <span>Self-harm hits: ${selfHarmHits}</span>
    </div>
    <svg class="chart-svg" viewBox="0 0 ${width} ${height}" role="img">
      <text x="${startX}" y="${labelY}" class="svg-axis-text">${t("sentimentLabel")}</text>
      <rect x="${startX}" y="${barY}" width="${barWidth}" height="${barHeight}" rx="11" fill="rgba(107,45,25,0.08)"></rect>
      <rect x="${startX}" y="${barY}" width="${positiveWidth}" height="${barHeight}" rx="11" fill="#50793d"></rect>
      <rect x="${startX + positiveWidth}" y="${barY}" width="${negativeWidth}" height="${barHeight}" rx="11" fill="#b3473d"></rect>
      <text x="${startX}" y="${barY + 42}" class="svg-value-text">Positive ${sentimentCounts.positive} | Negative ${sentimentCounts.negative}</text>
      <text x="380" y="${labelY}" class="svg-axis-text">Modality coverage</text>
      ${coverageMarks}
    </svg>
  `;
}

function renderRiskDistribution() {
  const record = getAnalysisRecord();
  if (!record) {
    elements.riskDistribution.className = "chart-stack empty-state";
    elements.riskDistribution.textContent = t("noAssessmentAnalysis");
    return;
  }

  const comparisonCards = DOMAINS.map((domain) => `
    <div class="compare-card">
      <div class="score-header"><span>${localizedDomainLabel(domain)}</span><strong>${(record.multimodal?.overall?.[domain] || "low").toUpperCase()}</strong></div>
      ${scoreLine(t("questionnaireLabel"), Number(record.questionnaire?.[`${domain}_score`] || 0))}
      ${scoreLine(t("combinedAiLabel"), Number(record.multimodal?.overall?.scores?.[domain] || 0))}
    </div>
  `).join("");

  elements.riskDistribution.className = "chart-stack";
  elements.riskDistribution.innerHTML = buildChartCard(
    t("domainScoreComparisonTitle"),
    t("domainScoreComparisonText"),
    comparisonCards,
    t("domainScoreComparisonDescription")
  );
}

function renderSubmissionTrend() {
  const record = getAnalysisRecord();
  if (!record) {
    elements.submissionTrend.className = "chart-stack empty-state";
    elements.submissionTrend.textContent = t("noComponentBreakdown");
    return;
  }
  const modalityRows = ["text", "audio", "image"].map((modality) => {
    const payload = record.multimodal?.[modality] || {};
    const avgScore = average(DOMAINS.map((domain) => Number(payload[`${domain}_score`] || 0)));
    return {
      label: modality.charAt(0).toUpperCase() + modality.slice(1),
      value: Number(payload.confidence || 0),
      display: `${formatPercent(payload.confidence || 0)} conf | ${avgScore.toFixed(2)} avg score`,
    };
  });
  elements.submissionTrend.className = "chart-stack";
  elements.submissionTrend.innerHTML = buildChartCard(
    "Component Contribution",
    "Confidence and average signal strength by modality",
    buildHorizontalMetricSvg(modalityRows, "#287970"),
    "This view shows how strongly text, audio, and image contributed to the final screening result."
  );
}

function renderRiskHotspots() {
  const record = getAnalysisRecord();
  if (!record) {
    elements.riskHotspots.className = "chart-stack empty-state";
    elements.riskHotspots.textContent = t("noModalityQuality");
    return;
  }

  const cards = ["text", "audio", "image"].map((modality) => {
    const payload = record.multimodal?.[modality] || {};
    const features = payload.features || {};
    const metadata = [];
    if (features.transformer_model && features.transformer_model !== "unavailable") metadata.push(features.transformer_model);
    if (features.vision_backend) metadata.push(features.vision_backend);
    if (features.duration) metadata.push(`${Number(features.duration).toFixed(1)}s`);
    if (features.voiced_ratio !== undefined) metadata.push(`voiced ${Math.round(Number(features.voiced_ratio) * 100)}%`);
    return `
      <div class="detail-card">
        <div class="detail-inline"><h3>${localizedModalityLabel(modality)}</h3><strong>${payload.available ? t("usableLabel") : t("limitedLabel")}</strong></div>
        ${scoreLine(t("confidenceLabel"), Number(payload.confidence || 0))}
        <p class="detail-muted">${payload.notes || t("noModalityNoteLabel")}</p>
        <p class="detail-muted">${metadata.join(" | ") || t("noAdditionalProcessingStatsLabel")}</p>
      </div>
    `;
  }).join("");

  elements.riskHotspots.className = "chart-stack";
  elements.riskHotspots.innerHTML = buildChartCard(
    t("modalityQualityTitle"),
    t("modalityQualityShortText"),
    cards,
    t("modalityQualityHelperText")
  );
}

function renderNlpTrends() {
  const record = getAnalysisRecord();
  if (!record) {
    elements.nlpTrends.className = "chart-stack empty-state";
    elements.nlpTrends.textContent = t("noRecommendationDetails");
    return;
  }

  elements.nlpTrends.className = "chart-stack";
  elements.nlpTrends.innerHTML = buildChartCard(
    t("recommendationAndDisclaimerTitle"),
    overallRiskLabel(record),
    `
      <div class="detail-card">
        <h3>${t("recommendationTitle")}</h3>
        <p>${record.multimodal?.recommendation || t("noRecommendationText")}</p>
      </div>
      <div class="detail-card">
        <h3>${t("screeningDisclaimerTitle")}</h3>
        <p>${record.multimodal?.disclaimer || t("noDisclaimerText")}</p>
      </div>
    `,
    t("recommendationOverviewText")
  );
}

function renderTrajectoryModel() {
  const record = getAnalysisRecord();
  const trajectory = getTrajectory(record);
  if (!record || !trajectory) {
    elements.trajectoryModel.className = "chart-stack empty-state";
    elements.trajectoryModel.textContent = t("noTrajectoryLabel");
    elements.trajectorySummary.className = "chart-stack empty-state";
    elements.trajectorySummary.textContent = t("noTrendSummaryLabel");
    return;
  }

  const chartPoints = trajectory.points.map((point) => ({
    label: point.created_at,
    count: Math.round(Number(point.overall_score || 0) * 100),
  }));
  elements.trajectoryModel.className = "chart-stack";
  elements.trajectoryModel.innerHTML = buildChartCard(
    t("overallRiskTrajectoryTitle"),
    t("screeningCountLabel", { count: trajectory.history_count, status: trajectoryStatusLabel(trajectory.status) }),
    buildLineTrendSvg(chartPoints),
    trajectory.summary,
  );

  const domainCards = DOMAINS.map((domain) => {
    const info = trajectory.domains?.[domain] || {};
    const change = Number(info.change_from_baseline || 0);
    return `
      <div class="detail-card">
        <div class="detail-inline"><h3>${localizedDomainLabel(domain)}</h3><strong>${localizedTrajectoryStatus(info.direction || "stable")}</strong></div>
        ${scoreLine(t("currentLabel"), Number(info.latest_score || 0))}
        <p class="detail-muted">${t("changeSinceBaselineLabel")}: ${change >= 0 ? "+" : ""}${change.toFixed(2)}</p>
      </div>
    `;
  }).join("");
  elements.trajectorySummary.className = "chart-stack";
  elements.trajectorySummary.innerHTML = buildChartCard(
    t("trendSummaryTitle"),
    t("baselineToCurrentLabel", {
      baseline: Number(trajectory.baseline_overall_score || 0).toFixed(2),
      current: Number(trajectory.latest_overall_score || 0).toFixed(2),
    }),
    `
      <div class="detail-grid compact-grid">
        <div class="detail-card">
          <h3>${t("statusTitle")}</h3>
          <p>${trajectoryStatusLabel(trajectory.status)}</p>
          <p class="detail-muted">${trajectory.summary}</p>
        </div>
        <div class="detail-card">
          <h3>${t("trajectoryMetricsTitle")}</h3>
          <p>${t("changeSinceBaselineLabel")}: ${Number(trajectory.change_from_baseline || 0).toFixed(2)}</p>
          <p>${t("recentChangeLabel")}: ${Number(trajectory.change_from_previous || 0).toFixed(2)}</p>
          <p>${t("volatilityLabel")}: ${Number(trajectory.volatility || 0).toFixed(2)}</p>
        </div>
      </div>
      <div class="detail-grid compact-grid">${domainCards}</div>
    `,
    t("trendModelDescription"),
  );
}

function renderModelStatistics() {
  const record = getAnalysisRecord();
  if (!record) {
    elements.villageSummary.className = "chart-stack empty-state";
    elements.villageSummary.textContent = t("noModelStats");
    return;
  }

  const textFeatures = record.multimodal?.text?.features || {};
  const modelRows = getModelComparisonRows(record);
  const availableRows = modelRows.filter((item) => item.sampleCount > 0 || item.source === "trained_bundle");

  if (!availableRows.length) {
    elements.villageSummary.className = "chart-stack empty-state";
    elements.villageSummary.textContent = t("noTrainedModelStatsLabel");
    return;
  }

  const summaryCards = [
    { label: t("textTransformerLabel"), value: textFeatures.transformer_model || t("unavailableLabel") },
    { label: `${t("sentimentLabel")} ${t("analysisEngineLabel")}`, value: textFeatures.sentiment_model || t("unavailableLabel") },
    { label: `${t("emotionLabel")} ${t("analysisEngineLabel")}`, value: textFeatures.emotion_model || t("unavailableLabel") },
    { label: t("trainedModalitiesLabel"), value: `${availableRows.length}/3` },
  ];

  const metricChart = buildHorizontalMetricSvg(
    availableRows.map((item) => ({
      label: item.label,
      value: Math.max(item.macroR2, 0),
      display: `R2 ${formatMetricNumber(item.macroR2, 3)} | ${item.sampleCount} samples`,
    })),
    "#9e4d29"
  );

  const comparisonCards = availableRows.map((item) => `
    <div class="detail-card">
      <div class="detail-inline"><h3>${item.label}</h3><strong>${item.source === "trained_bundle" ? t("trainedBundleLabel") : t("fallbackLabel")}</strong></div>
      ${scoreLine(t("confidenceHintLabel"), item.confidenceHint)}
      <p class="detail-muted">${t("macroR2Label")}: ${formatMetricNumber(item.macroR2, 3)}</p>
      <p class="detail-muted">${t("samplesLabel")}: ${item.sampleCount}</p>
      <p class="detail-muted">${t("domainsLabel")}: ${item.domains.length ? item.domains.map((domain) => localizedDomainLabel(domain)).join(", ") : t("unavailableLabel")}</p>
      <p class="detail-muted">${t("manifestLabel")}: ${formatCompactPath(item.manifestPath)}</p>
      <p class="detail-muted">${t("datasetRootLabel")}: ${formatCompactPath(item.datasetRoot)}</p>
      <p class="detail-muted">${t("trainedAtLabel")}: ${item.trainedAt === "Unavailable" ? t("unavailableLabel") : formatDate(item.trainedAt)}</p>
    </div>
  `).join("");

  elements.villageSummary.className = "chart-stack";
  elements.villageSummary.innerHTML = `
    <div class="tile-grid">
      ${summaryCards.map((item) => `
        <div class="summary-tile">
          <div class="tile-top"><span>${item.label}</span><strong>${item.value}</strong></div>
        </div>
      `).join("")}
    </div>
    ${buildChartCard(
      t("trainedBundleComparisonTitle"),
      t("macroR2CoverageText"),
      metricChart,
      t("trainedBundleDescription")
    )}
    <div class="compare-grid">
      ${comparisonCards}
    </div>
  `;
}

function renderNlpSignalSummary() {
  const record = getAnalysisRecord();
  if (!record) {
    elements.assessorSummary.className = "tile-grid empty-state";
    elements.assessorSummary.textContent = t("noNlpSummary");
    return;
  }

  const features = record.multimodal?.text?.features || {};
  const modelRows = getModelComparisonRows(record).filter((item) => item.sampleCount > 0 || item.source === "trained_bundle");
  const trainedDomainTotal = modelRows.reduce((sum, item) => sum + item.domains.length, 0);
  const cards = [
    { label: t("sentimentLabel"), value: features.sentiment_label || t("unknownLabel") },
    { label: t("emotionLabel"), value: features.dominant_emotion || t("unknownLabel") },
    { label: t("safetyKeywordsLabel"), value: features.self_harm_keyword_detected ? t("detectedLabel") : t("notDetectedLabel") },
    { label: t("keywordMatchesLabel"), value: (features.self_harm_keyword_matches || []).join(", ") || t("noneLabel") },
    { label: t("narrativeWordCountLabel"), value: features.word_count || 0 },
    { label: `${t("emotionLabel")} ${t("emotionIntensityLabel")}`, value: Number(features.emotion_intensity || 0).toFixed(2) },
    { label: t("trainedModalitiesLabel"), value: modelRows.length || 0 },
    { label: t("domainCoverageLabel"), value: trainedDomainTotal || 0 },
  ];
  elements.assessorSummary.className = "tile-grid";
  elements.assessorSummary.innerHTML = cards.map((item) => `
    <div class="summary-tile">
      <div class="tile-top"><span>${item.label}</span><strong>${item.value}</strong></div>
    </div>
  `).join("");
}

function wireSummaryTileClicks() {
  return;
}

function renderTable() {
  const results = state.filteredResults;
  if (!results.length) {
    elements.resultsTableBody.innerHTML = `<tr><td colspan="7" class="table-empty">${t("noMatchRecords")}</td></tr>`;
    elements.pageStatus.textContent = tf("pageStatus", { page: "1", total: "1" });
    elements.prevPageBtn.disabled = true;
    elements.nextPageBtn.disabled = true;
    return;
  }
  const pageSize = 10;
  const totalPages = Math.max(1, Math.ceil(results.length / pageSize));
  const start = (state.currentPage - 1) * pageSize;
  const pageItems = results.slice(start, start + pageSize);
  elements.resultsTableBody.innerHTML = pageItems.map((record) => {
    const domain = dominantRisk(record);
    const level = record.multimodal?.overall?.[domain] || "low";
    return `
      <tr class="table-row ${state.selectedRecord?.assessment_id === record.assessment_id ? "selected" : ""}" data-id="${record.assessment_id}">
        <td>${record.assessment_id}</td>
        <td>${record.profile?.full_name || t("unknownUserLabel")}</td>
        <td>${record.profile?.village || t("unknownLabel")}</td>
        <td>${record.profile?.assessor || t("unknownLabel")}</td>
        <td>${formatDate(record.created_at)}</td>
        <td><span class="risk-pill ${level}">${localizedDomainLabel(domain)} ${localizedRiskLevel(level)}</span></td>
        <td>${formatPercent(record.multimodal?.overall?.confidence || 0)}</td>
      </tr>
    `;
  }).join("");
  elements.resultsTableBody.querySelectorAll("[data-id]").forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedRecord = state.filteredResults.find((record) => record.assessment_id === row.dataset.id) || null;
      renderDashboard();
    });
  });
  elements.pageStatus.textContent = tf("pageStatus", { page: String(state.currentPage), total: String(totalPages) });
  elements.prevPageBtn.disabled = state.currentPage <= 1;
  elements.nextPageBtn.disabled = state.currentPage >= totalPages;
}

function scoreLine(label, value) {
  return `
    <div class="score-line">
      <div class="score-header"><span>${label}</span><strong>${(Number(value) || 0).toFixed(2)}</strong></div>
      <div class="score-track"><div class="score-fill" style="width:${clamp01(value) * 100}%"></div></div>
    </div>
  `;
}

function renderSelectedAssessment() {
  const record = state.selectedRecord;
  if (!record) {
    elements.selectedAssessment.className = "empty-state";
    elements.selectedAssessment.textContent = t("noRecordSelected");
    return;
  }
  const questionnairePills = DOMAINS.map((domain) => `<span class="risk-pill ${record.questionnaire[`${domain}_risk`]}">${localizedDomainLabel(domain)} ${localizedRiskLevel(record.questionnaire[`${domain}_risk`])}</span>`).join("");
  const overallPills = DOMAINS.map((domain) => `<span class="risk-pill ${record.multimodal.overall[domain]}">${localizedDomainLabel(domain)} ${localizedRiskLevel(record.multimodal.overall[domain])}</span>`).join("");
  elements.selectedAssessment.className = "detail-stack";
  elements.selectedAssessment.innerHTML = `
    <div class="detail-card">
      <div class="detail-inline"><h3>${record.profile.full_name || t("unknownUserLabel")}</h3><strong>${record.assessment_id}</strong></div>
      <p class="detail-muted">${record.profile.village || t("unknownLocationLabel")} | ${t("ageLabel")}: ${record.profile.age || t("noDataMetricLabel")} | ${record.profile.gender || t("notStatedLabel")}</p>
      <p class="detail-muted">${t("assessorLabel")}: ${record.profile.assessor || t("noDataMetricLabel")} | ${t("languageLabel")}: ${record.profile.language || t("noDataMetricLabel")} | ${t("phoneLabel")}: ${record.profile.phone || t("noDataMetricLabel")}</p>
      <p class="detail-muted">${t("createdAtLabel")}: ${formatDate(record.created_at)}</p>
      <div class="action-row">
        <button id="deleteSelectedRecordBtn" class="ghost-btn small-btn" type="button">${t("deleteRecord")}</button>
      </div>
    </div>
    <div class="detail-card">
      <h3>${t("questionnaireRiskTitle")}</h3>
      <div class="detail-inline">${questionnairePills}</div>
      ${scoreLine(t("questionnaireOverall"), record.questionnaire.overall_score)}
    </div>
    <div class="detail-card">
      <h3>${t("combinedResultTitle")}</h3>
      <div class="detail-inline">${overallPills}</div>
      ${scoreLine(t("confidenceLabel"), record.multimodal.overall.confidence)}
      ${DOMAINS.map((domain) => scoreLine(`${localizedDomainLabel(domain)} ${t("scoreLabel")}`, record.multimodal.overall.scores[domain])).join("")}
    </div>
    <div class="detail-card">
      <h3>${t("recommendationLabel")}</h3>
      <p>${record.multimodal.recommendation}</p>
      <p class="detail-muted">${record.multimodal.disclaimer}</p>
    </div>
  `;
  const deleteButton = elements.selectedAssessment.querySelector("#deleteSelectedRecordBtn");
  if (deleteButton) {
    deleteButton.addEventListener("click", () => deleteSelectedAssessmentRecord(record.assessment_id));
  }
}

function comparisonRow(label, questionnaireValue, multimodalValue) {
  const safeQuestionnaire = Number(questionnaireValue || 0);
  const safeMultimodal = Number(multimodalValue || 0);
  return `
    <div class="compare-card">
      <h3>${label}</h3>
      <div class="score-line">
        <div class="score-header"><span>${t("questionnaireLabel")}</span><strong>${safeQuestionnaire.toFixed(2)}</strong></div>
        <div class="dual-track"><div class="score-fill dual-fill questionnaire" style="width:${clamp01(safeQuestionnaire) * 100}%"></div></div>
      </div>
      <div class="score-line">
        <div class="score-header"><span>${t("dashboardLabel")}</span><strong>${safeMultimodal.toFixed(2)}</strong></div>
        <div class="dual-track"><div class="score-fill dual-fill multimodal" style="width:${clamp01(safeMultimodal) * 100}%"></div></div>
      </div>
    </div>
  `;
}

function renderScoreComparison() {
  const record = state.selectedRecord;
  if (!record) {
    elements.scoreComparison.className = "empty-state";
    elements.scoreComparison.textContent = t("noRecordSelected");
    return;
  }
  elements.scoreComparison.className = "compare-grid";
  elements.scoreComparison.innerHTML = `
    <div class="compare-legend">
      <span><span class="legend-dot questionnaire"></span>${t("questionnaireLabel")}</span>
      <span><span class="legend-dot multimodal"></span>${t("dashboardLabel")}</span>
    </div>
    ${DOMAINS.map((domain) => comparisonRow(localizedDomainLabel(domain), record.questionnaire[`${domain}_score`], record.multimodal.overall.scores[domain])).join("")}
  `;
}

function modalityCard(title, payload) {
  const available = payload?.available;
  const uploadReceived = payload?.features?.upload_received;
  const notes = payload?.notes || t("noDataModality");
  const statusText = available ? t("availableLabel") : uploadReceived ? t("uploadReceivedLabel") : t("notAvailableLabel");
  return `
    <div class="modality-card ${available ? "" : "unavailable"}">
      <h3>${title}</h3>
      <p class="detail-muted">${statusText}</p>
      <p>${notes}</p>
    </div>
  `;
}

function renderModalityBreakdown() {
  const record = state.selectedRecord;
  if (!record) {
    elements.modalityBreakdown.className = "empty-state";
    elements.modalityBreakdown.textContent = t("noRecordSelected");
    return;
  }
  elements.modalityBreakdown.className = "modality-grid";
  elements.modalityBreakdown.innerHTML = [
    modalityCard(localizedModalityLabel("text"), record.multimodal.text),
    modalityCard(localizedModalityLabel("audio"), record.multimodal.audio),
    modalityCard(localizedModalityLabel("image"), record.multimodal.image),
  ].join("");
}

function renderFeatureSnapshot() {
  const record = state.selectedRecord;
  if (!record) {
    elements.featureSnapshot.className = "empty-state";
    elements.featureSnapshot.textContent = t("noRecordSelected");
    return;
  }
  const featureCards = ["text", "audio", "image"]
    .filter((key) => record.multimodal[key]?.features)
    .map((key) => {
      const items = Object.entries(record.multimodal[key].features).map(([name, value]) => `<li>${name}: ${formatFeatureValue(value)}</li>`).join("");
      return `<div class="feature-card"><h3>${localizedModalityLabel(key)} ${t("featuresLabel")}</h3><ul class="feature-list">${items}</ul></div>`;
    });
  if (!featureCards.length) {
    elements.featureSnapshot.className = "empty-state";
    elements.featureSnapshot.textContent = t("noFeaturesLabel");
    return;
  }
  elements.featureSnapshot.className = "feature-grid";
  elements.featureSnapshot.innerHTML = featureCards.join("");
}

function renderPatientHistory() {
  const record = state.selectedRecord;
  const trajectory = getTrajectory(record);
  if (!record || !trajectory) {
    elements.patientHistory.className = "empty-state";
    elements.patientHistory.textContent = t("noRecordSelected");
    elements.domainTrajectory.className = "empty-state";
    elements.domainTrajectory.textContent = t("noRecordSelected");
    return;
  }

  if (trajectory.history_count < 2) {
    elements.patientHistory.className = "detail-stack";
    elements.patientHistory.innerHTML = `
      <div class="detail-card">
        <h3>${trajectoryStatusLabel(trajectory.status)}</h3>
        <p>${trajectory.summary}</p>
      </div>
    `;
  } else {
    const timelinePoints = trajectory.points.map((point) => ({
      label: point.created_at,
      count: Math.round(Number(point.overall_score || 0) * 100),
    }));
    const visitCards = trajectory.points.map((point) => `
      <div class="summary-tile">
        <div class="tile-top"><span>${formatShortDateLabel(point.created_at)}</span><strong>${Math.round(Number(point.overall_score || 0) * 100)}%</strong></div>
        <p class="detail-muted">${point.assessment_id} | ${localizedDomainLabel(point.strongest_domain)}</p>
      </div>
    `).join("");
    elements.patientHistory.className = "chart-stack";
    elements.patientHistory.innerHTML = `
      ${buildLineTrendSvg(timelinePoints)}
      <div class="tile-grid">${visitCards}</div>
    `;
  }

  const domainRows = DOMAINS.map((domain) => {
    const info = trajectory.domains?.[domain] || {};
    const delta = Number(info.change_from_baseline || 0);
    return {
      label: localizedDomainLabel(domain),
      value: Math.abs(delta),
      display: `${localizedTrajectoryStatus(info.direction || "stable")} | ${delta >= 0 ? "+" : ""}${delta.toFixed(2)}`,
    };
  });
  elements.domainTrajectory.className = "chart-stack";
  elements.domainTrajectory.innerHTML = `
    <div class="detail-card">
      <h3>${trajectoryStatusLabel(trajectory.status)}</h3>
      <p>${trajectory.summary}</p>
    </div>
    ${buildHorizontalMetricSvg(domainRows, "#ad4a21")}
  `;
}

function renderDetailPanels() {
  renderSelectedAssessment();
  renderScoreComparison();
  renderModalityBreakdown();
  renderFeatureSnapshot();
  renderPatientHistory();
}

function formatFeatureValue(value) {
  if (Array.isArray(value)) {
    return value.map((item) => formatFeatureValue(item)).join(", ");
  }
  if (value && typeof value === "object") {
    return `<pre>${JSON.stringify(value, null, 2)}</pre>`;
  }
  return String(value);
}

function renderExplanationSummary(features) {
  const explanations = features?.domain_explanations || {};
  const candidates = Object.entries(explanations)
    .filter(([, item]) => item?.available && Array.isArray(item?.top_contributors) && item.top_contributors.length)
    .sort((left, right) => {
      const leftScore = Math.abs(Number(left[1].predicted_value || 0) - Number(left[1].base_value || 0));
      const rightScore = Math.abs(Number(right[1].predicted_value || 0) - Number(right[1].base_value || 0));
      return rightScore - leftScore;
    });
  if (!candidates.length) return "";
  const [domain, explanation] = candidates[0];
  const items = explanation.top_contributors
    .slice(0, 3)
    .map((item) => `<li>${item.feature}: ${item.direction} risk (${Number(item.shap_value || 0).toFixed(3)})</li>`)
    .join("");
  return `
      <h3>${t("whyFlaggedLabel", { domain: localizedDomainLabel(domain) })}</h3>
      <p>${t("topModelContributorsLabel")}</p>
      <ul>${items}</ul>
  `;
}

function renderWorkspacePanels() {
  const record = state.draftRecord;
  if (!record) {
    elements.workspacePrediction.className = "empty-state";
    elements.workspacePrediction.textContent = t("workspacePredictionEmpty");
    elements.workspaceNlp.className = "empty-state";
    elements.workspaceNlp.textContent = t("workspaceNlpEmpty");
    elements.workspaceReadiness.className = "empty-state";
    elements.workspaceReadiness.textContent = t("workspaceReadinessEmpty");
    return;
  }

  elements.workspacePrediction.className = "detail-stack";
  elements.workspacePrediction.innerHTML = `
    <div class="detail-card">
      <div class="detail-inline"><h3>${record.profile.full_name || "Unnamed user"}</h3><strong>${record.assessment_id}</strong></div>
      <p class="detail-muted">${state.draftRecord ? `${t("livePreviewLabel")}${state.draftPreviewLoading ? " | refreshing..." : ""}` : `${t("savedAtLabel")} ${formatDate(record.created_at)}`}</p>
      ${DOMAINS.map((domain) => scoreLine(`${localizedDomainLabel(domain)} Score`, record.multimodal.overall.scores[domain])).join("")}
      <p class="detail-muted">${record.multimodal.recommendation}</p>
    </div>
  `;

  const features = record.multimodal.text?.features || {};
  const audioStatus = modalityReadinessMessage("audio", record.multimodal.audio, getCurrentAudioFile());
  const imageStatus = modalityReadinessMessage("image", record.multimodal.image, getCurrentImageFile());
  elements.workspaceNlp.className = "detail-stack";
  elements.workspaceNlp.innerHTML = `
    <div class="detail-card">
      <h3>${t("sentimentLabel")}</h3>
      <p>${features.sentiment_label || "unknown"} via ${features.sentiment_model || "backend heuristic"}</p>
      <h3>${t("emotionLabel")}</h3>
      <p>${features.dominant_emotion || "neutral"} via ${features.emotion_model || "backend heuristic"}</p>
      <h3>${t("safetyLanguageLabel")}</h3>
      <p>${features.self_harm_keyword_detected ? `Self-harm keywords detected: ${(features.self_harm_keyword_matches || []).join(", ")}` : "No self-harm keywords detected"}</p>
      <h3>${t("transformerLabel")}</h3>
      <p>${features.transformer_model || "unavailable"}</p>
      ${renderExplanationSummary(features)}
      <h3>${t("audioModalityLabel")}</h3>
      <p>${audioStatus.text}</p>
      <h3>${t("imageModalityLabel")}</h3>
      <p>${imageStatus.text}</p>
    </div>
  `;

  const readinessChecks = [
    { label: "Consent", ready: Boolean(elements.consent.checked) },
    { label: "Candidate name", ready: Boolean(elements.fullName.value.trim()) },
    { label: "Village", ready: Boolean(elements.village.value.trim()) },
    { label: "Assessor", ready: Boolean(elements.assessor.value.trim()) },
    { label: "Narrative text", ready: Boolean(elements.textNarrative.value.trim()) },
    { label: "Audio upload", ready: audioStatus.ready, detail: audioStatus.text, tone: audioStatus.tone },
    { label: "Image upload", ready: imageStatus.ready, detail: imageStatus.text, tone: imageStatus.tone },
  ];
  const scoringChecks = readinessChecks.filter((item) => {
    if (!item.label.endsWith("upload")) return true;
    return item.label.startsWith("Audio") ? Boolean(getCurrentAudioFile()) : Boolean(getCurrentImageFile());
  });
  const readinessScore = scoringChecks.length ? scoringChecks.filter((item) => item.ready).length / scoringChecks.length : 0;
  elements.workspaceReadiness.className = "detail-stack";
  elements.workspaceReadiness.innerHTML = `
    <div class="detail-card">
      <h3>${t("readinessScoreLabel")}</h3>
      ${scoreLine(t("completionLabel"), readinessScore)}
      ${readinessChecks.map((item) => {
        const statusLabel = item.tone === "error"
          ? t("needsAttention")
          : item.tone === "success"
            ? t("readyLabel")
            : t("infoLabel");
        return `<p class="detail-muted">${statusLabel}: ${item.detail || item.label}</p>`;
      }).join("")}
    </div>
  `;
}

function renderDashboard() {
  renderOverview();
  renderRiskDistribution();
  renderSubmissionTrend();
  renderModelStatistics();
  renderNlpSignalSummary();
  renderRiskHotspots();
  renderNlpTrends();
  renderTrajectoryModel();
  renderTable();
  renderDetailPanels();
  renderWorkspacePanels();
}

function switchView(viewId) {
  elements.tabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewId);
  });
  elements.viewSections.forEach((section) => {
    const isActive = section.id === viewId;
    section.classList.toggle("is-hidden", !isActive);
    section.classList.toggle("section-live", false);
    if (isActive) {
      void section.offsetWidth;
      section.classList.add("section-live");
    }
  });
}

function activateTab(viewId) {
  const matchingTab = elements.tabButtons.find((button) => button.dataset.view === viewId);
  if (matchingTab) {
    matchingTab.click();
    return;
  }
  switchView(viewId);
}

function jumpToDashboardArea(viewId, panelId = "") {
  activateTab(viewId);
  const targetId = panelId || viewId;
  window.requestAnimationFrame(() => {
    const target = document.getElementById(targetId) || document.getElementById(viewId);
    if (!target) return;
    target.scrollIntoView({ behavior: "smooth", block: "start" });
    if (typeof target.focus === "function") {
      target.setAttribute("tabindex", "-1");
      target.focus({ preventScroll: true });
    }
  });
}

function resetAssessmentForm() {
  cancelDraftPreview();
  state.draftPreviewRequestId += 1;
  elements.assessmentForm.reset();
  QUESTION_BANK.forEach((question) => {
    const radio = document.querySelector(`input[name="${question.id}"][value="0"]`);
    if (radio) radio.checked = true;
  });
  clearSpeechRecording();
  clearCapturedPhoto();
  stopWebcam();
  clearUploadedMediaInputs();
  state.draftRecord = null;
  state.latestCreatedRecord = null;
  state.selectedRecord = null;
  state.draftPreviewLoading = false;
  updateCaptureUi();
  renderWorkspacePanels();
  setBanner(elements.workspaceStatus, t("workspacePredictionEmpty"), "neutral");
}

function adaptiveResponseOptionsFromLanguage(language = currentAdaptiveLanguage()) {
  return adaptiveResponseOptions(null, language);
}

function renderAdaptiveAnswerOptions() {
  if (!elements.adaptiveAnswerOptions) return;
  const currentValue = state.adaptiveSelectedAnswer ?? "";
  const options = adaptiveResponseOptions();
  const cards = options.map((option, index) => {
    const card = document.createElement("label");
    card.className = "adaptive-choice-card";
    const input = document.createElement("input");
    input.type = "radio";
    input.name = "adaptiveAnswer";
    input.value = String(option.value);
    input.checked = String(currentValue) === String(option.value);
    input.disabled = !state.adaptiveSessionStarted || !state.adaptiveCurrentQuestion || state.adaptiveLoading;
    input.addEventListener("change", () => {
      state.adaptiveSelectedAnswer = input.value;
      elements.adaptiveAnswerOptions.querySelectorAll(".adaptive-choice-card").forEach((node) => {
        const radio = node.querySelector('input[type="radio"]');
        node.classList.toggle("is-selected", Boolean(radio?.checked));
      });
    });

    const badge = document.createElement("span");
    badge.className = "adaptive-choice-badge";
    badge.textContent = String(index + 1);

    const text = document.createElement("span");
    text.className = "adaptive-choice-text";
    text.textContent = option.label;

    card.classList.toggle("is-selected", input.checked);
    card.append(input, badge, text);
    return card;
  });
  elements.adaptiveAnswerOptions.replaceChildren(...cards);
}

function renderAdaptiveStatus(message, tone = "neutral") {
  setBanner(elements.adaptiveStatus, message, tone);
}

function renderAdaptiveMetaPills(items) {
  if (!elements.adaptiveQuestionMeta) return;
  if (!items.length) {
    elements.adaptiveQuestionMeta.textContent = "";
    return;
  }
  const nodes = items.map((item) => {
    const pill = document.createElement("span");
    pill.className = "adaptive-meta-pill";
    const label = document.createElement("strong");
    label.textContent = item.label;
    pill.append(label);
    pill.append(` ${item.value}`);
    return pill;
  });
  elements.adaptiveQuestionMeta.replaceChildren(...nodes);
}

function adaptiveLogistic(value) {
  const exponent = Math.max(Math.min(-Number(value), 60), -60);
  return 1 / (1 + Math.exp(exponent));
}

function adaptiveQuestionParameters(question, index) {
  let discrimination = 1.0 + (0.15 * (index % 4));
  if (["depression", "anxiety", "stress"].includes(question.domain)) {
    discrimination += 0.1;
  }
  let difficulty = ADAPTIVE_SECTION_BASE_DIFFICULTY[question.section] || 0.0;
  difficulty += 0.12 * (index % 3);
  const override = ADAPTIVE_ITEM_OVERRIDES[question.id] || {};
  if (override.a !== undefined && override.a !== null) {
    discrimination = Number(override.a);
  }
  if (override.b !== undefined && override.b !== null) {
    difficulty = Number(override.b);
  }
  return {
    a: Number(discrimination.toFixed(3)),
    b: Number(difficulty.toFixed(3)),
  };
}

function adaptiveResponseCategoryProbabilities(theta, discrimination, difficulty) {
  const thresholds = ADAPTIVE_RESPONSE_THRESHOLDS.map((offset) => Number(difficulty) + Number(offset));
  const cumulative = [1.0];
  thresholds.forEach((threshold) => {
    cumulative.push(adaptiveLogistic(Number(discrimination) * (Number(theta) - threshold)));
  });
  cumulative.push(0.0);
  const probabilities = [];
  for (let index = 0; index < cumulative.length - 1; index += 1) {
    probabilities.push(Math.max(cumulative[index] - cumulative[index + 1], 1e-9));
  }
  const total = probabilities.reduce((sum, value) => sum + value, 0);
  if (total <= 0) {
    return [0.25, 0.25, 0.25, 0.25];
  }
  return probabilities.map((value) => value / total);
}

function adaptiveThetaLogPosterior(theta, responses) {
  let logLikelihood = 0;
  QUESTION_BANK.forEach((question, index) => {
    const value = responses[question.id];
    if (value === undefined || value === null) {
      return;
    }
    const params = adaptiveQuestionParameters(question, index);
    const category = Math.max(0, Math.min(3, Number.parseInt(value, 10)));
    const probabilities = adaptiveResponseCategoryProbabilities(theta, params.a, params.b);
    logLikelihood += Math.log(probabilities[category] || 1e-9);
  });
  const priorScale = ADAPTIVE_THETA_PRIOR_SD;
  const logPrior = -0.5 * ((Number(theta) / priorScale) ** 2);
  return logLikelihood + logPrior;
}

function adaptiveEstimateTheta(responses) {
  let bestTheta = 0;
  let bestScore = Number.NEGATIVE_INFINITY;
  for (let theta = ADAPTIVE_THETA_GRID_MIN; theta <= ADAPTIVE_THETA_GRID_MAX + 1e-9; theta += ADAPTIVE_THETA_GRID_STEP) {
    const score = adaptiveThetaLogPosterior(theta, responses);
    if (score > bestScore) {
      bestScore = score;
      bestTheta = theta;
    }
  }

  const refinementStart = Math.max(ADAPTIVE_THETA_GRID_MIN, bestTheta - ADAPTIVE_THETA_GRID_STEP);
  const refinementEnd = Math.min(ADAPTIVE_THETA_GRID_MAX, bestTheta + ADAPTIVE_THETA_GRID_STEP);
  for (let theta = refinementStart; theta <= refinementEnd + 1e-9; theta += ADAPTIVE_THETA_GRID_STEP / 10) {
    const score = adaptiveThetaLogPosterior(theta, responses);
    if (score > bestScore) {
      bestScore = score;
      bestTheta = theta;
    }
  }

  return Math.max(Math.min(bestTheta, ADAPTIVE_THETA_GRID_MAX), ADAPTIVE_THETA_GRID_MIN);
}

function adaptiveDomainCoverageBonus(domain, answeredCounts, balanceWeight = ADAPTIVE_DOMAIN_BALANCE_WEIGHT) {
  const targetCount = Math.max(1, QUESTION_BANK.length / Math.max(DOMAINS.length, 1));
  const answeredCount = Number(answeredCounts[domain] || 0);
  const coverageGap = Math.max(0, targetCount - answeredCount) / targetCount;
  return 1 + (Number(balanceWeight) * coverageGap);
}

function buildLocalAdaptiveQuestionBank(responses, language = currentLanguage()) {
  const answered = { ...responses };
  const answeredIds = new Set(Object.keys(answered).filter((questionId) => answered[questionId] !== undefined && answered[questionId] !== null));
  const theta = adaptiveEstimateTheta(answered);
  const tuning = {
    info_threshold: ADAPTIVE_INFO_THRESHOLD,
    coverage_weight: ADAPTIVE_DOMAIN_BALANCE_WEIGHT,
    defaults: {
      info_threshold: ADAPTIVE_INFO_THRESHOLD,
      coverage_weight: ADAPTIVE_DOMAIN_BALANCE_WEIGHT,
    },
    source: "browser-fallback",
  };
  const answeredCounts = Object.fromEntries(DOMAINS.map((domain) => [domain, 0]));
  QUESTION_BANK.forEach((question) => {
    if (answeredIds.has(question.id)) {
      answeredCounts[question.domain] += 1;
    }
  });

  const scoredQuestions = [];
  QUESTION_BANK.forEach((question, index) => {
    if (answeredIds.has(question.id)) {
      return;
    }
    const params = adaptiveQuestionParameters(question, index);
    const probability = 1 / (1 + Math.exp(Math.max(Math.min(-params.a * (theta - params.b), 60), -60)));
    const information = (params.a ** 2) * probability * (1 - probability);
    const coverageBonus = adaptiveDomainCoverageBonus(question.domain, answeredCounts, tuning.coverage_weight);
    const selectionScore = information * coverageBonus;
    scoredQuestions.push({
      ...question,
      prompt_localized: language === "English"
        ? question.prompt
        : QUESTION_TRANSLATIONS[question.id]?.[language] || question.prompt,
      section_label: language === "English"
        ? question.section
        : SECTION_TRANSLATIONS[question.section]?.[language] || question.section,
      language,
      irt: {
        discrimination: params.a,
        difficulty: params.b,
        information: Number(information.toFixed(6)),
      },
      adaptive: {
        selection_score: Number(selectionScore.toFixed(6)),
        coverage_bonus: Number(coverageBonus.toFixed(6)),
        answered_in_domain: answeredCounts[question.domain],
      },
    });
  });

  scoredQuestions.sort((left, right) => {
    if ((right.adaptive?.selection_score || 0) !== (left.adaptive?.selection_score || 0)) {
      return (right.adaptive?.selection_score || 0) - (left.adaptive?.selection_score || 0);
    }
    return (right.irt?.information || 0) - (left.irt?.information || 0);
  });

  const nextQuestion = scoredQuestions[0] || null;
  const maxInformation = scoredQuestions.length
    ? Math.max(...scoredQuestions.map((item) => item.irt?.information || 0))
    : 0;
  const selectedInformation = nextQuestion?.irt?.information || 0;
  const shouldStop = (
    answeredIds.size >= ADAPTIVE_MAX_ITEMS
    || (answeredIds.size >= ADAPTIVE_MIN_ITEMS && maxInformation < tuning.info_threshold)
    || !nextQuestion
  );

  return {
    theta: Number(theta.toFixed(6)),
    answered_count: answeredIds.size,
    remaining_count: scoredQuestions.length,
    next_question: nextQuestion,
    should_stop: shouldStop,
    max_information: Number(maxInformation.toFixed(6)),
    selected_information: Number(selectedInformation.toFixed(6)),
    tuning,
    response_options: adaptiveResponseOptionsFromLanguage(language),
    choose_one_label: adaptiveText("chooseOne", {}, language),
    language,
  };
}

function renderAdaptiveQuestion() {
  renderAdaptiveAnswerOptions();

  if (state.adaptiveCompleted && state.adaptiveLastRecord) {
    elements.adaptiveQuestionPrompt.textContent = adaptiveText("completedPrompt", {
      id: state.adaptiveLastRecord.assessment_id,
    });
    elements.adaptiveQuestionMeta.textContent = adaptiveText("completedMeta");
    elements.adaptiveNextBtn.disabled = true;
    elements.adaptiveStartBtn.disabled = false;
    elements.adaptiveResetBtn.disabled = false;
    return;
  }

  if (state.adaptiveLoading) {
    elements.adaptiveQuestionPrompt.textContent = t("adaptiveStatusLoading");
    elements.adaptiveQuestionMeta.textContent = adaptiveText("loadingMeta");
    elements.adaptiveNextBtn.disabled = true;
    elements.adaptiveStartBtn.disabled = true;
    elements.adaptiveResetBtn.disabled = false;
    return;
  }

  if (!state.adaptiveSessionStarted || !state.adaptiveCurrentQuestion) {
    elements.adaptiveQuestionPrompt.textContent = t("adaptiveQuestionHint");
    elements.adaptiveQuestionMeta.textContent = t("adaptiveStatusIdle");
    elements.adaptiveNextBtn.disabled = true;
    elements.adaptiveStartBtn.disabled = false;
    elements.adaptiveResetBtn.disabled = false;
    return;
  }

  const question = state.adaptiveCurrentQuestion;
  const adaptiveMeta = question.adaptive || {};
  const progressMeta = state.adaptiveProgress || {};
  const tuning = progressMeta.tuning || {};
  elements.adaptiveQuestionPrompt.textContent = questionPrompt(question, currentAdaptiveLanguage());
  const sectionLabel = question.language === currentAdaptiveLanguage() && question.section_label
    ? question.section_label
    : adaptiveSectionLabel(question.section, currentAdaptiveLanguage());
  const remainingLabel = adaptiveText("remaining");
  const irtInfoLabel = adaptiveText("irtInfo");
  const difficultyLabel = adaptiveText("difficulty");
  const selectionScoreLabel = adaptiveText("selectionScore");
  const coverageBonusLabel = adaptiveText("coverageBonus");
  const stopThresholdLabel = adaptiveText("stopThreshold");
  const balanceWeightLabel = adaptiveText("balanceWeight");
  renderAdaptiveMetaPills([
    { label: adaptiveText("section"), value: sectionLabel },
    { label: irtInfoLabel, value: (question.irt?.information || 0).toFixed(3) },
    { label: difficultyLabel, value: (question.irt?.difficulty || 0).toFixed(2) },
    { label: selectionScoreLabel, value: (adaptiveMeta.selection_score ?? question.irt?.information ?? 0).toFixed(3) },
    { label: coverageBonusLabel, value: (adaptiveMeta.coverage_bonus ?? 1).toFixed(2) },
    { label: remainingLabel, value: String(progressMeta.remaining_count ?? 0) },
    ...(tuning.info_threshold !== undefined ? [{ label: stopThresholdLabel, value: Number(tuning.info_threshold).toFixed(3) }] : []),
    ...(tuning.coverage_weight !== undefined ? [{ label: balanceWeightLabel, value: Number(tuning.coverage_weight).toFixed(3) }] : []),
  ]);
  elements.adaptiveNextBtn.disabled = false;
  elements.adaptiveStartBtn.disabled = true;
  elements.adaptiveResetBtn.disabled = false;
}

function resetAdaptiveState() {
  state.adaptiveResponses = {};
  state.adaptiveSelectedAnswer = "";
  state.adaptiveCurrentQuestion = null;
  state.adaptiveProgress = null;
  state.adaptiveCompleted = false;
  state.adaptiveLastRecord = null;
  state.adaptiveLoading = false;
  state.adaptiveRequestId += 1;
  state.adaptiveSessionStarted = false;
  if (elements.adaptiveForm) {
    elements.adaptiveForm.reset();
  }
  renderAdaptiveAnswerOptions();
  renderAdaptiveStatus(t("adaptiveStatusIdle"));
  renderAdaptiveQuestion();
}

function buildAdaptivePayload() {
  const questionnaireResponses = { ...state.adaptiveResponses };
  const questionnaire = scoreQuestionnaire(questionnaireResponses);
  return {
    profile: {
      full_name: elements.adaptiveFullName.value.trim(),
      age: Number(elements.adaptiveAge.value || 0),
      gender: elements.adaptiveGender.value,
      village: elements.adaptiveVillage.value.trim(),
      phone: "",
      assessor: elements.adaptiveAssessor.value.trim(),
      language: normalizeLanguage(elements.adaptiveLanguage.value || elements.language.value || currentLanguage()),
      consent_received: elements.adaptiveConsent.checked,
      record_origin: "test",
    },
    questionnaire,
    text_input: elements.adaptiveTextNarrative.value,
    audio_file: getCurrentAudioFile(),
    image_file: getCurrentImageFile(),
    audio_metadata: buildUploadMetadata(getCurrentAudioFile()),
    image_metadata: buildUploadMetadata(getCurrentImageFile()),
  };
}

async function saveAdaptiveAssessmentToApi(payload) {
  if (!payload.profile.full_name || !payload.profile.village || !payload.profile.assessor) {
    renderAdaptiveStatus(adaptiveText("profileMissing"), "error");
    return null;
  }
  if (!payload.profile.consent_received) {
    renderAdaptiveStatus(adaptiveText("consentMissing"), "error");
    return null;
  }

  const adaptiveRecordBanner = (record, offline = false) => {
    state.adaptiveLastRecord = record;
    state.adaptiveCompleted = true;
    state.adaptiveLoading = false;
    state.adaptiveSessionStarted = false;
    state.adaptiveCurrentQuestion = null;
    state.adaptiveProgress = null;
    renderAdaptiveQuestion();
    renderAdaptiveStatus(adaptiveText("completedPrompt", { id: record.assessment_id }), "success");
    setActiveResults([record], {
      focusLatest: true,
      bannerMessage: `${t("analyticsShowing")} ${record.assessment_id}.`,
      bannerTone: "success",
    });
    switchView("analyticsView");
    return record;
  };

  try {
    renderAdaptiveStatus(t("saveInProgress"), "neutral");
    const response = await fetch("/api/assessments", {
      method: "POST",
      body: buildAssessmentFormData(payload),
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const savedRecord = normalizeRecord(await response.json());
    await persistLocalRecord(savedRecord);
    return adaptiveRecordBanner(savedRecord, false);
  } catch (error) {
    console.error("Adaptive assessment save failed", error);
    const localRecord = buildOfflineAssessmentRecord(payload);
    await queueAssessmentForSync(payload, localRecord);
    await persistLocalRecord(localRecord);
    return adaptiveRecordBanner(localRecord, true);
  }
}

async function fetchAdaptiveSession(responses) {
  const requestId = state.adaptiveRequestId + 1;
  state.adaptiveRequestId = requestId;
  state.adaptiveLoading = true;
  renderAdaptiveStatus(t("adaptiveStatusLoading"), "neutral");
  renderAdaptiveQuestion();
  try {
    const progress = await fetchAdaptiveQuestionState(responses, currentAdaptiveLanguage());
    if (requestId !== state.adaptiveRequestId) {
      return null;
    }
    state.adaptiveProgress = progress;
    state.adaptiveCurrentQuestion = progress.next_question || null;
    state.adaptiveLoading = false;
    state.adaptiveSessionStarted = true;
    renderAdaptiveQuestion();
    if (progress.should_stop || !progress.next_question) {
      renderAdaptiveStatus(t("adaptiveStatusComplete"), "success");
      const payload = buildAdaptivePayload();
      const record = await saveAdaptiveAssessmentToApi(payload);
      return record;
    }
    renderAdaptiveStatus(t("adaptiveStatusReady"), "success");
    return progress;
  } catch (error) {
    if (requestId !== state.adaptiveRequestId) {
      return null;
    }
    console.warn("Adaptive session fetch failed; using browser fallback.", error);
    try {
      const progress = buildLocalAdaptiveQuestionBank(responses, currentAdaptiveLanguage());
      if (requestId !== state.adaptiveRequestId) {
        return null;
      }
      state.adaptiveProgress = progress;
      state.adaptiveCurrentQuestion = progress.next_question || null;
      state.adaptiveLoading = false;
      state.adaptiveSessionStarted = true;
      renderAdaptiveQuestion();
      if (progress.should_stop || !progress.next_question) {
        renderAdaptiveStatus(t("adaptiveStatusComplete"), "success");
        const payload = buildAdaptivePayload();
        const record = await saveAdaptiveAssessmentToApi(payload);
        return record;
      }
      renderAdaptiveStatus(adaptiveText("fallbackNotice"), "neutral");
      return progress;
    } catch (fallbackError) {
      if (requestId !== state.adaptiveRequestId) {
        return null;
      }
      console.error("Adaptive browser fallback failed", fallbackError);
      state.adaptiveLoading = false;
      state.adaptiveProgress = null;
      state.adaptiveCurrentQuestion = null;
      state.adaptiveSessionStarted = false;
      renderAdaptiveQuestion();
      renderAdaptiveStatus(t("adaptiveStatusError"), "error");
      return null;
    }
  }
}

async function startAdaptiveSession() {
  state.adaptiveResponses = {};
  state.adaptiveCompleted = false;
  state.adaptiveLastRecord = null;
  state.adaptiveSelectedAnswer = "";
  renderAdaptiveAnswerOptions();
  await fetchAdaptiveSession({});
}

async function submitAdaptiveAnswer() {
  if (!state.adaptiveSessionStarted || !state.adaptiveCurrentQuestion) {
    renderAdaptiveStatus(t("adaptiveQuestionHint"), "neutral");
    return;
  }
  const selected = elements.adaptiveAnswerOptions?.querySelector('input[type="radio"]:checked');
  const answer = selected?.value ?? "";
  if (answer === "") {
    renderAdaptiveStatus(adaptiveText("answerRequired"), "error");
    return;
  }

  const updatedResponses = { ...state.adaptiveResponses, [state.adaptiveCurrentQuestion.id]: Number(answer) };
  state.adaptiveResponses = updatedResponses;
  state.adaptiveSelectedAnswer = "";
  renderAdaptiveAnswerOptions();
  await fetchAdaptiveSession(updatedResponses);
}

async function submitAssessment(event) {
  event.preventDefault();
  if (!elements.consent.checked) {
    setBanner(elements.workspaceStatus, "Please confirm consent before saving the assessment.", "error");
    return;
  }
  const payload = buildAssessmentPayload();
  await saveAssessmentToApi(payload);
}

async function saveAssessmentToApi(payload) {
  if (!state.networkOnline) {
    const localRecord = buildOfflineAssessmentRecord(payload);
    await queueAssessmentForSync(payload, localRecord);
    state.latestCreatedRecord = localRecord;
    state.draftRecord = null;
    renderWorkspacePanels();
    setActiveResults([localRecord], {
      focusLatest: true,
      bannerMessage: `${t("assessmentIdLabel")} ${localRecord.assessment_id} ${t("savedOfflineQueuedShortLabel")}`,
      bannerTone: "success",
    });
    setBanner(elements.workspaceStatus, t("savedOfflineQueuedLabel"), "success");
    switchView("analyticsView");
    return;
  }
  try {
    setBanner(elements.workspaceStatus, t("saveInProgress"), "neutral");
    const response = await fetch("/api/assessments", {
      method: "POST",
      body: buildAssessmentFormData(payload),
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const savedRecord = normalizeRecord(await response.json());
    await persistLocalRecord(savedRecord);
    state.latestCreatedRecord = savedRecord;
    state.draftRecord = null;
    renderWorkspacePanels();
    setActiveResults([savedRecord], {
      focusLatest: true,
      bannerMessage: `${t("analyticsShowing")} ${savedRecord.assessment_id}.`,
      bannerTone: "success",
    });
    setBanner(elements.workspaceStatus, `${t("assessmentIdLabel")} ${savedRecord.assessment_id} ${t("savedMessage")}`, "success");
    switchView("analyticsView");
  } catch (error) {
    console.error("Assessment save failed", error);
    const localRecord = buildOfflineAssessmentRecord(payload);
    await queueAssessmentForSync(payload, localRecord);
    state.latestCreatedRecord = localRecord;
    state.draftRecord = null;
    renderWorkspacePanels();
    setActiveResults([localRecord], {
      focusLatest: true,
      bannerMessage: `${t("assessmentIdLabel")} ${localRecord.assessment_id} saved offline after the API became unavailable.`,
      bannerTone: "success",
    });
    setBanner(elements.workspaceStatus, t("backendUnavailableSavedOfflineLabel"), "success");
    switchView("analyticsView");
  }
}

async function fetchDraftPreview(payload, requestId) {
  if (!state.networkOnline) {
    if (requestId !== state.draftPreviewRequestId) {
      return;
    }
    state.draftRecord = buildAssessmentRecordFromAnalysis(payload, buildOfflineMultimodal(payload), "Offline Preview");
    state.draftPreviewLoading = false;
    renderWorkspacePanels();
    return;
  }
  try {
    const response = await fetch("/api/preview", {
      method: "POST",
      body: buildAssessmentFormData(payload),
    });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const multimodal = await response.json();
    if (requestId !== state.draftPreviewRequestId) {
      return;
    }
    state.draftRecord = buildAssessmentRecordFromAnalysis(payload, multimodal);
    state.draftPreviewLoading = false;
    renderWorkspacePanels();
  } catch (error) {
    if (requestId !== state.draftPreviewRequestId) {
      return;
    }
    console.error("Draft preview failed", error);
    state.draftRecord = buildAssessmentRecordFromAnalysis(payload, buildOfflineMultimodal(payload), "Offline Preview");
    state.draftPreviewLoading = false;
    setBanner(elements.workspaceStatus, t("backendPreviewUnavailableLabel"), "neutral");
    renderWorkspacePanels();
  }
}

function updateDraftPreview() {
  const hasAnyInput = Boolean(
    elements.fullName.value.trim()
    || elements.village.value.trim()
    || elements.assessor.value.trim()
    || elements.textNarrative.value.trim()
    || elements.audioFile.files[0]
    || elements.imageFile.files[0]
  );
  if (state.draftPreviewTimer) {
    clearTimeout(state.draftPreviewTimer);
  }
  if (!hasAnyInput) {
    state.draftPreviewRequestId += 1;
    state.draftRecord = null;
    state.draftPreviewLoading = false;
    renderWorkspacePanels();
    return;
  }

  const payload = buildAssessmentPayload();
  const requestId = state.draftPreviewRequestId + 1;
  state.draftPreviewRequestId = requestId;
  state.draftRecord = null;
  state.draftPreviewLoading = true;
  renderWorkspacePanels();
  state.draftPreviewTimer = setTimeout(() => {
    fetchDraftPreview(payload, requestId);
  }, 250);
}

async function loadDefaultResults() {
  const offlineRecords = await loadOfflineRecords();
  if (offlineRecords.length) {
    setActiveResults(visibleUserRecords(offlineRecords), {
      focusLatest: true,
      bannerTone: "success",
    });
  }
  try {
    await loadApiResults(t("backendApiLabel"));
  } catch {
    setBanner(elements.statusBanner, t("loadRecordsFromApiFailedLabel"), "error");
  }
}

async function loadSampleResults() {
  try {
    const response = await fetch("/api/sample", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    loadResults(visibleUserRecords(await response.json()), t("sampleDatasetLabel"));
    return true;
  } catch {
    setBanner(elements.statusBanner, currentLanguage() === "Bengali" ? "স্যাম্পল ডেটাসেট লোড করা যায়নি।" : currentLanguage() === "Hindi" ? "सैंपल डाटासेट लोड नहीं हो सका।" : "Could not load the sample dataset.", "error");
    return false;
  }
}

function loadBrowserResults() {
  return loadApiResults(t("backendApiLabel"));
}

async function loadApiResults(sourceLabel, focusLatest = false) {
  try {
    const response = await fetch("/api/assessments", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const apiRecords = uniqueRecords(visibleUserRecords(await response.json()));
    for (const record of apiRecords) {
      await persistLocalRecord(record);
    }
    const merged = uniqueRecords([...visibleUserRecords(await loadOfflineRecords()), ...apiRecords]);
    loadResults(merged, sourceLabel, focusLatest);
    return merged.length > 0;
  } catch (error) {
    console.error("API load failed", error);
    const localRecords = visibleUserRecords(await loadOfflineRecords());
    if (localRecords.length) {
      loadResults(localRecords, t("localOfflineStorageLabel"), focusLatest);
      setBanner(elements.statusBanner, t("offlineRecordsLoadedLabel"), "neutral");
      return true;
    }
    setBanner(elements.statusBanner, t("loadRecordsFromApiGenericErrorLabel"), "error");
    return false;
  }
}

function exportFilteredResults() {
  if (!state.filteredResults.length) {
    setBanner(elements.statusBanner, t("noFilteredExportLabel"), "error");
    return;
  }
  const blob = new Blob([JSON.stringify(state.filteredResults, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "dashboard-filtered-records.json";
  link.click();
  URL.revokeObjectURL(url);
  setBanner(elements.statusBanner, t("exportedFilteredLabel", { count: state.filteredResults.length }), "success");
}

function fetchRecordById() {
  const query = normalizeText(elements.recordLookup.value).toUpperCase();
  if (!query) {
    setBanner(elements.statusBanner, t("fetchPrompt"), "error");
    return;
  }
  fetchRecordByIdFromApi(query);
}

async function fetchRecordByIdFromApi(assessmentId) {
  try {
    const response = await fetch(`/api/assessments/${encodeURIComponent(assessmentId)}`, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const record = normalizeRecord(await response.json());
    if (!visibleUserRecords([record]).length) {
      throw new Error("Record hidden from user view.");
    }
    const existingIndex = state.allResults.findIndex((item) => item.assessment_id === record.assessment_id);
    if (existingIndex >= 0) {
      state.allResults[existingIndex] = record;
    } else {
      state.allResults.unshift(record);
    }
    state.selectedRecord = record;
    populateFilterOptions();
    applyFilters();
    switchView("recordsView");
    renderDashboard();
    setBanner(elements.statusBanner, tf("fetchSuccess", { id: record.assessment_id }), "success");
  } catch (error) {
    console.error("Record fetch failed", error);
    const localRecord = state.allResults.find((item) => item.assessment_id === assessmentId);
    if (localRecord && visibleUserRecords([localRecord]).length) {
      state.selectedRecord = localRecord;
      switchView("recordsView");
      renderDashboard();
      setBanner(elements.statusBanner, t("loadedOfflineRecordLabel", { id: assessmentId }), "neutral");
      return;
    }
    setBanner(elements.statusBanner, t("fetchMissing"), "error");
  }
}

async function deleteSelectedAssessmentRecord(assessmentId) {
  const record = state.allResults.find((item) => item.assessment_id === assessmentId) || state.selectedRecord;
  if (!record || record.assessment_id !== assessmentId) {
    setBanner(elements.statusBanner, t("deleteRecordNotFound"), "error");
    return;
  }
  if (!window.confirm(t("deleteRecordConfirm"))) {
    return;
  }

  const removeFromState = async () => {
    await removeLocalRecord(assessmentId);
    try {
      await offlineStoreDelete(OFFLINE_PENDING_STORE, assessmentId);
    } catch (error) {
      console.warn("Could not remove pending queue entry", error);
    }
    await refreshPendingSyncCount();
    state.allResults = state.allResults.filter((item) => item.assessment_id !== assessmentId);
    state.filteredResults = state.filteredResults.filter((item) => item.assessment_id !== assessmentId);
    if (state.selectedRecord?.assessment_id === assessmentId) {
      state.selectedRecord = state.filteredResults[0] || null;
    }
    if (state.latestCreatedRecord?.assessment_id === assessmentId) {
      state.latestCreatedRecord = null;
    }
    populateFilterOptions();
    applyFilters();
  };

  if (!state.networkOnline) {
    if (record.sync_status !== "pending") {
      setBanner(elements.statusBanner, t("deleteRecordRequiresOnline"), "error");
      return;
    }
    try {
      await removeFromState();
      setBanner(elements.statusBanner, tf("deleteRecordSuccess", { id: assessmentId }), "success");
    } catch (error) {
      console.error("Local record deletion failed", error);
      setBanner(elements.statusBanner, tf("deleteRecordFailed", { id: assessmentId }), "error");
    }
    return;
  }

  try {
    if (record.sync_status !== "pending") {
      const response = await fetch(`/api/assessments/${encodeURIComponent(assessmentId)}`, { method: "DELETE" });
      if (!response.ok && response.status !== 404) {
        throw new Error(`HTTP ${response.status}`);
      }
    }
    await removeFromState();
    setBanner(elements.statusBanner, tf("deleteRecordSuccess", { id: assessmentId }), "success");
  } catch (error) {
    console.error("Assessment deletion failed", error);
    setBanner(elements.statusBanner, tf("deleteRecordFailed", { id: assessmentId }), "error");
  }
}

function loadInitialBrowserRecords() {
  state.allResults = [];
  state.filteredResults = [];
  state.selectedRecord = null;
  state.currentPage = 1;
  populateFilterOptions();
  renderDashboard();
  setBanner(elements.analysisStatusBanner, t("analyticsBannerDefault"), "neutral");
  setBanner(elements.statusBanner, t("recordsBannerDefault"), "neutral");
}

async function registerServiceWorker() {
  if (!("serviceWorker" in navigator)) {
    return;
  }
  try {
    await navigator.serviceWorker.register("/sw.js", { scope: "/" });
    state.serviceWorkerReady = true;
  } catch (error) {
    console.error("Service worker registration failed", error);
    state.serviceWorkerReady = false;
  }
  updateOfflineStatus();
}

async function initializeOfflineFirst() {
  await refreshPendingSyncCount();
  await registerServiceWorker();
  if (state.networkOnline) {
    await syncPendingAssessments();
  }
}

elements.tabButtons.forEach((button) => {
  button.addEventListener("click", () => switchView(button.dataset.view));
});

elements.assessmentForm.addEventListener("submit", submitAssessment);
elements.resetAssessmentBtn.addEventListener("click", () => {
  resetAssessmentForm();
  updateDraftPreview();
});
elements.adaptiveStartBtn.addEventListener("click", startAdaptiveSession);
elements.adaptiveNextBtn.addEventListener("click", submitAdaptiveAnswer);
elements.adaptiveResetBtn.addEventListener("click", resetAdaptiveState);
elements.startRecordingBtn.addEventListener("click", () => {
  startSpeechRecording();
});
elements.stopRecordingBtn.addEventListener("click", () => {
  stopSpeechRecording();
});
elements.clearRecordingBtn.addEventListener("click", () => {
  clearSpeechRecording();
});
elements.startCameraBtn.addEventListener("click", () => {
  startWebcam();
});
elements.capturePhotoBtn.addEventListener("click", () => {
  captureWebcamPhoto();
});
elements.stopCameraBtn.addEventListener("click", () => {
  stopWebcam();
});
elements.clearCapturedPhotoBtn.addEventListener("click", () => {
  clearCapturedPhoto();
});
elements.fetchRecordBtn.addEventListener("click", fetchRecordById);
elements.downloadSelectedPdfBtn.addEventListener("click", () => downloadPdfForRecord(state.selectedRecord));
[
  elements.fullName,
  elements.age,
  elements.gender,
  elements.village,
  elements.phone,
  elements.assessor,
  elements.language,
  elements.consent,
  elements.textNarrative,
  elements.audioFile,
  elements.imageFile,
].forEach((element) => {
  element.addEventListener("input", updateDraftPreview);
  element.addEventListener("change", updateDraftPreview);
});
elements.audioFile.addEventListener("change", () => {
  state.recordedAudioFile = null;
  updateCaptureUi();
});
elements.imageFile.addEventListener("change", () => {
  if (elements.capturedPhotoPreview.src) {
    URL.revokeObjectURL(elements.capturedPhotoPreview.src);
  }
  elements.capturedPhotoPreview.removeAttribute("src");
  state.capturedImageFile = null;
  updateCaptureUi();
});
elements.applyLanguageBtn.addEventListener("click", () => {
  applyDashboardLanguageSelection();
});
elements.language.addEventListener("change", () => {
  if (elements.dashboardLanguage) {
    elements.dashboardLanguage.value = elements.language.value;
  }
  applyDashboardLanguageSelection();
});
if (elements.adaptiveLanguage) {
  elements.adaptiveLanguage.addEventListener("change", () => {
    if (elements.language) {
      elements.language.value = elements.adaptiveLanguage.value;
    }
    if (elements.dashboardLanguage) {
      elements.dashboardLanguage.value = elements.adaptiveLanguage.value;
    }
    applyDashboardLanguageSelection();
  });
}
elements.prevPageBtn.addEventListener("click", () => {
  if (state.currentPage > 1) {
    state.currentPage -= 1;
    renderTable();
  }
});

elements.nextPageBtn.addEventListener("click", () => {
  const totalPages = Math.max(1, Math.ceil(state.filteredResults.length / 10));
  if (state.currentPage < totalPages) {
    state.currentPage += 1;
    renderTable();
  }
});

window.addEventListener("online", async () => {
  state.networkOnline = true;
  updateOfflineStatus();
  await syncPendingAssessments();
});

window.addEventListener("offline", () => {
  state.networkOnline = false;
  updateOfflineStatus();
  setBanner(elements.statusBanner, t("offlineModeActiveLabel"), "neutral");
});

async function bootstrapDashboard() {
  buildQuestionnaire();
  wireQuestionnaireEvents();
  applyLanguage();
  resetAdaptiveState();
  updateCaptureUi();
  resetAssessmentForm();
  loadInitialBrowserRecords();
  updateOfflineStatus();
  updateDraftPreview();
  const hasRecords = await loadApiResults(t("backendApiLabel"));
  if (!hasRecords) {
    await loadSampleResults();
  }
  await initializeOfflineFirst();
}

bootstrapDashboard();
