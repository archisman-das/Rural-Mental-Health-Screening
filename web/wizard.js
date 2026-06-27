const STORAGE_KEY = "mh-screening-wizard-state-v1";
const SAVED_RECORD_KEY = "mh-screening-wizard-last-record-v1";
const LANGUAGE_STORAGE_KEY = "mh-dashboard-language";

const QUESTIONNAIRE_ITEMS = [
  { id: "q1", label: "Little interest or pleasure in doing things" },
  { id: "q2", label: "Feeling down, depressed, or hopeless" },
  { id: "q3", label: "Trouble falling or staying asleep, or sleeping too much" },
  { id: "q4", label: "Feeling tired or having little energy" },
  { id: "q5", label: "Poor appetite or overeating" },
  { id: "q6", label: "Feeling bad about yourself or that you are a failure" },
  { id: "q7", label: "Trouble concentrating on things" },
  { id: "q8", label: "Moving or speaking so slowly or fidgety/restless" },
  { id: "q9", label: "Thoughts of being better off dead or self-harm" },
  { id: "q10", label: "Finding it hard to control worrying" },
  { id: "q11", label: "Feeling nervous, restless, or on edge" },
  { id: "q12", label: "Feeling afraid that something bad may happen" },
  { id: "q13", label: "Physical signs of anxiety such as racing heart, trembling, or sweating" },
  { id: "q14", label: "Avoiding people, places, or tasks because they increase anxiety" },
  { id: "q15", label: "Repeatedly needing reassurance before doing normal daily activities" },
  { id: "q16", label: "Daily responsibilities feeling too overwhelming" },
  { id: "q17", label: "Feeling irritable, tense, or unable to relax" },
  { id: "q18", label: "Stress affecting work, home life, or relationships" },
  { id: "q19", label: "Feeling under constant pressure with too little time or support" },
  { id: "q20", label: "Finding it hard to calm down or recover after a stressful event" },
  { id: "q21", label: "Stress showing up as headaches, body pain, or stomach discomfort" },
  { id: "q22", label: "Trouble falling asleep, staying asleep, or waking too early" },
  { id: "q23", label: "Poor sleep causing tiredness or sleepiness during the day" },
  { id: "q24", label: "An irregular sleep schedule that feels hard to control" },
  { id: "q25", label: "Waking up feeling unrefreshed even after enough hours in bed" },
  { id: "q26", label: "Worrying about sleep so much that it becomes harder to rest" },
  { id: "q27", label: "Sleep frequently interrupted by dreams, worry, pain, or restlessness" },
  { id: "q28", label: "Feeling emotionally or physically exhausted by responsibilities" },
  { id: "q29", label: "Feeling detached, numb, or less motivated toward duties" },
  { id: "q30", label: "Feeling unable to keep up with usual responsibilities" },
  { id: "q31", label: "Feeling frustrated, cynical, or emotionally distant from your work or caregiving role" },
  { id: "q32", label: "Feeling that your effort is high but the return, appreciation, or support is low" },
  { id: "q33", label: "Even after rest, still feeling drained and not fully recovered" },
  { id: "q34", label: "Feeling alone or isolated even when people are nearby" },
  { id: "q35", label: "Feeling that emotional support is lacking" },
  { id: "q36", label: "Finding it hard to feel connected to people around you" },
  { id: "q37", label: "Feeling that you do not fully belong in your family, workplace, or community" },
  { id: "q38", label: "Having few people you can openly share worries or emotions with" },
  { id: "q39", label: "Withdrawing from conversations, gatherings, or relationships more than before" },
  { id: "q40", label: "Using alcohol, tobacco, or substances to cope with stress or emotions" },
  { id: "q41", label: "Finding it difficult to reduce or control substance use" },
  { id: "q42", label: "Substance use affecting health, relationships, or responsibilities" },
  { id: "q43", label: "Strong urges or cravings that are difficult to ignore" },
  { id: "q44", label: "Needing more of the substance than before to get the same effect" },
  { id: "q45", label: "Feeling unwell, irritable, or restless when trying not to use the substance" },
];

const QUESTIONNAIRE_SEGMENTS = [
  { id: "Depression", itemIds: ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9"] },
  { id: "Anxiety", itemIds: ["q10", "q11", "q12", "q13", "q14", "q15"] },
  { id: "Stress", itemIds: ["q16", "q17", "q18", "q19", "q20", "q21"] },
  { id: "Sleep Disorder", itemIds: ["q22", "q23", "q24", "q25", "q26", "q27"] },
  { id: "Burnout", itemIds: ["q28", "q29", "q30", "q31", "q32", "q33"] },
  { id: "Loneliness", itemIds: ["q34", "q35", "q36", "q37", "q38", "q39"] },
  { id: "Substance Abuse", itemIds: ["q40", "q41", "q42", "q43", "q44", "q45"] },
];

const QUESTIONNAIRE_SEGMENT_LABELS = {
  English: {
    Depression: "Depression",
    Anxiety: "Anxiety",
    Stress: "Stress",
    "Sleep Disorder": "Sleep Disorder",
    Burnout: "Burnout",
    Loneliness: "Loneliness",
    "Substance Abuse": "Substance Abuse",
  },
  Hindi: {
    Depression: "अवसाद",
    Anxiety: "चिंता",
    Stress: "तनाव",
    "Sleep Disorder": "नींद की समस्या",
    Burnout: "बर्नआउट",
    Loneliness: "अकेलापन",
    "Substance Abuse": "पदार्थ दुरुपयोग",
  },
  Bengali: {
    Depression: "বিষণ্নতা",
    Anxiety: "উদ্বেগ",
    Stress: "স্ট্রেস",
    "Sleep Disorder": "ঘুমের সমস্যা",
    Burnout: "বার্নআউট",
    Loneliness: "একাকীত্ব",
    "Substance Abuse": "পদার্থের অপব্যবহার",
  },
};

const QUESTIONNAIRE_SEGMENT_SUMMARIES = {
  English: {
    Depression: "Mood, sleep, energy, guilt, and focus",
    Anxiety: "Worry, restlessness, fear, and avoidance",
    Stress: "Overload, tension, pressure, and stress impact",
    "Sleep Disorder": "Sleep onset, interruptions, and daytime fatigue",
    Burnout: "Exhaustion, detachment, and reduced capacity",
    Loneliness: "Isolation, belonging, and support",
    "Substance Abuse": "Use, control, cravings, and withdrawal",
  },
  Hindi: {
    Depression: "मूड, नींद, ऊर्जा, दोष और ध्यान",
    Anxiety: "चिंता, बेचैनी, डर और बचाव",
    Stress: "अधिक भार, तनाव, दबाव और असर",
    "Sleep Disorder": "नींद आने, टूटने और दिन की थकान",
    Burnout: "थकान, दूरी और क्षमता में कमी",
    Loneliness: "अकेलापन, अपनापन और समर्थन",
    "Substance Abuse": "उपयोग, नियंत्रण, लालसा और वापसी",
  },
  Bengali: {
    Depression: "মুড, ঘুম, শক্তি, অপরাধবোধ ও মনোযোগ",
    Anxiety: "দুশ্চিন্তা, অস্থিরতা, ভয় ও এড়িয়ে চলা",
    Stress: "অতিরিক্ত চাপ, টান, প্রেশার ও প্রভাব",
    "Sleep Disorder": "ঘুম আসা, ঘুম ভাঙা ও দিনের ক্লান্তি",
    Burnout: "ক্লান্তি, বিচ্ছিন্নতা ও সক্ষমতা হ্রাস",
    Loneliness: "বিচ্ছিন্নতা, আপনজনের অনুভূতি ও সহায়তা",
    "Substance Abuse": "ব্যবহার, নিয়ন্ত্রণ, তৃষ্ণা ও প্রত্যাহার",
  },
};

const RESPONSE_OPTIONS = [
  { label: "Not at all", value: 0 },
  { label: "Several days", value: 1 },
  { label: "More than half the days", value: 2 },
  { label: "Nearly every day", value: 3 },
];

const RESPONSE_OPTION_LABELS = {
  English: ["Not at all", "Several days", "More than half the days", "Nearly every day"],
  Hindi: ["बिलकुल नहीं", "कुछ दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
  Bengali: ["একদম না", "কয়েক দিন", "অর্ধেকের বেশি দিন", "প্রায় প্রতিদিন"],
};

const QUESTIONNAIRE_LABELS = {
  English: {
    q1: "Little interest or pleasure in doing things",
    q2: "Feeling down, depressed, or hopeless",
    q3: "Trouble falling or staying asleep, or sleeping too much",
    q4: "Feeling tired or having little energy",
    q5: "Poor appetite or overeating",
    q6: "Feeling bad about yourself or that you are a failure",
    q7: "Trouble concentrating on things",
    q8: "Moving or speaking so slowly or fidgety/restless",
    q9: "Thoughts of being better off dead or self-harm",
  },
  Hindi: {
    q1: "कामों में कम रुचि या आनंद",
    q2: "उदास, निराश या हताश महसूस करना",
    q3: "नींद आने या बनी रहने में कठिनाई, या बहुत ज़्यादा सोना",
    q4: "थका हुआ महसूस करना या ऊर्जा की कमी",
    q5: "भूख कम लगना या बहुत अधिक खाना",
    q6: "खुद को बुरा महसूस करना या असफल समझना",
    q7: "किसी बात पर ध्यान केंद्रित करने में कठिनाई",
    q8: "बहुत धीरे चलना/बोलना या बेचैनी महसूस करना",
    q9: "मर जाने या खुद को नुकसान पहुँचाने के विचार",
  },
  Bengali: {
    q1: "কাজে কম আগ্রহ বা আনন্দ বোধ করা",
    q2: "দুঃখী, বিষণ্ণ বা নিরাশ লাগা",
    q3: "ঘুম আসতে বা ঘুম ধরে রাখতে সমস্যা, অথবা খুব বেশি ঘুমানো",
    q4: "ক্লান্ত লাগা বা শক্তির অভাব",
    q5: "ক্ষুধা কমে যাওয়া বা অতিরিক্ত খাওয়া",
    q6: "নিজেকে খারাপ লাগা বা ব্যর্থ মনে হওয়া",
    q7: "কোনো কিছুর ওপর মনোযোগ দিতে সমস্যা",
    q8: "খুব ধীরে কথা বলা/চলা বা অস্থির লাগা",
    q9: "মরে যাওয়া বা নিজেকে আঘাত করার চিন্তা",
  },
};

const WIZARD_UI_TRANSLATIONS = {
  English: {
    screening: {
      heroEyebrow: "Step 1 of 3",
      heroTitle: "Rural Mental Health Detection",
      heroText: "Start the session by entering identity and consent details before moving to the questionnaire.",
      ready: "Screening step ready",
      first: "Identity and consent first",
      sideCard1Label: "screening card",
      sideCard2Label: "linked steps next",
      sideCard3Label: "final insights page",
      languageLabel: "Preferred language",
      applyLanguage: "Apply Language",
      languageStatus: "Preferred language is ready to apply.",
      profileTitle: "Candidate Profile",
      fullName: "Full name",
      age: "Age",
      gender: "Gender",
      village: "Village / Local area",
      district: "District",
      block: "Block / Subdivision",
      occupation: "Occupation",
      phone: "Phone / reference number",
      assessor: "Assessor name",
      consent: "Consent received for screening",
      next: "Next",
      placeholders: {
        fullName: "Enter full name",
        age: "Enter age in years",
        village: "Village or locality",
        district: "District name",
        block: "Block or subdivision",
        occupation: "Current occupation",
        phone: "Optional contact",
        assessor: "Health worker or counselor",
      },
      visual: {
        questionnaire: "Questionnaire",
        questionnaireText: "Structured symptom signals",
        questionnaireBody: "Page 2 opens on its own screen after the screening card is complete.",
        uploads: "Uploads",
        uploadsText: "Text, audio, video",
        uploadsBody: "Page 3 gathers the metadata and uploads.",
        flow: "Wizard flow",
        flowText: "Next and Previous",
        flowBody: "The buttons move between separate pages instead of one long scroll.",
        path: "Live screening path",
        pathStatus: "stepwise",
      },
    },
    questionnaire: {
      headerEyebrow: "Step 2 of 3",
      headerTitle: "Questionnaire",
      headerText: "Rate how often each symptom appeared in the last two weeks.",
      segmentIntro: "Questions are grouped by symptom area to make screening faster and easier to follow.",
      segmentTitles: {
        mood: "Mood and self-worth",
        body: "Sleep, energy, and body changes",
        thinking: "Thinking, focus, and safety",
      },
      segmentSummaries: {
        mood: "Interest, mood, and self-view",
        body: "Sleep pattern, tiredness, and appetite",
        thinking: "Concentration, movement, and safety",
      },
      validatedTitle: "Validated instruments",
      validatedText: "Tap PHQ-9 to open the full screening details.",
      aboutButton: "About PHQ-9",
      loadingInstruments: "Loading validated instrument buttons...",
      prev: "Previous",
      next: "Next",
    },
    insights: {
      headerEyebrow: "Step 3 of 3",
      headerTitle: "Upload Metadata",
      headerText: "Add narrative and uploads before saving the final record.",
      formTitle: "Free Text and Upload Metadata",
      narrativeLabel: "Describe how the person has been feeling",
      narrativePlaceholder: "Example: I have been feeling tired, disconnected, anxious, and unable to sleep well.",
      speechTitle: "Guided Speech Recording",
      speechTopic: "Topic: Describe your last few days, your sleep, stress, and how connected you feel to people around you.",
      speechStatus: "Use the record buttons on your device or attach a sample below.",
      startRecording: "Start Recording",
      stopRecording: "Stop Recording",
      clearRecording: "Clear Recording",
      recordingReady: "Speech recording ready",
      recordingProgress: "Recording in progress...",
      recordingMissing: "No speech recording captured yet.",
      voiceSample: "Voice sample",
      passiveTitle: "Additional Input",
      passiveTopic: "Upload a short front-camera video or related note if you want to include extra context.",
      passiveLabel: "Video or note",
      passiveStatus: "No additional input captured yet.",
      liveFaceTitle: "Live Face Capture",
      liveFaceTopic: "Capture one clear front-facing photo from the webcam for live facial-cue analysis.",
      faceLabel: "Face image",
      startCamera: "Open Camera",
      capturePhoto: "Capture Photo",
      stopCamera: "Close Camera",
      clearPhoto: "Clear Photo",
      cameraOpen: "Camera is open. Capture a clear front-facing photo.",
      photoReady: "Captured photo ready",
      photoMissing: "No live photo captured yet.",
      liveInsightsTitle: "Upload Metadata",
      liveInsightsText: "Add narrative and uploads before saving the final record.",
      saveStatus: "Complete the assessment and save it to generate the result.",
      predictionTitle: "Live Prediction Preview",
      predictionText: "Combined questionnaire and narrative preview before save",
      nlpTitle: "Live NLP Insights",
      nlpText: "Sentiment, emotions, and safety indicators from the narrative text",
      readinessTitle: "Intake Readiness",
      readinessText: "Checks whether the record is ready to save and analyze",
      prev: "Previous",
      save: "Save Assessment",
    },
    summary: {
      profile: "Profile",
      complete: "Complete",
      incomplete: "Incomplete",
      questionnaireScore: "Questionnaire score",
      language: "Language",
      narrativeLength: "Narrative length",
      signals: "Signals",
      attachments: "Attachments",
      characters: "characters",
      selected: "selected",
      noSignals: "No strong signals detected",
      ready: "Ready to save the final record.",
      notReady: "Complete the steps to make the record ready.",
      profileComplete: "Profile complete",
      profileIncomplete: "Profile incomplete",
      questionnaireCaptured: "Questionnaire captured",
      questionnaireMissing: "Questionnaire not filled",
      narrativeAdded: "Narrative added",
      narrativeMissing: "Narrative missing",
    },
  },
  Hindi: {
    screening: {
      heroEyebrow: "चरण 1/3",
      heroTitle: "ग्रामीण मानसिक स्वास्थ्य पहचान",
      heroText: "प्रश्नावली पर जाने से पहले पहचान और सहमति विवरण भरकर सत्र शुरू करें।",
      ready: "स्क्रीनिंग चरण तैयार",
      first: "पहले पहचान और सहमति",
      sideCard1Label: "स्क्रीनिंग कार्ड",
      sideCard2Label: "अगले जुड़े चरण",
      sideCard3Label: "अंतिम अंतर्दृष्टि पृष्ठ",
      languageLabel: "पसंदीदा भाषा",
      applyLanguage: "भाषा लागू करें",
      languageStatus: "पसंदीदा भाषा लागू करने के लिए तैयार है।",
      profileTitle: "उम्मीदवार प्रोफ़ाइल",
      fullName: "पूरा नाम",
      age: "आयु",
      gender: "लिंग",
      village: "गाँव / स्थानीय क्षेत्र",
      district: "जिला",
      block: "प्रखंड / उपखंड",
      occupation: "पेशा",
      phone: "फोन / संदर्भ संख्या",
      assessor: "मूल्यांकनकर्ता का नाम",
      consent: "स्क्रीनिंग के लिए सहमति मिली",
      next: "अगला",
      placeholders: {
        fullName: "पूरा नाम दर्ज करें",
        age: "वर्षों में आयु दर्ज करें",
        village: "गाँव या इलाका",
        district: "जिले का नाम",
        block: "प्रखंड या उपखंड",
        occupation: "वर्तमान पेशा",
        phone: "वैकल्पिक संपर्क",
        assessor: "स्वास्थ्यकर्मी या काउंसलर",
      },
      visual: {
        questionnaire: "प्रश्नावली",
        questionnaireText: "संरचित लक्षण संकेत",
        questionnaireBody: "स्क्रीनिंग कार्ड पूरा होने के बाद पेज 2 अपने अलग स्क्रीन पर खुलता है।",
        uploads: "अपलोड",
        uploadsText: "पाठ, ऑडियो, वीडियो",
        uploadsBody: "पेज 3 में मेटाडेटा और लाइव अंतर्दृष्टि आती है।",
        flow: "विज़ार्ड प्रवाह",
        flowText: "अगला और पिछला",
        flowBody: "बटन एक लंबे स्क्रोल की जगह अलग-अलग पेजों के बीच ले जाते हैं।",
        path: "लाइव स्क्रीनिंग पथ",
        pathStatus: "क्रमिक",
      },
    },
    questionnaire: {
      headerEyebrow: "चरण 2/3",
      headerTitle: "प्रश्नावली",
      headerText: "पिछले दो हफ्तों में प्रत्येक लक्षण कितनी बार आया, इसे रेट करें।",
      validatedTitle: "मान्यीकृत उपकरण",
      validatedText: "पूर्ण स्क्रीनिंग विवरण खोलने के लिए PHQ-9 पर टैप करें।",
      aboutButton: "PHQ-9 के बारे में",
      loadingInstruments: "मान्यीकृत उपकरण बटन लोड हो रहे हैं...",
      prev: "पिछला",
      next: "अगला",
    },
    insights: {
      headerEyebrow: "चरण 3/3",
      headerTitle: "मेटाडेटा अपलोड और लाइव अंतर्दृष्टि",
      headerText: "अंतिम रिकॉर्ड सहेजने से पहले विवरण, अपलोड जोड़ें, और लाइव पूर्वानुमान, NLP संकेत, तथा readiness देखें।",
      formTitle: "मुक्त पाठ और अपलोड मेटाडेटा",
      narrativeLabel: "बताएँ कि व्यक्ति कैसा महसूस कर रहा था",
      narrativePlaceholder: "उदाहरण: मैं थका हुआ, अलग-थलग, चिंतित महसूस कर रहा हूँ, और अच्छी नींद नहीं आ रही है।",
      speechTitle: "निर्देशित भाषण रिकॉर्डिंग",
      speechTopic: "विषय: अपने पिछले कुछ दिनों, नींद, तनाव, और लोगों से अपने जुड़ाव के बारे में बताइए।",
      speechStatus: "अपने डिवाइस के रिकॉर्ड बटन का उपयोग करें या नीचे नमूना जोड़ें।",
      voiceSample: "आवाज़ का नमूना",
      passiveTitle: "अतिरिक्त इनपुट",
      passiveTopic: "यदि आप अतिरिक्त संदर्भ शामिल करना चाहते हैं, तो एक छोटा फ्रंट-कैमरा वीडियो या संबंधित नोट अपलोड करें।",
      passiveLabel: "वीडियो या नोट",
      passiveStatus: "अभी तक कोई अतिरिक्त इनपुट नहीं मिला है।",
      liveFaceTitle: "लाइव चेहरे की कैप्चर",
      liveFaceTopic: "लाइव चेहरे के संकेतों के विश्लेषण के लिए वेबकैम से एक स्पष्ट फ्रंट फोटो लें।",
      faceLabel: "चेहरे की छवि",
      liveInsightsTitle: "लाइव अंतर्दृष्टि",
      liveInsightsText: "अंतिम रिकॉर्ड सहेजने से पहले लाइव पूर्वावलोकन, स्क्रीनिंग readiness, और सहायक संकेत देखें।",
      saveStatus: "रिज़ल्ट बनाने के लिए आकलन पूरा करें और सहेजें।",
      predictionTitle: "लाइव पूर्वानुमान पूर्वावलोकन",
      predictionText: "सहेजने से पहले प्रश्नावली और कथा का संयुक्त पूर्वावलोकन",
      nlpTitle: "लाइव NLP अंतर्दृष्टि",
      nlpText: "कथा पाठ से भावना, इमोशन और सुरक्षा संकेत",
      readinessTitle: "इंटेक तैयारियाँ",
      readinessText: "जाँचता है कि रिकॉर्ड सहेजने और विश्लेषण के लिए तैयार है या नहीं",
      prev: "पिछला",
      save: "आकलन सहेजें",
    },
    summary: {
      profile: "प्रोफ़ाइल",
      complete: "पूरा",
      incomplete: "अधूरा",
      questionnaireScore: "प्रश्नावली स्कोर",
      language: "भाषा",
      narrativeLength: "कथा लंबाई",
      signals: "संकेत",
      attachments: "संलग्नक",
      characters: "अक्षर",
      selected: "चयनित",
      noSignals: "कोई मजबूत संकेत नहीं मिले",
      ready: "अंतिम रिकॉर्ड सहेजने के लिए तैयार।",
      notReady: "रिकॉर्ड को तैयार करने के लिए चरण पूरे करें।",
      profileComplete: "प्रोफ़ाइल पूर्ण",
      profileIncomplete: "प्रोफ़ाइल अपूर्ण",
      questionnaireCaptured: "प्रश्नावली दर्ज",
      questionnaireMissing: "प्रश्नावली नहीं भरी",
      narrativeAdded: "कथा जोड़ी गई",
      narrativeMissing: "कथा गायब",
    },
  },
  Bengali: {
    screening: {
      heroEyebrow: "ধাপ 1/3",
      heroTitle: "গ্রামীণ মানসিক স্বাস্থ্য সনাক্তকরণ",
      heroText: "প্রশ্নাবলীতে যাওয়ার আগে পরিচয় এবং সম্মতির তথ্য পূরণ করে সেশন শুরু করুন।",
      ready: "স্ক্রিনিং ধাপ প্রস্তুত",
      first: "প্রথমে পরিচয় ও সম্মতি",
      sideCard1Label: "স্ক্রিনিং কার্ড",
      sideCard2Label: "পরবর্তী সংযুক্ত ধাপ",
      sideCard3Label: "চূড়ান্ত অন্তর্দৃষ্টি পৃষ্ঠা",
      languageLabel: "পছন্দের ভাষা",
      applyLanguage: "ভাষা প্রয়োগ করুন",
      languageStatus: "পছন্দের ভাষা প্রয়োগের জন্য প্রস্তুত।",
      profileTitle: "প্রার্থী প্রোফাইল",
      fullName: "পুরো নাম",
      age: "বয়স",
      gender: "লিঙ্গ",
      village: "গ্রাম / স্থানীয় এলাকা",
      district: "জেলা",
      block: "ব্লক / উপবিভাগ",
      occupation: "পেশা",
      phone: "ফোন / রেফারেন্স নম্বর",
      assessor: "মূল্যায়নকারীর নাম",
      consent: "স্ক্রিনিংয়ের জন্য সম্মতি পাওয়া গেছে",
      next: "পরবর্তী",
      placeholders: {
        fullName: "পুরো নাম লিখুন",
        age: "বছরে বয়স লিখুন",
        village: "গ্রাম বা এলাকা",
        district: "জেলার নাম",
        block: "ব্লক বা উপবিভাগ",
        occupation: "বর্তমান পেশা",
        phone: "ঐচ্ছিক যোগাযোগ",
        assessor: "স্বাস্থ্যকর্মী বা পরামর্শদাতা",
      },
      visual: {
        questionnaire: "প্রশ্নাবলী",
        questionnaireText: "গঠনমূলক উপসর্গ সংকেত",
        questionnaireBody: "স্ক্রিনিং কার্ড শেষ হলে পেজ 2 আলাদা স্ক্রিনে খুলবে।",
        uploads: "আপলোড",
        uploadsText: "পাঠ্য, অডিও, ভিডিও",
        uploadsBody: "পেজ 3 মেটাডেটা এবং লাইভ অন্তর্দৃষ্টি দেখায়।",
        flow: "উইজার্ড প্রবাহ",
        flowText: "পরবর্তী ও পূর্ববর্তী",
        flowBody: "একটি লম্বা স্ক্রোলের বদলে বোতামগুলো আলাদা পেজের মধ্যে নিয়ে যায়।",
        path: "লাইভ স্ক্রিনিং পথ",
        pathStatus: "ধাপে ধাপে",
      },
    },
    questionnaire: {
      headerEyebrow: "ধাপ 2/3",
      headerTitle: "প্রশ্নাবলী",
      headerText: "গত দুই সপ্তাহে প্রতিটি উপসর্গ কতবার হয়েছে তা রেট করুন।",
      validatedTitle: "যাচাইকৃত যন্ত্র",
      validatedText: "সম্পূর্ণ স্ক্রিনিং বিবরণ খুলতে PHQ-9 এ ট্যাপ করুন।",
      aboutButton: "PHQ-9 সম্পর্কে",
      loadingInstruments: "যাচাইকৃত যন্ত্রের বোতাম লোড হচ্ছে...",
      prev: "পূর্ববর্তী",
      next: "পরবর্তী",
    },
    insights: {
      headerEyebrow: "ধাপ 3/3",
      headerTitle: "মেটাডেটা আপলোড এবং লাইভ অন্তর্দৃষ্টি",
      headerText: "চূড়ান্ত রেকর্ড সংরক্ষণের আগে বর্ণনা, আপলোড, এবং লাইভ প্রেডিকশন, NLP সংকেত ও readiness দেখুন।",
      formTitle: "মুক্ত পাঠ্য এবং আপলোড মেটাডেটা",
      narrativeLabel: "ব্যক্তিটি কেমন অনুভব করছে তা বর্ণনা করুন",
      narrativePlaceholder: "উদাহরণ: আমি ক্লান্ত, বিচ্ছিন্ন, উদ্বিগ্ন বোধ করছি, এবং ভাল ঘুম হচ্ছে না।",
      speechTitle: "নির্দেশিত বক্তৃতা রেকর্ডিং",
      speechTopic: "বিষয়: আপনার শেষ কয়েক দিন, ঘুম, চাপ, এবং মানুষের সাথে আপনার সংযোগ কেমন ছিল তা বর্ণনা করুন।",
      speechStatus: "আপনার ডিভাইসের রেকর্ড বোতাম ব্যবহার করুন বা নিচে একটি নমুনা যোগ করুন।",
      voiceSample: "ভয়েস নমুনা",
      passiveTitle: "অতিরিক্ত ইনপুট",
      passiveTopic: "অতিরিক্ত প্রসঙ্গ যোগ করতে চাইলে একটি ছোট ফ্রন্ট-ক্যামেরার ভিডিও বা সম্পর্কিত নোট আপলোড করুন।",
      passiveLabel: "ভিডিও বা নোট",
      passiveStatus: "এখনও কোনো অতিরিক্ত ইনপুট পাওয়া যায়নি।",
      liveFaceTitle: "লাইভ মুখ ক্যাপচার",
      liveFaceTopic: "লাইভ মুখের সংকেত বিশ্লেষণের জন্য ওয়েবক্যাম থেকে একটি পরিষ্কার সামনের ছবি নিন।",
      faceLabel: "মুখের ছবি",
      liveInsightsTitle: "লাইভ অন্তর্দৃষ্টি",
      liveInsightsText: "চূড়ান্ত রেকর্ড সংরক্ষণের আগে লাইভ প্রিভিউ, screening readiness, এবং সহায়ক সংকেত দেখুন।",
      saveStatus: "ফলাফল তৈরি করতে মূল্যায়ন শেষ করে সংরক্ষণ করুন।",
      predictionTitle: "লাইভ প্রেডিকশন প্রিভিউ",
      predictionText: "সংরক্ষণের আগে প্রশ্নাবলী এবং বর্ণনার সম্মিলিত প্রিভিউ",
      nlpTitle: "লাইভ NLP অন্তর্দৃষ্টি",
      nlpText: "বর্ণনামূলক পাঠ্য থেকে অনুভূতি, ইমোশন, এবং নিরাপত্তা সংকেত",
      readinessTitle: "ইনটেক প্রস্তুতি",
      readinessText: "রেকর্ড সংরক্ষণ ও বিশ্লেষণের জন্য প্রস্তুত কিনা তা পরীক্ষা করে",
      prev: "পূর্ববর্তী",
      save: "মূল্যায়ন সংরক্ষণ করুন",
    },
    summary: {
      profile: "প্রোফাইল",
      complete: "সম্পূর্ণ",
      incomplete: "অসম্পূর্ণ",
      questionnaireScore: "প্রশ্নাবলী স্কোর",
      language: "ভাষা",
      narrativeLength: "বর্ণনার দৈর্ঘ্য",
      signals: "সংকেত",
      attachments: "সংযুক্তি",
      characters: "অক্ষর",
      selected: "নির্বাচিত",
      noSignals: "কোনো শক্তিশালী সংকেত পাওয়া যায়নি",
      ready: "চূড়ান্ত রেকর্ড সংরক্ষণের জন্য প্রস্তুত।",
      notReady: "রেকর্ড প্রস্তুত করতে ধাপগুলো সম্পন্ন করুন।",
      profileComplete: "প্রোফাইল সম্পূর্ণ",
      profileIncomplete: "প্রোফাইল অসম্পূর্ণ",
      questionnaireCaptured: "প্রশ্নাবলী সম্পন্ন",
      questionnaireMissing: "প্রশ্নাবলী পূরণ হয়নি",
      narrativeAdded: "বর্ণনা যোগ হয়েছে",
      narrativeMissing: "বর্ণনা অনুপস্থিত",
    },
  },
};

function normalizeLanguage(language) {
  return ["English", "Hindi", "Bengali"].includes(language) ? language : "English";
}

function wizardTranslations(language = "English") {
  return WIZARD_UI_TRANSLATIONS[normalizeLanguage(language)] || WIZARD_UI_TRANSLATIONS.English;
}

function wizardText(language, path, key) {
  return wizardTranslations(language)?.[path]?.[key] || wizardTranslations("English")?.[path]?.[key] || "";
}

function setLeadingLabelText(selector, text) {
  const label = document.querySelector(selector);
  if (!label) return;
  const textNode = [...label.childNodes].find((node) => node.nodeType === Node.TEXT_NODE);
  if (textNode) {
    textNode.textContent = `${text} `;
  }
}

function setSelectOptionLabels(selectId, labels) {
  const select = document.getElementById(selectId);
  if (!select) return;
  [...select.options].forEach((option, index) => {
    if (labels[index] !== undefined) {
      option.textContent = labels[index];
    }
  });
}

const liveCapture = {
  mediaRecorder: null,
  mediaChunks: [],
  webcamStream: null,
};

let activeWizardState = null;

const DEFAULT_STATE = {
  profile: {
    fullName: "",
    age: "",
    gender: "Prefer not to say",
    language: "English",
    village: "",
    district: "",
    block: "",
    occupation: "",
    phone: "",
    assessor: "",
    consent: false,
  },
  questionnaire: {},
  narrative: "",
  audioFileName: "",
  passiveVideoName: "",
  imageFileName: "",
};

function loadState() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    const storedLanguage = (() => {
      try {
        return normalizeLanguage(localStorage.getItem(LANGUAGE_STORAGE_KEY) || "English");
      } catch {
        return "English";
      }
    })();
    if (!raw) {
      return {
        ...structuredClone(DEFAULT_STATE),
        profile: { ...structuredClone(DEFAULT_STATE.profile), language: storedLanguage },
      };
    }
    const parsed = JSON.parse(raw);
    return {
      profile: {
        ...structuredClone(DEFAULT_STATE.profile),
        ...(parsed.profile || {}),
        language: normalizeLanguage(parsed.profile?.language || storedLanguage),
      },
      questionnaire: { ...(parsed.questionnaire || {}) },
      narrative: String(parsed.narrative || ""),
      audioFileName: String(parsed.audioFileName || ""),
      passiveVideoName: String(parsed.passiveVideoName || ""),
      imageFileName: String(parsed.imageFileName || ""),
    };
  } catch {
    const fallbackLanguage = (() => {
      try {
        return normalizeLanguage(localStorage.getItem(LANGUAGE_STORAGE_KEY) || "English");
      } catch {
        return "English";
      }
    })();
    return {
      ...structuredClone(DEFAULT_STATE),
      profile: { ...structuredClone(DEFAULT_STATE.profile), language: fallbackLanguage },
    };
  }
}

function saveState(state) {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  try {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, normalizeLanguage(state.profile.language));
  } catch {
    // Ignore persistence failures.
  }
}

function applyScreeningLanguage(language) {
  const normalized = language || "English";
  document.documentElement.lang = normalized === "Hindi" ? "hi" : normalized === "Bengali" ? "bn" : "en";
  try {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, normalizeLanguage(normalized));
  } catch {
    // Ignore persistence failures.
  }
}

function syncConsentNextButton(state) {
  const nextButton = document.getElementById("nextToQuestionnaire");
  if (!nextButton) return;
  const allowed = Boolean(
    state?.profile?.fullName &&
    state?.profile?.age &&
    state?.profile?.village &&
    state?.profile?.district &&
    state?.profile?.assessor &&
    state?.profile?.consent
  );
  nextButton.disabled = !allowed;
  nextButton.setAttribute("aria-disabled", String(!allowed));
  nextButton.classList.toggle("is-disabled", !allowed);
}

function setNodeText(selector, text) {
  const node = document.querySelector(selector);
  if (node) node.textContent = text;
}

function bindField(id, state, path) {
  const node = document.getElementById(id);
  if (!node) return;
  const current = path.split(".").reduce((obj, key) => obj?.[key], state);
  if (node.type === "checkbox") {
    node.checked = Boolean(current);
  } else {
    node.value = current ?? "";
  }
  const update = () => {
    let target = state;
    const keys = path.split(".");
    for (let index = 0; index < keys.length - 1; index += 1) {
      target = target[keys[index]];
    }
    target[keys[keys.length - 1]] = node.type === "checkbox" ? node.checked : node.value;
    saveState(state);
    if (path === "profile.language") {
      applyScreeningLanguage(state.profile.language);
    }
    if (path === "profile.consent") {
      syncConsentNextButton(state);
    }
    updateInsights(state);
  };
  node.addEventListener("input", update);
  node.addEventListener("change", update);
}

function attachFileField(id, state, key) {
  const node = document.getElementById(id);
  if (!node) return;
  node.addEventListener("change", () => {
    state[key] = node.files?.[0]?.name || "";
    saveState(state);
    updateInsights(state);
    updateCaptureUi(state);
  });
}

function updateCaptureUi(state = activeWizardState || loadState()) {
  const language = normalizeLanguage(state?.profile?.language || "English");
  const ui = wizardTranslations(language).insights;
  const recordingStatus = document.getElementById("recordingStatus");
  const cameraStatus = document.getElementById("cameraStatus");
  const startRecordingBtn = document.getElementById("startRecordingBtn");
  const stopRecordingBtn = document.getElementById("stopRecordingBtn");
  const clearRecordingBtn = document.getElementById("clearRecordingBtn");
  const startCameraBtn = document.getElementById("startCameraBtn");
  const capturePhotoBtn = document.getElementById("capturePhotoBtn");
  const stopCameraBtn = document.getElementById("stopCameraBtn");
  const clearCapturedPhotoBtn = document.getElementById("clearCapturedPhotoBtn");
  const cameraPreview = document.getElementById("cameraPreview");
  const capturedPhotoPreview = document.getElementById("capturedPhotoPreview");
  const audioFile = document.getElementById("audioFile");
  const imageFile = document.getElementById("imageFile");

  const recorderActive = Boolean(liveCapture.mediaRecorder && liveCapture.mediaRecorder.state === "recording");
  const hasRecording = Boolean(state.audioFileName || audioFile?.files?.[0]);
  if (startRecordingBtn) startRecordingBtn.disabled = recorderActive;
  if (stopRecordingBtn) stopRecordingBtn.disabled = !recorderActive;
  if (clearRecordingBtn) clearRecordingBtn.disabled = !hasRecording && !recorderActive;
  if (recordingStatus) {
    recordingStatus.textContent = hasRecording
      ? `${ui.recordingReady || "Speech recording ready"}: ${state.audioFileName || audioFile?.files?.[0]?.name || ""}`.trim()
      : recorderActive
        ? ui.recordingProgress || "Recording in progress..."
        : ui.recordingMissing || "No speech recording captured yet.";
  }

  const streamActive = Boolean(liveCapture.webcamStream);
  const hasPhoto = Boolean(state.imageFileName || imageFile?.files?.[0]);
  if (startCameraBtn) startCameraBtn.disabled = streamActive;
  if (capturePhotoBtn) capturePhotoBtn.disabled = !streamActive;
  if (stopCameraBtn) stopCameraBtn.disabled = !streamActive;
  if (clearCapturedPhotoBtn) clearCapturedPhotoBtn.disabled = !hasPhoto;
  if (cameraPreview) cameraPreview.classList.toggle("is-hidden", !streamActive);
  if (capturedPhotoPreview) capturedPhotoPreview.classList.toggle("is-hidden", !hasPhoto);
  if (cameraStatus) {
    cameraStatus.textContent = hasPhoto
      ? `${ui.photoReady || "Captured photo ready"}: ${state.imageFileName || imageFile?.files?.[0]?.name || ""}`.trim()
      : streamActive
        ? ui.cameraOpen || "Camera is open. Capture a clear front-facing photo."
        : ui.photoMissing || "No live photo captured yet.";
  }

}

function clearUploadedMediaInputs() {
  const audioFile = document.getElementById("audioFile");
  const imageFile = document.getElementById("imageFile");
  if (audioFile) audioFile.value = "";
  if (imageFile) imageFile.value = "";
}

async function startSpeechRecording() {
  if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
    return;
  }
  const state = activeWizardState;
  if (!state) return;
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mimeType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus")
      ? "audio/webm;codecs=opus"
      : MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "";
    liveCapture.mediaChunks = [];
    liveCapture.mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
    liveCapture.mediaRecorder.addEventListener("dataavailable", (event) => {
      if (event.data && event.data.size > 0) liveCapture.mediaChunks.push(event.data);
    });
    liveCapture.mediaRecorder.addEventListener("stop", () => {
      const finalMime = liveCapture.mediaRecorder?.mimeType || mimeType || "audio/webm";
      const blob = new Blob(liveCapture.mediaChunks, { type: finalMime });
      state.audioFileName = `guided-speech.${finalMime.includes("ogg") ? "ogg" : "webm"}`;
      stream.getTracks().forEach((track) => track.stop());
      liveCapture.mediaRecorder = null;
      liveCapture.mediaChunks = [];
      saveState(state);
      updateCaptureUi(state);
      updateInsights(state);
    });
    state.audioFileName = "";
    clearUploadedMediaInputs();
    liveCapture.mediaRecorder.start();
    updateCaptureUi(state);
  } catch {
    // Keep the UI responsive even if microphone access fails.
  }
}

function stopSpeechRecording() {
  if (liveCapture.mediaRecorder && liveCapture.mediaRecorder.state === "recording") {
    liveCapture.mediaRecorder.stop();
  }
}

function clearSpeechRecording() {
  if (liveCapture.mediaRecorder && liveCapture.mediaRecorder.state === "recording") {
    liveCapture.mediaRecorder.stop();
  }
  const state = activeWizardState;
  if (!state) return;
  state.audioFileName = "";
  liveCapture.mediaChunks = [];
  saveState(state);
  updateCaptureUi(state);
  updateInsights(state);
}

async function startWebcam() {
  if (!navigator.mediaDevices?.getUserMedia) {
    return;
  }
  const state = activeWizardState;
  if (!state) return;
  try {
    if (document.getElementById("capturedPhotoPreview")?.src) {
      URL.revokeObjectURL(document.getElementById("capturedPhotoPreview").src);
      document.getElementById("capturedPhotoPreview").removeAttribute("src");
    }
    state.imageFileName = "";
    const imageFile = document.getElementById("imageFile");
    if (imageFile) imageFile.value = "";
    liveCapture.webcamStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
    const cameraPreview = document.getElementById("cameraPreview");
    if (cameraPreview) cameraPreview.srcObject = liveCapture.webcamStream;
    updateCaptureUi(state);
  } catch {
    // Keep the UI responsive if webcam access fails.
  }
}

function stopWebcam() {
  if (liveCapture.webcamStream) {
    liveCapture.webcamStream.getTracks().forEach((track) => track.stop());
    liveCapture.webcamStream = null;
  }
  const cameraPreview = document.getElementById("cameraPreview");
  if (cameraPreview) cameraPreview.srcObject = null;
  updateCaptureUi(activeWizardState || loadState());
}

function captureWebcamPhoto() {
  const state = activeWizardState;
  const cameraPreview = document.getElementById("cameraPreview");
  const canvas = document.getElementById("captureCanvas");
  const capturedPhotoPreview = document.getElementById("capturedPhotoPreview");
  if (!state || !liveCapture.webcamStream || !cameraPreview || !canvas || !capturedPhotoPreview) return;
  const width = cameraPreview.videoWidth || 640;
  const height = cameraPreview.videoHeight || 480;
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext("2d");
  context.drawImage(cameraPreview, 0, 0, width, height);
  canvas.toBlob((blob) => {
    if (!blob) return;
    if (capturedPhotoPreview.src) {
      URL.revokeObjectURL(capturedPhotoPreview.src);
    }
    state.imageFileName = "captured-face.jpg";
    capturedPhotoPreview.src = URL.createObjectURL(blob);
    stopWebcam();
    saveState(state);
    updateCaptureUi(state);
    updateInsights(state);
  }, "image/jpeg", 0.92);
}

function clearCapturedPhoto() {
  const state = activeWizardState;
  const capturedPhotoPreview = document.getElementById("capturedPhotoPreview");
  if (capturedPhotoPreview?.src) {
    URL.revokeObjectURL(capturedPhotoPreview.src);
    capturedPhotoPreview.removeAttribute("src");
  }
  if (!state) return;
  state.imageFileName = "";
  const imageFile = document.getElementById("imageFile");
  if (imageFile) imageFile.value = "";
  saveState(state);
  updateCaptureUi(state);
  updateInsights(state);
}

function buildQuestionnaire(language = loadState().profile.language) {
  const container = document.getElementById("questionnaireContainer");
  if (!container) return;
  const state = loadState();
  const normalizedLanguage = normalizeLanguage(language);
  const optionLabels = RESPONSE_OPTION_LABELS[normalizedLanguage] || RESPONSE_OPTION_LABELS.English;
  const ui = wizardTranslations(normalizedLanguage).questionnaire;
  container.innerHTML = `
    <div class="questionnaire-segment-intro">
      <p class="detail-muted">${ui.segmentIntro || ""}</p>
    </div>
    ${QUESTIONNAIRE_SEGMENTS.map((segment) => {
      const questions = segment.itemIds.map((itemId) => {
        const item = QUESTIONNAIRE_ITEMS.find((entry) => entry.id === itemId);
        if (!item) return "";
        const current = Number(state.questionnaire[item.id] ?? 0);
        const options = RESPONSE_OPTIONS.map((option) => {
          const checked = current === option.value ? "checked" : "";
          return `
            <label class="wizard-choice">
              <input type="radio" name="${item.id}" value="${option.value}" ${checked}>
              <span>${optionLabels[option.value] || option.label}</span>
            </label>`;
        }).join("");
        return `
          <article class="wizard-question">
            <h4>${QUESTIONNAIRE_LABELS[normalizedLanguage]?.[item.id] || item.label}</h4>
            <div class="wizard-options">${options}</div>
          </article>`;
      }).join("");
      return `
        <section class="questionnaire-segment">
          <div class="questionnaire-segment-header">
            <p class="intake-kicker">${QUESTIONNAIRE_SEGMENT_LABELS[normalizedLanguage]?.[segment.id] || segment.id}</p>
            <p class="questionnaire-segment-summary">${QUESTIONNAIRE_SEGMENT_SUMMARIES[normalizedLanguage]?.[segment.id] || QUESTIONNAIRE_SEGMENT_SUMMARIES.English[segment.id] || ""}</p>
          </div>
          <div class="questionnaire-segment-grid">${questions}</div>
        </section>`;
    }).join("")}
  `;

  container.querySelectorAll('input[type="radio"]').forEach((radio) => {
    radio.addEventListener("change", () => {
      state.questionnaire[radio.name] = Number(radio.value);
      saveState(state);
      updateInsights(state);
    });
  });

  const validatedPanel = document.getElementById("validatedInstrumentPanel");
  const validatedInfo = document.getElementById("validatedInstrumentInfo");
  const phq9Items = QUESTIONNAIRE_ITEMS.slice(0, 9);
  const detailOptions = optionLabels.map((label) => `<li>${label}</li>`).join("");
  if (validatedPanel) {
    validatedPanel.className = "validated-instrument-panel";
    validatedPanel.innerHTML = `
      <button id="validatedInstrumentInfoBtn" class="ghost-btn validated-instrument-btn" type="button" data-validated-instrument-id="phq9">
        PHQ-9
      </button>
    `;
  }
  if (validatedInfo) {
    validatedInfo.className = "validated-instrument-info is-hidden";
    validatedInfo.innerHTML = `
      <div class="validated-instrument-detail-shell">
        <div class="validated-instrument-detail-head">
          <strong>PHQ-9</strong>
          <span class="intake-kicker">${ui.headerTitle || "Questionnaire"}</span>
        </div>
        <p class="detail-muted">Patient Health Questionnaire-9, original English version</p>
        <div class="validated-instrument-detail-list">
          ${phq9Items.map((item, index) => {
            const label = QUESTIONNAIRE_LABELS[normalizedLanguage]?.[item.id] || item.label;
            return `<div class="validated-instrument-detail-item"><span>${String(index + 1).padStart(2, "0")}. ${label}</span></div>`;
          }).join("")}
        </div>
        <div class="validated-instrument-detail-scale">
          <p class="detail-muted">Response scale</p>
          <ul>${detailOptions}</ul>
        </div>
      </div>
    `;
  }
  document.getElementById("validatedInstrumentInfoBtn")?.addEventListener("click", () => {
    if (!validatedInfo) return;
    validatedInfo.classList.toggle("is-hidden");
  });
}

function computeQuestionnaireAverage(questionnaire) {
  const values = QUESTIONNAIRE_ITEMS.map((item) => Number(questionnaire[item.id] ?? 0));
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function scoreLabel(score, language = "English") {
  const labels = {
    English: ["Low", "Mild", "Moderate", "High"],
    Hindi: ["कम", "हल्का", "मध्यम", "उच्च"],
    Bengali: ["কম", "মৃদু", "মধ্যম", "উচ্চ"],
  }[normalizeLanguage(language)] || ["Low", "Mild", "Moderate", "High"];
  if (score < 0.75) return labels[0];
  if (score < 1.5) return labels[1];
  if (score < 2.25) return labels[2];
  return labels[3];
}

function extractSignals(text) {
  const lower = String(text || "").toLowerCase();
  const matches = [];
  const signalMap = {
    sleep: ["sleep", "insomnia", "restless"],
    mood: ["sad", "depressed", "hopeless", "down"],
    stress: ["stress", "anxious", "worry", "tense"],
    isolation: ["alone", "isolated", "disconnected", "lonely"],
  };
  Object.entries(signalMap).forEach(([label, words]) => {
    if (words.some((word) => lower.includes(word))) matches.push(label);
  });
  return matches;
}

function updateInsights(state) {
  const prediction = document.getElementById("workspacePrediction");
  const nlp = document.getElementById("workspaceNlp");
  const readiness = document.getElementById("workspaceReadiness");
  const status = document.getElementById("workspaceStatus") || document.getElementById("saveStatus");

  if (!prediction || !nlp || !readiness) return;

  const language = normalizeLanguage(state.profile.language);
  const ui = wizardTranslations(language);
  const questionScore = computeQuestionnaireAverage(state.questionnaire);
  const profileReady = Boolean(state.profile.fullName && state.profile.age && state.profile.village && state.profile.assessor && state.profile.consent);
  const narrative = state.narrative.trim();
  const signals = extractSignals(narrative);

  prediction.innerHTML = `
    <div class="wizard-summary">
      <p><strong>${ui.summary.profile}:</strong> ${profileReady ? ui.summary.complete : ui.summary.incomplete}</p>
      <p><strong>${ui.summary.questionnaireScore}:</strong> ${questionScore.toFixed(2)} (${scoreLabel(questionScore, language)})</p>
      <p><strong>${ui.summary.language}:</strong> ${language}</p>
    </div>
  `;

  nlp.innerHTML = `
    <div class="wizard-summary">
      <p><strong>${ui.summary.narrativeLength}:</strong> ${narrative.length || 0} ${ui.summary.characters}</p>
      <p><strong>${ui.summary.signals}:</strong> ${signals.length ? signals.join(", ") : ui.summary.noSignals}</p>
      <p><strong>${ui.summary.attachments}:</strong> ${[state.audioFileName, state.imageFileName].filter(Boolean).length} ${ui.summary.selected}</p>
    </div>
  `;

  const readinessItems = [
    profileReady ? ui.summary.profileComplete : ui.summary.profileIncomplete,
    questionScore > 0 ? ui.summary.questionnaireCaptured : ui.summary.questionnaireMissing,
    narrative ? ui.summary.narrativeAdded : ui.summary.narrativeMissing,
  ];

  readiness.innerHTML = `
    <div class="wizard-summary">
      ${readinessItems.map((item) => `<p>${item}</p>`).join("")}
    </div>
  `;

  if (status) {
    status.textContent = profileReady && questionScore >= 0 && narrative
      ? ui.summary.ready
      : ui.summary.notReady;
  }
}

function initScreeningPage() {
  const state = loadState();
  bindField("fullName", state, "profile.fullName");
  bindField("age", state, "profile.age");
  bindField("gender", state, "profile.gender");
  bindField("language", state, "profile.language");
  bindField("village", state, "profile.village");
  bindField("district", state, "profile.district");
  bindField("block", state, "profile.block");
  bindField("occupation", state, "profile.occupation");
  bindField("phone", state, "profile.phone");
  bindField("assessor", state, "profile.assessor");
  bindField("consent", state, "profile.consent");
  applyScreeningLanguage(state.profile.language);
  renderScreeningLanguage(state.profile.language);
  syncConsentNextButton(state);
  updateInsights(state);

  document.getElementById("nextToQuestionnaire")?.addEventListener("click", () => {
    if (!state.profile.consent) {
      return;
    }
    saveState(state);
    window.location.href = "questionnaire.html";
  });
}

function initQuestionnairePage() {
  const state = loadState();
  renderQuestionnaireLanguage(state.profile.language);
  updateInsights(state);
  document.getElementById("prevToScreening")?.addEventListener("click", () => {
    window.location.href = "screening.html";
  });
  document.getElementById("nextToLiveInsights")?.addEventListener("click", () => {
    saveState(state);
    window.location.href = "live-insights.html";
  });
}

function initInsightsPage() {
  const state = loadState();
  activeWizardState = state;
  renderInsightsLanguage(state.profile.language);
  bindField("narrative", state, "narrative");
  attachFileField("audioFile", state, "audioFileName");
  attachFileField("imageFile", state, "imageFileName");
  updateInsights(state);
  updateCaptureUi(state);

  document.getElementById("startRecordingBtn")?.addEventListener("click", startSpeechRecording);
  document.getElementById("stopRecordingBtn")?.addEventListener("click", stopSpeechRecording);
  document.getElementById("clearRecordingBtn")?.addEventListener("click", clearSpeechRecording);
  document.getElementById("startCameraBtn")?.addEventListener("click", startWebcam);
  document.getElementById("capturePhotoBtn")?.addEventListener("click", captureWebcamPhoto);
  document.getElementById("stopCameraBtn")?.addEventListener("click", stopWebcam);
  document.getElementById("clearCapturedPhotoBtn")?.addEventListener("click", clearCapturedPhoto);
  document.getElementById("prevToQuestionnaire")?.addEventListener("click", () => {
    window.location.href = "questionnaire.html";
  });
  document.getElementById("saveRecord")?.addEventListener("click", () => {
    saveState(state);
    sessionStorage.setItem(SAVED_RECORD_KEY, JSON.stringify({ ...state, savedAt: new Date().toISOString() }));
    updateInsights(state);
    const banner = document.getElementById("saveStatus");
    if (banner) banner.textContent = "Record saved for analysis. Returning to the dashboard...";
    window.setTimeout(() => {
      window.location.href = "/web/index.html#analyticsView";
    }, 1200);
  });
}

function renderScreeningLanguage(language) {
  const normalized = normalizeLanguage(language);
  const ui = wizardTranslations(normalized).screening;
  document.documentElement.lang = normalized === "Hindi" ? "hi" : normalized === "Bengali" ? "bn" : "en";
  document.title = ui.heroTitle;
  setLeadingLabelText(".hero-copy-main .eyebrow", ui.heroEyebrow);
  setNodeText(".hero-copy-main h1", ui.heroTitle);
  setNodeText(".hero-copy-main .hero-text", ui.heroText);
  setNodeText(".wizard-meta .offline-pill.online", ui.ready);
  setNodeText(".wizard-meta .offline-pill.syncing", ui.first);
  setNodeText(".hero-copy-side .hero-metric-card:nth-child(1) .hero-metric-label", ui.sideCard1Label);
  setNodeText(".hero-copy-side .hero-metric-card:nth-child(2) .hero-metric-label", ui.sideCard2Label);
  setNodeText(".hero-copy-side .hero-metric-card:nth-child(3) .hero-metric-label", ui.sideCard3Label);
  setNodeText(".language-switcher label", ui.languageLabel);
  setNodeText(".profile-card h3", ui.profileTitle);
  setLeadingLabelText('label[for="language"]', ui.languageLabel);
  setLeadingLabelText(".profile-card label:nth-of-type(1)", ui.fullName);
  setLeadingLabelText(".profile-card label:nth-of-type(2)", ui.age);
  setLeadingLabelText(".profile-card label:nth-of-type(3)", ui.gender);
  setLeadingLabelText(".profile-card label:nth-of-type(4)", ui.village);
  setLeadingLabelText(".profile-card label:nth-of-type(5)", ui.district);
  setLeadingLabelText(".profile-card label:nth-of-type(6)", ui.block);
  setLeadingLabelText(".profile-card label:nth-of-type(7)", ui.occupation);
  setLeadingLabelText(".profile-card label:nth-of-type(8)", ui.phone);
  setLeadingLabelText(".profile-card label:nth-of-type(9)", ui.assessor);
  setLeadingLabelText(".profile-consent", ui.consent);
  setNodeText("#nextToQuestionnaire", ui.next);
  setNodeText("#languageStatus", ui.languageStatus);
  const placeholderMap = ui.placeholders;
  if (document.getElementById("fullName")) document.getElementById("fullName").placeholder = placeholderMap.fullName;
  if (document.getElementById("age")) document.getElementById("age").placeholder = placeholderMap.age;
  if (document.getElementById("village")) document.getElementById("village").placeholder = placeholderMap.village;
  if (document.getElementById("district")) document.getElementById("district").placeholder = placeholderMap.district;
  if (document.getElementById("block")) document.getElementById("block").placeholder = placeholderMap.block;
  if (document.getElementById("occupation")) document.getElementById("occupation").placeholder = placeholderMap.occupation;
  if (document.getElementById("phone")) document.getElementById("phone").placeholder = placeholderMap.phone;
  if (document.getElementById("assessor")) document.getElementById("assessor").placeholder = placeholderMap.assessor;
  setNodeText(".signal-card-text .signal-card-label", ui.visual.questionnaire);
  setNodeText(".signal-card-text strong", ui.visual.questionnaireText);
  setNodeText(".signal-card-text p", ui.visual.questionnaireBody);
  setNodeText(".signal-card-audio .signal-card-label", ui.visual.uploads);
  setNodeText(".signal-card-audio strong", ui.visual.uploadsText);
  setNodeText(".signal-card-audio p", ui.visual.uploadsBody);
  setNodeText(".signal-card-face .signal-card-label", ui.visual.flow);
  setNodeText(".signal-card-face strong", ui.visual.flowText);
  setNodeText(".signal-card-face p", ui.visual.flowBody);
  setNodeText(".signal-chart-header span:first-child", ui.visual.path);
  setNodeText(".signal-chart-header span:last-child", ui.visual.pathStatus);
}

function renderQuestionnaireLanguage(language) {
  const normalized = normalizeLanguage(language);
  const ui = wizardTranslations(normalized).questionnaire;
  document.documentElement.lang = normalized === "Hindi" ? "hi" : normalized === "Bengali" ? "bn" : "en";
  document.title = ui.headerTitle;
  setNodeText(".wizard-header .eyebrow", ui.headerEyebrow);
  setNodeText(".wizard-header h1", ui.headerTitle);
  setNodeText(".wizard-header .hero-text", ui.headerText);
  setNodeText(".form-card h3", ui.validatedTitle);
  setNodeText(".form-card .detail-muted", ui.validatedText);
  setNodeText("#prevToScreening", ui.prev);
  setNodeText("#nextToLiveInsights", ui.next);
  buildQuestionnaire(normalized);
}

function renderInsightsLanguage(language) {
  const normalized = normalizeLanguage(language);
  const ui = wizardTranslations(normalized).insights;
  const liveControlLabels = normalized === "Hindi"
    ? {
        startRecording: "\u0930\u093f\u0915\u0949\u0930\u094d\u0921 \u0936\u0941\u0930\u0942 \u0915\u0930\u0947\u0902",
        stopRecording: "\u0930\u093f\u0915\u0949\u0930\u094d\u0921 \u0930\u094b\u0915\u0947\u0902",
        clearRecording: "\u0930\u093f\u0915\u0949\u0930\u094d\u0921 \u0938\u093e\u092b \u0915\u0930\u0947\u0902",
        startCamera: "\u0915\u0948\u092e\u0930\u093e \u0916\u094b\u0932\u0947\u0902",
        capturePhoto: "\u092b\u094b\u091f\u094b \u0932\u0947\u0902",
        stopCamera: "\u0915\u0948\u092e\u0930\u093e \u092c\u0902\u0926 \u0915\u0930\u0947\u0902",
        clearPhoto: "\u092b\u094b\u091f\u094b \u0938\u093e\u092b \u0915\u0930\u0947\u0902",
      }
    : normalized === "Bengali"
      ? {
          startRecording: "\u09b0\u09c7\u0995\u09b0\u09cd\u09a1 \u09b6\u09c1\u09b0\u09c1 \u0995\u09b0\u09c1\u09a8",
          stopRecording: "\u09b0\u09c7\u0995\u09b0\u09cd\u09a1 \u09ac\u09a8\u09cd\u09a7 \u0995\u09b0\u09c1\u09a8",
          clearRecording: "\u09b0\u09c7\u0995\u09b0\u09cd\u09a1 \u09ae\u09c1\u099b\u09bf\u09af\u09bc\u09c7 \u09ab\u09c7\u09b2\u09c1\u09a8",
          startCamera: "\u0995\u09cd\u09af\u09be\u09ae\u09c7\u09b0\u09be \u0996\u09c1\u09b2\u09c1\u09a8",
          capturePhoto: "\u09ab\u09cb\u099f\u09cb \u09a8\u09bf\u09a8",
          stopCamera: "\u0995\u09cd\u09af\u09be\u09ae\u09c7\u09b0\u09be \u09ac\u09a8\u09cd\u09a7 \u0995\u09b0\u09c1\u09a8",
          clearPhoto: "\u09ab\u09cb\u099f\u09cb \u09ae\u09c1\u099b\u09bf\u09af\u09bc\u09c7 \u09ab\u09c7\u09b2\u09c1\u09a8",
        }
      : {
          startRecording: "Start Recording",
          stopRecording: "Stop Recording",
          clearRecording: "Clear Recording",
          startCamera: "Open Camera",
          capturePhoto: "Capture Photo",
          stopCamera: "Close Camera",
          clearPhoto: "Clear Photo",
        };
  document.documentElement.lang = normalized === "Hindi" ? "hi" : normalized === "Bengali" ? "bn" : "en";
  document.title = ui.headerTitle;
  setNodeText(".wizard-header .eyebrow", ui.headerEyebrow);
  setNodeText(".wizard-header h1", ui.headerTitle);
  setNodeText(".wizard-header .hero-text", ui.headerText);
  setNodeText(".wizard-grid-2 .form-card:nth-child(1) h3", ui.formTitle);
  setLeadingLabelText(".wizard-grid-2 .form-card:nth-child(1) > label:nth-of-type(1)", ui.narrativeLabel);
  const narrative = document.getElementById("narrative");
  if (narrative) narrative.placeholder = ui.narrativePlaceholder;
  setNodeText(".wizard-grid-2 .capture-card:nth-of-type(1) .capture-head strong", ui.speechTitle);
  setNodeText(".wizard-grid-2 .capture-card:nth-of-type(1) .capture-head .capture-topic", ui.speechTopic);
  setNodeText(".wizard-grid-2 .capture-card:nth-of-type(1) .capture-status", ui.speechStatus);
  setNodeText("#startRecordingBtn", ui.startRecording || liveControlLabels.startRecording);
  setNodeText("#stopRecordingBtn", ui.stopRecording || liveControlLabels.stopRecording);
  setNodeText("#clearRecordingBtn", ui.clearRecording || liveControlLabels.clearRecording);
  setLeadingLabelText(".wizard-grid-2 .form-card:nth-child(1) > label:nth-of-type(2)", ui.voiceSample);
  setNodeText(".wizard-grid-2 .capture-card:nth-of-type(2) .capture-head strong", ui.liveFaceTitle);
  setNodeText(".wizard-grid-2 .capture-card:nth-of-type(2) .capture-head .capture-topic", ui.liveFaceTopic);
  setNodeText("#startCameraBtn", ui.startCamera || liveControlLabels.startCamera);
  setNodeText("#capturePhotoBtn", ui.capturePhoto || liveControlLabels.capturePhoto);
  setNodeText("#stopCameraBtn", ui.stopCamera || liveControlLabels.stopCamera);
  setNodeText("#clearCapturedPhotoBtn", ui.clearPhoto || liveControlLabels.clearPhoto);
  setLeadingLabelText(".wizard-grid-2 .form-card:nth-child(1) > label:nth-of-type(3)", ui.faceLabel);
  setNodeText(".review-card .section-heading h3", ui.liveInsightsTitle);
  setNodeText(".review-card .section-heading p", ui.liveInsightsText);
  setNodeText("#saveStatus", ui.saveStatus);
  setNodeText(".review-card .detail-grid .detail-panel:nth-child(1) h2", ui.predictionTitle);
  setNodeText(".review-card .detail-grid .detail-panel:nth-child(1) p", ui.predictionText);
  setNodeText(".review-card .detail-grid .detail-panel:nth-child(2) h2", ui.nlpTitle);
  setNodeText(".review-card .detail-grid .detail-panel:nth-child(2) p", ui.nlpText);
  setNodeText(".review-card .detail-grid .detail-panel:nth-child(3) h2", ui.readinessTitle);
  setNodeText(".review-card .detail-grid .detail-panel:nth-child(3) p", ui.readinessText);
  setNodeText("#prevToQuestionnaire", ui.prev);
  setNodeText("#saveRecord", ui.save);
}

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  if (page === "screening") initScreeningPage();
  if (page === "questionnaire") initQuestionnairePage();
  if (page === "insights") initInsightsPage();
});
