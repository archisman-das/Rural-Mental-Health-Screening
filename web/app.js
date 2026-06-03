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

const RESPONSE_OPTION_TRANSLATIONS = {
  English: ["Not at all", "Several days", "More than half the days", "Nearly every day"],
  Hindi: ["बिलकुल नहीं", "कुछ दिन", "आधे से अधिक दिन", "लगभग हर दिन"],
  Bengali: ["একদম না", "কয়েক দিন", "অর্ধেকের বেশি দিন", "প্রায় প্রতিদিন"],
};

const UI_TRANSLATIONS = {
  English: {
    workspaceTab: "Assessment Workspace",
    analyticsTab: "Analytics Hub",
    recordsTab: "Records and Reports",
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
    narrativeLabel: "Describe how the person has been feeling",
    narrativePlaceholder: "Example: I have been feeling tired, disconnected, anxious, and unable to sleep well.",
    guidedSpeechTitle: "Guided Speech Recording",
    guidedSpeechTopic: "Topic: Describe your last few days, your sleep, stress, and how connected you feel to people around you.",
    audioFileLabel: "Voice sample",
    liveFaceTitle: "Live Face Capture",
    liveFaceTopic: "Capture one clear front-facing photo from the webcam for live facial-cue analysis.",
    imageFileLabel: "Face image",
    saveAssessmentBtn: "Save Assessment",
    resetAssessmentBtn: "Reset Form",
    workspaceStatusDefault: "Complete the assessment and save it to generate the result.",
    workspacePredictionEmpty: "Start filling the assessment to generate a live prediction preview.",
    workspaceNlpEmpty: "NLP signals will appear here while the narrative is being entered.",
    workspaceReadinessEmpty: "Fill in candidate details, consent, questionnaire, and narrative to see readiness feedback.",
    analyticsBannerDefault: "Complete and save an assessment to open detailed analysis here.",
    recordsBannerDefault: "Fetch a saved assessment by ID when you want to review or download an older report.",
    analyticsReady: "detailed component-wise analysis is ready.",
    savedMessage: "saved through the backend API.",
    analyticsShowing: "Analytics Hub is now showing assessment",
    saveInProgress: "Saving assessment through the Python NLP backend...",
    previewRefreshing: "Refreshing the live preview from the Python NLP backend...",
    noRecordSelected: "No assessment selected.",
    assessmentIdLabel: "Assessment ID",
    candidateLabel: "Candidate",
    villageShortLabel: "Village",
    assessorShortLabel: "Assessor",
    createdAtLabel: "Created At",
    analyticsIntroCurrent: "One assessment in focus",
    analyticsIntroCurrentText: "Analytics Hub now explains the currently saved assessment instead of loading a list of backend records by default.",
    analyticsIntroModel: "Model Insights",
    analyticsIntroModelText: "Review domain-level scores, modality quality, confidence, transformer usage, and NLP signal interpretation for this assessment.",
    analyticsIntroScope: "Prediction Scope",
    analyticsIntroScopeText: "Depression, Anxiety, Stress, Sleep Disorder, Burnout, Loneliness, and Substance Abuse.",
    detailAnalysisTitle: "Detailed component-wise analysis for the current assessment.",
    recordsHeadingText: "Fetch records, inspect individual predictions, and export a PDF report.",
    recordLookupPlaceholder: "Enter assessment ID to fetch",
    fetchRecordBtn: "Fetch Record",
    downloadPdfBtn: "Download Selected PDF",
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
    questionnaireRiskTitle: "Questionnaire Risk",
    questionnaireOverall: "Questionnaire Overall",
    combinedResultTitle: "Combined Dashboard Result",
    confidenceLabel: "Confidence",
    recommendationLabel: "Recommendation",
    questionnaireLabel: "Questionnaire",
    dashboardLabel: "Dashboard",
    noDataModality: "No data available for this modality.",
    availableLabel: "Available",
    uploadReceivedLabel: "Upload Received, Not Analyzable",
    notAvailableLabel: "Not available",
    noFeaturesLabel: "No raw feature values were captured for this record.",
    noMatchRecords: "No assessments match the current filters.",
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
  },
  Hindi: {
    workspaceTab: "आकलन कार्यक्षेत्र",
    analyticsTab: "विश्लेषण केंद्र",
    recordsTab: "रिकॉर्ड और रिपोर्ट",
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
    narrativeLabel: "व्यक्ति कैसा महसूस कर रहा है, इसका वर्णन करें",
    narrativePlaceholder: "उदाहरण: मैं थका हुआ, अलग-थलग, चिंतित और ठीक से सो नहीं पा रहा हूँ।",
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
    analyticsBannerDefault: "विस्तृत विश्लेषण देखने के लिए आकलन पूरा करके सहेजें।",
    recordsBannerDefault: "पुरानी रिपोर्ट देखने या डाउनलोड करने के लिए आकलन ID से रिकॉर्ड खोजें।",
    analyticsReady: "का विस्तृत घटक-आधारित विश्लेषण तैयार है।",
    savedMessage: "बैकएंड API के माध्यम से सहेजा गया।",
    analyticsShowing: "Analytics Hub अब यह आकलन दिखा रहा है",
    saveInProgress: "Python NLP बैकएंड के माध्यम से आकलन सहेजा जा रहा है...",
    previewRefreshing: "Python NLP बैकएंड से लाइव प्रीव्यू ताज़ा किया जा रहा है...",
    noRecordSelected: "कोई आकलन चुना नहीं गया है।",
    assessmentIdLabel: "आकलन आईडी",
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
    questionnaireRiskTitle: "प्रश्नावली जोखिम",
    questionnaireOverall: "प्रश्नावली कुल स्कोर",
    combinedResultTitle: "संयुक्त डैशबोर्ड परिणाम",
    confidenceLabel: "कॉन्फिडेंस",
    recommendationLabel: "सिफारिश",
    questionnaireLabel: "प्रश्नावली",
    dashboardLabel: "डैशबोर्ड",
    noDataModality: "इस मॉडेलिटी के लिए कोई डेटा उपलब्ध नहीं है।",
    availableLabel: "उपलब्ध",
    uploadReceivedLabel: "अपलोड मिला, लेकिन विश्लेषण योग्य नहीं",
    notAvailableLabel: "उपलब्ध नहीं",
    noFeaturesLabel: "इस रिकॉर्ड के लिए कोई कच्चे फीचर मान उपलब्ध नहीं हैं।",
    noMatchRecords: "मौजूदा फ़िल्टर से कोई आकलन मेल नहीं खाता।",
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
  },
  Bengali: {
    workspaceTab: "মূল্যায়ন কর্মক্ষেত্র",
    analyticsTab: "বিশ্লেষণ কেন্দ্র",
    recordsTab: "রেকর্ড ও রিপোর্ট",
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
    narrativeLabel: "ব্যক্তি কেমন অনুভব করছেন তা বর্ণনা করুন",
    narrativePlaceholder: "উদাহরণ: আমি ক্লান্ত, বিচ্ছিন্ন, উদ্বিগ্ন এবং ঠিকমতো ঘুমাতে পারছি না।",
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
    analyticsBannerDefault: "বিস্তারিত বিশ্লেষণ দেখতে মূল্যায়ন সম্পূর্ণ করে সংরক্ষণ করুন।",
    recordsBannerDefault: "পুরোনো রিপোর্ট দেখতে বা ডাউনলোড করতে মূল্যায়ন আইডি দিয়ে রেকর্ড আনুন।",
    analyticsReady: "এর বিস্তারিত অংশভিত্তিক বিশ্লেষণ প্রস্তুত।",
    savedMessage: "ব্যাকএন্ড API-এর মাধ্যমে সংরক্ষিত হয়েছে।",
    analyticsShowing: "Analytics Hub এখন এই মূল্যায়ন দেখাচ্ছে",
    saveInProgress: "Python NLP ব্যাকএন্ডের মাধ্যমে মূল্যায়ন সংরক্ষণ করা হচ্ছে...",
    previewRefreshing: "Python NLP ব্যাকএন্ড থেকে লাইভ প্রিভিউ আপডেট করা হচ্ছে...",
    noRecordSelected: "কোনো মূল্যায়ন নির্বাচন করা হয়নি।",
    assessmentIdLabel: "মূল্যায়ন আইডি",
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
    questionnaireRiskTitle: "প্রশ্নমালার ঝুঁকি",
    questionnaireOverall: "প্রশ্নমালার সামগ্রিক স্কোর",
    combinedResultTitle: "সমন্বিত ড্যাশবোর্ড ফলাফল",
    confidenceLabel: "কনফিডেন্স",
    recommendationLabel: "পরামর্শ",
    questionnaireLabel: "প্রশ্নমালা",
    dashboardLabel: "ড্যাশবোর্ড",
    noDataModality: "এই ইনপুট উৎসের জন্য কোনো তথ্য পাওয়া যায়নি।",
    availableLabel: "উপলব্ধ",
    uploadReceivedLabel: "আপলোড পাওয়া গেছে, তবে বিশ্লেষণযোগ্য নয়",
    notAvailableLabel: "উপলব্ধ নয়",
    noFeaturesLabel: "এই রেকর্ডের জন্য কোনো কাঁচা ফিচার মান সংরক্ষিত নেই।",
    noMatchRecords: "বর্তমান ফিল্টারের সাথে কোনো মূল্যায়ন মেলেনি।",
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
};

const elements = {
  tabButtons: [...document.querySelectorAll(".tab-btn")],
  viewSections: [...document.querySelectorAll(".view-section")],
  dashboardLanguage: document.getElementById("dashboardLanguage"),
  applyLanguageBtn: document.getElementById("applyLanguageBtn"),
  questionnaireContainer: document.getElementById("questionnaireContainer"),
  assessmentForm: document.getElementById("assessmentForm"),
  saveAssessmentBtn: document.getElementById("saveAssessmentBtn"),
  resetAssessmentBtn: document.getElementById("resetAssessmentBtn"),
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
  analysisOverallRisk: document.getElementById("analysisOverallRisk"),
  riskDistribution: document.getElementById("riskDistribution"),
  submissionTrend: document.getElementById("submissionTrend"),
  riskHotspots: document.getElementById("riskHotspots"),
  nlpTrends: document.getElementById("nlpTrends"),
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
};

function safeRecords(payload) {
  return Array.isArray(payload) ? payload : [];
}

function emptyScores() {
  return Object.fromEntries(DOMAINS.map((domain) => [domain, 0]));
}

function emptyRisks() {
  return Object.fromEntries(DOMAINS.map((domain) => [domain, "unknown"]));
}

function normalizeRecord(record) {
  const safeRecord = record || {};
  const questionnaire = safeRecord.questionnaire || {};
  const overall = safeRecord.multimodal?.overall || {};
  const scores = overall.scores || {};
  const normalizedQuestionnaire = {
    available: questionnaire.available ?? true,
    overall_score: Number(questionnaire.overall_score || 0),
    notes: questionnaire.notes || "No questionnaire notes available.",
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
    profile: {
      full_name: safeRecord.profile?.full_name || "",
      age: Number(safeRecord.profile?.age || 0),
      gender: safeRecord.profile?.gender || "Prefer not to say",
      village: safeRecord.profile?.village || "",
      phone: safeRecord.profile?.phone || "",
      assessor: safeRecord.profile?.assessor || "",
      language: safeRecord.profile?.language || "English",
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
  };
}

function normalizeText(value) {
  return String(value || "").trim().toLowerCase();
}

function currentLanguage() {
  return elements.dashboardLanguage?.value || elements.language?.value || "English";
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

function questionPrompt(question) {
  return QUESTION_TRANSLATIONS[question.id]?.[currentLanguage()] || question.prompt;
}

function questionSectionLabel(section) {
  return SECTION_TRANSLATIONS[section]?.[currentLanguage()] || section;
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

function applyLanguage() {
  if (elements.language && elements.language.value !== currentLanguage()) {
    elements.language.value = currentLanguage();
  }
  setNodeText('.tab-btn[data-view="workspaceView"]', t("workspaceTab"));
  setNodeText('.tab-btn[data-view="analyticsView"]', t("analyticsTab"));
  setNodeText('.tab-btn[data-view="recordsView"]', t("recordsTab"));
  setNodeText(".language-switcher label", currentLanguage() === "Hindi" ? "डैशबोर्ड भाषा" : currentLanguage() === "Bengali" ? "ড্যাশবোর্ড ভাষা" : "Dashboard language");
  setNodeText("#applyLanguageBtn", currentLanguage() === "Hindi" ? "भाषा लागू करें" : currentLanguage() === "Bengali" ? "ভাষা প্রয়োগ করুন" : "Apply Language");
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
  setLabelText(elements.fullName, t("fullNameLabel"));
  setLabelText(elements.age, t("ageLabel"));
  setLabelText(elements.gender, t("genderLabel"));
  setLabelText(elements.village, t("villageLabel"));
  setLabelText(elements.phone, t("phoneLabel"));
  setLabelText(elements.assessor, t("assessorLabel"));
  setLabelText(elements.language, t("languageLabel"));
  setCheckboxLabel(elements.consent, t("consentLabel"));
  setLabelText(elements.textNarrative, t("narrativeLabel"));
  elements.textNarrative.placeholder = t("narrativePlaceholder");
  setNodeText(".form-grid .form-card:nth-child(2) .capture-card:nth-of-type(1) .capture-head strong", t("guidedSpeechTitle"));
  setNodeText(".form-grid .form-card:nth-child(2) .capture-card:nth-of-type(1) .capture-head .capture-topic", t("guidedSpeechTopic"));
  setLabelText(elements.audioFile, t("audioFileLabel"));
  setNodeText(".form-grid .form-card:nth-child(2) .capture-card:nth-of-type(2) .capture-head strong", t("liveFaceTitle"));
  setNodeText(".form-grid .form-card:nth-child(2) .capture-card:nth-of-type(2) .capture-head .capture-topic", t("liveFaceTopic"));
  setLabelText(elements.imageFile, t("imageFileLabel"));
  setNodeText(".questionnaire-card h3", t("questionnaireTitle"));
  setNodeText(".questionnaire-card .section-heading p", t("questionnaireSubtitle"));
  setNodeText(".action-row .primary-btn", t("saveAssessmentBtn"));
  setNodeText(".action-row .ghost-btn", t("resetAssessmentBtn"));
  setNodeText("#workspaceView .section-heading h2", t("workspaceTab"));
  setNodeText("#workspaceView .section-heading p", currentLanguage() === "Hindi" ? "डैशबोर्ड से सीधे नया स्क्रीनिंग रिकॉर्ड बनाएं।" : currentLanguage() === "Bengali" ? "ড্যাশবোর্ড থেকেই নতুন স্ক্রিনিং রেকর্ড তৈরি করুন।" : "Create a new screening record directly from the dashboard.");
  setNodeText("#analyticsView .section-heading h2", t("analyticsTab"));
  setNodeText("#analyticsView .section-heading p", t("detailAnalysisTitle"));
  setNodeText("#recordsView .section-heading h2", t("recordsTab"));
  setNodeText("#recordsView .section-heading p", t("recordsHeadingText"));
  setNodeText("#fetchRecordBtn", t("fetchRecordBtn"));
  setNodeText("#downloadSelectedPdfBtn", t("downloadPdfBtn"));
  elements.recordLookup.placeholder = t("recordLookupPlaceholder");
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
  setNodeText("#recordsView .table-section .section-heading h2", t("recordsExplorerTitle"));
  setNodeText("#recordsView .table-section .section-heading p", t("recordsExplorerText"));
  setNodeText("#recordsView .detail-grid:nth-of-type(4) .panel:nth-child(1) .section-heading h2", t("assessmentDetailTitle"));
  setNodeText("#recordsView .detail-grid:nth-of-type(4) .panel:nth-child(1) .section-heading p", t("assessmentDetailText"));
  setNodeText("#recordsView .detail-grid:nth-of-type(4) .panel:nth-child(2) .section-heading h2", t("scoreComparisonTitle"));
  setNodeText("#recordsView .detail-grid:nth-of-type(4) .panel:nth-child(2) .section-heading p", t("scoreComparisonText"));
  setNodeText("#recordsView .detail-grid:nth-of-type(5) .panel:nth-child(1) .section-heading h2", t("modalityBreakdownTitle"));
  setNodeText("#recordsView .detail-grid:nth-of-type(5) .panel:nth-child(1) .section-heading p", t("modalityBreakdownText"));
  setNodeText("#recordsView .detail-grid:nth-of-type(5) .panel:nth-child(2) .section-heading h2", t("featureSnapshotTitle"));
  setNodeText("#recordsView .detail-grid:nth-of-type(5) .panel:nth-child(2) .section-heading p", t("featureSnapshotText"));
}

function applyDashboardLanguageSelection() {
  buildQuestionnaire();
  wireQuestionnaireEvents();
  applyLanguage();
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
  state.allResults = safeRecords(records)
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
        <p>${questionPrompt(question)}</p>
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
    language: elements.language.value,
    consent_received: elements.consent.checked,
  };
}

function buildAssessmentPayload() {
  const questionnaireResponses = collectQuestionnaireResponses();
  const questionnaire = scoreQuestionnaire(questionnaireResponses);
  return {
    profile: buildProfilePayload(),
    questionnaire,
    text_input: elements.textNarrative.value,
    audio_metadata: buildUploadMetadata(getCurrentAudioFile()),
    image_metadata: buildUploadMetadata(getCurrentImageFile()),
  };
}

function buildAssessmentFormData(payload) {
  const formData = new FormData();
  formData.append("profile", JSON.stringify(payload.profile));
  formData.append("questionnaire", JSON.stringify(payload.questionnaire));
  formData.append("text_input", payload.text_input || "");
  if (getCurrentAudioFile()) {
    formData.append("audio_file", getCurrentAudioFile());
  }
  if (getCurrentImageFile()) {
    formData.append("image_file", getCurrentImageFile());
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
    "Rural Mental Health Screening Dashboard Report",
    `Assessment ID: ${record.assessment_id}`,
    `Created At: ${record.created_at}`,
    `Candidate: ${record.profile.full_name || "Unnamed user"}`,
    `Village: ${record.profile.village || "Unknown"}`,
    `Assessor: ${record.profile.assessor || "Unknown"}`,
    "",
  ];
  DOMAINS.forEach((domain) => {
    lines.push(`${DOMAIN_LABELS[domain]} Questionnaire: ${record.questionnaire[`${domain}_risk`]}`);
    lines.push(`${DOMAIN_LABELS[domain]} Dashboard: ${record.multimodal.overall[domain]}`);
  });
  lines.push("");
  lines.push(`Recommendation: ${record.multimodal.recommendation}`);

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
    bannerMessage: `Loaded ${safeRecords(records).length} assessment records from ${sourceLabel}.`,
    bannerTone: "success",
  });
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
  return state.selectedRecord || state.latestCreatedRecord || state.filteredResults[0] || null;
}

function strongestDomain(record) {
  if (!record) return null;
  return DOMAINS
    .map((domain) => ({ domain, score: Number(record.multimodal?.overall?.scores?.[domain] || 0) }))
    .sort((left, right) => right.score - left.score)[0]?.domain || null;
}

function overallRiskLabel(record) {
  if (!record) return "No data";
  const levels = DOMAINS.map((domain) => record.multimodal?.overall?.[domain] || "low");
  if (levels.includes("high")) return "High";
  if (levels.includes("moderate")) return "Moderate";
  return "Low";
}

function renderOverview() {
  const record = getAnalysisRecord();
  if (!record) {
    elements.analysisAssessmentId.textContent = "No data";
    elements.analysisConfidence.textContent = "0%";
    elements.analysisStrongestDomain.textContent = "No data";
    elements.analysisCoverage.textContent = "0/3";
    elements.analysisSubmissionTime.textContent = "No data";
    elements.analysisOverallRisk.textContent = "No data";
    setBanner(elements.analysisStatusBanner, t("analyticsBannerDefault"), "neutral");
    return;
  }

  const modalitiesUsed = ["text", "audio", "image"].filter((key) => record.multimodal?.[key]?.available).length;
  const dominant = strongestDomain(record);
  elements.analysisAssessmentId.textContent = record.assessment_id;
  elements.analysisConfidence.textContent = formatPercent(record.multimodal?.overall?.confidence || 0);
  elements.analysisStrongestDomain.textContent = dominant ? DOMAIN_LABELS[dominant] : "No data";
  elements.analysisCoverage.textContent = `${modalitiesUsed}/3`;
  elements.analysisSubmissionTime.textContent = formatDate(record.created_at);
  elements.analysisOverallRisk.textContent = overallRiskLabel(record);
  setBanner(elements.analysisStatusBanner, `${record.profile?.full_name || "Current user"}: ${t("analyticsReady")}`, "success");
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
      <div class="score-header"><span>${DOMAIN_LABELS[domain]}</span><strong>${(record.multimodal?.overall?.[domain] || "low").toUpperCase()}</strong></div>
      ${scoreLine("Questionnaire", Number(record.questionnaire?.[`${domain}_score`] || 0))}
      ${scoreLine("Combined AI", Number(record.multimodal?.overall?.scores?.[domain] || 0))}
    </div>
  `).join("");

  elements.riskDistribution.className = "chart-stack";
  elements.riskDistribution.innerHTML = buildChartCard(
    "Domain Score Comparison",
    "Questionnaire score versus combined AI score",
    comparisonCards,
    "This section compares self-reported symptoms with the final multimodal backend score for each condition."
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
        <div class="detail-inline"><h3>${modality.charAt(0).toUpperCase() + modality.slice(1)}</h3><strong>${payload.available ? "Usable" : "Limited"}</strong></div>
        ${scoreLine("Confidence", Number(payload.confidence || 0))}
        <p class="detail-muted">${payload.notes || "No modality note available."}</p>
        <p class="detail-muted">${metadata.join(" | ") || "No additional processing statistics available."}</p>
      </div>
    `;
  }).join("");

  elements.riskHotspots.className = "chart-stack";
  elements.riskHotspots.innerHTML = buildChartCard(
    "Modality Quality",
    "Availability, confidence, and processing quality",
    cards,
    "Use this section to understand which inputs were strong enough to support the final decision."
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
    "Recommendation And Disclaimer",
    overallRiskLabel(record),
    `
      <div class="detail-card">
        <h3>Recommendation</h3>
        <p>${record.multimodal?.recommendation || "No recommendation available."}</p>
      </div>
      <div class="detail-card">
        <h3>Screening Disclaimer</h3>
        <p>${record.multimodal?.disclaimer || "No disclaimer available."}</p>
      </div>
    `,
    "This area gives the end user the screening interpretation and the appropriate follow-up note."
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
    elements.villageSummary.textContent = "No trained model bundle statistics are available for this assessment yet.";
    return;
  }

  const summaryCards = [
    { label: "Text transformer", value: textFeatures.transformer_model || "Unavailable" },
    { label: `${t("sentimentLabel")} engine`, value: textFeatures.sentiment_model || "Unavailable" },
    { label: `${t("emotionLabel")} engine`, value: textFeatures.emotion_model || "Unavailable" },
    { label: "Trained modalities", value: `${availableRows.length}/3` },
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
      <div class="detail-inline"><h3>${item.label}</h3><strong>${item.source === "trained_bundle" ? "Trained bundle" : "Fallback"}</strong></div>
      ${scoreLine("Confidence Hint", item.confidenceHint)}
      <p class="detail-muted">Macro R2: ${formatMetricNumber(item.macroR2, 3)}</p>
      <p class="detail-muted">Samples: ${item.sampleCount}</p>
      <p class="detail-muted">Domains: ${item.domains.length ? item.domains.map((domain) => DOMAIN_LABELS[domain] || domain).join(", ") : "Unavailable"}</p>
      <p class="detail-muted">Manifest: ${formatCompactPath(item.manifestPath)}</p>
      <p class="detail-muted">Dataset root: ${formatCompactPath(item.datasetRoot)}</p>
      <p class="detail-muted">Trained at: ${item.trainedAt === "Unavailable" ? "Unavailable" : formatDate(item.trainedAt)}</p>
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
      "Trained Bundle Comparison",
      "Macro R2 and sample coverage by modality",
      metricChart,
      "This compares the locally trained bundle quality for text, audio, and image using the current saved model metadata."
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
    { label: t("sentimentLabel"), value: features.sentiment_label || "Unknown" },
    { label: t("emotionLabel"), value: features.dominant_emotion || "Unknown" },
    { label: "Safety keywords", value: features.self_harm_keyword_detected ? "Detected" : "Not detected" },
    { label: "Keyword matches", value: (features.self_harm_keyword_matches || []).join(", ") || "None" },
    { label: "Narrative word count", value: features.word_count || 0 },
    { label: `${t("emotionLabel")} intensity`, value: Number(features.emotion_intensity || 0).toFixed(2) },
    { label: "Trained modalities", value: modelRows.length || 0 },
    { label: "Domain coverage", value: trainedDomainTotal || 0 },
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
        <td>${record.profile?.full_name || "Unnamed user"}</td>
        <td>${record.profile?.village || "Unknown"}</td>
        <td>${record.profile?.assessor || "Unknown"}</td>
        <td>${formatDate(record.created_at)}</td>
        <td><span class="risk-pill ${level}">${DOMAIN_LABELS[domain]} ${level}</span></td>
        <td>${formatPercent(record.multimodal?.overall?.confidence || 0)}</td>
      </tr>
    `;
  }).join("");
  elements.resultsTableBody.querySelectorAll("[data-id]").forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedRecord = state.filteredResults.find((record) => record.assessment_id === row.dataset.id) || null;
      renderDetailPanels();
      renderTable();
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
  const questionnairePills = DOMAINS.map((domain) => `<span class="risk-pill ${record.questionnaire[`${domain}_risk`]}">${DOMAIN_LABELS[domain]} ${record.questionnaire[`${domain}_risk`]}</span>`).join("");
  const overallPills = DOMAINS.map((domain) => `<span class="risk-pill ${record.multimodal.overall[domain]}">${DOMAIN_LABELS[domain]} ${record.multimodal.overall[domain]}</span>`).join("");
  elements.selectedAssessment.className = "detail-stack";
  elements.selectedAssessment.innerHTML = `
    <div class="detail-card">
      <div class="detail-inline"><h3>${record.profile.full_name || "Unnamed user"}</h3><strong>${record.assessment_id}</strong></div>
      <p class="detail-muted">${record.profile.village || "Unknown location"} | Age ${record.profile.age || "N/A"} | ${record.profile.gender || "Not stated"}</p>
      <p class="detail-muted">Assessor: ${record.profile.assessor || "N/A"} | Language: ${record.profile.language || "N/A"} | Contact: ${record.profile.phone || "N/A"}</p>
      <p class="detail-muted">Submitted: ${formatDate(record.created_at)}</p>
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
      ${DOMAINS.map((domain) => scoreLine(`${DOMAIN_LABELS[domain]} Score`, record.multimodal.overall.scores[domain])).join("")}
    </div>
    <div class="detail-card">
      <h3>${t("recommendationLabel")}</h3>
      <p>${record.multimodal.recommendation}</p>
      <p class="detail-muted">${record.multimodal.disclaimer}</p>
    </div>
  `;
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
    ${DOMAINS.map((domain) => comparisonRow(DOMAIN_LABELS[domain], record.questionnaire[`${domain}_score`], record.multimodal.overall.scores[domain])).join("")}
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
    modalityCard("Text", record.multimodal.text),
    modalityCard("Audio", record.multimodal.audio),
    modalityCard("Image", record.multimodal.image),
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
      const items = Object.entries(record.multimodal[key].features).map(([name, value]) => `<li>${name}: ${Array.isArray(value) ? value.join(", ") : value}</li>`).join("");
      return `<div class="feature-card"><h3>${key.charAt(0).toUpperCase() + key.slice(1)} Features</h3><ul class="feature-list">${items}</ul></div>`;
    });
  if (!featureCards.length) {
    elements.featureSnapshot.className = "empty-state";
    elements.featureSnapshot.textContent = t("noFeaturesLabel");
    return;
  }
  elements.featureSnapshot.className = "feature-grid";
  elements.featureSnapshot.innerHTML = featureCards.join("");
}

function renderDetailPanels() {
  renderSelectedAssessment();
  renderScoreComparison();
  renderModalityBreakdown();
  renderFeatureSnapshot();
}

function renderWorkspacePanels() {
  const record = state.draftRecord || state.latestCreatedRecord;
  if (state.draftPreviewLoading && !state.draftRecord) {
    elements.workspacePrediction.className = "empty-state";
    elements.workspacePrediction.textContent = t("previewRefreshing");
    elements.workspaceNlp.className = "empty-state";
    elements.workspaceNlp.textContent = t("previewRefreshing");
    elements.workspaceReadiness.className = "empty-state";
    elements.workspaceReadiness.textContent = t("previewRefreshing");
    return;
  }
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
      ${DOMAINS.map((domain) => scoreLine(`${DOMAIN_LABELS[domain]} Score`, record.multimodal.overall.scores[domain])).join("")}
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
  renderTable();
  renderDetailPanels();
  renderWorkspacePanels();
}

function switchView(viewId) {
  elements.tabButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewId);
  });
  elements.viewSections.forEach((section) => {
    section.classList.toggle("is-hidden", section.id !== viewId);
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
  elements.assessmentForm.reset();
  QUESTION_BANK.forEach((question) => {
    const radio = document.querySelector(`input[name="${question.id}"][value="0"]`);
    if (radio) radio.checked = true;
  });
  clearSpeechRecording();
  clearCapturedPhoto();
  stopWebcam();
  clearUploadedMediaInputs();
  updateCaptureUi();
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
    state.latestCreatedRecord = savedRecord;
    state.draftRecord = null;
    setActiveResults([savedRecord], {
      focusLatest: true,
      bannerMessage: `${t("analyticsShowing")} ${savedRecord.assessment_id}.`,
      bannerTone: "success",
    });
    setBanner(elements.workspaceStatus, `${t("assessmentIdLabel")} ${savedRecord.assessment_id} ${t("savedMessage")}`, "success");
    switchView("analyticsView");
  } catch (error) {
    console.error("Assessment save failed", error);
    setBanner(elements.workspaceStatus, currentLanguage() === "Bengali" ? "ব্যাকএন্ড API-তে মূল্যায়ন সংরক্ষণ করা যায়নি।" : currentLanguage() === "Hindi" ? "आकलन बैकएंड API में सहेजा नहीं जा सका।" : "Could not save the assessment to the backend API.", "error");
  }
}

async function fetchDraftPreview(payload, requestId) {
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
    state.draftPreviewLoading = false;
    setBanner(elements.workspaceStatus, currentLanguage() === "Bengali" ? "ব্যাকএন্ড থেকে লাইভ NLP বিশ্লেষণ আপডেট করা যায়নি।" : currentLanguage() === "Hindi" ? "बैकएंड से लाइव NLP संकेत ताज़ा नहीं किए जा सके।" : "Could not refresh live NLP insights from the backend.", "error");
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
  state.draftPreviewLoading = true;
  renderWorkspacePanels();
  state.draftPreviewTimer = setTimeout(() => {
    fetchDraftPreview(payload, requestId);
  }, 250);
}

async function loadDefaultResults() {
  try {
    await loadApiResults("backend API");
  } catch {
    setBanner(elements.statusBanner, currentLanguage() === "Bengali" ? "ব্যাকএন্ড API থেকে রেকর্ড লোড করা যায়নি। প্রয়োজনে JSON ফাইল ম্যানুয়ালি আনুন।" : currentLanguage() === "Hindi" ? "बैकएंड API से रिकॉर्ड लोड नहीं हो सके। आवश्यकता हो तो JSON फाइल मैन्युअली आयात करें।" : "Could not load records from the backend API. Import a JSON file manually instead.", "error");
  }
}

async function loadSampleResults() {
  try {
    const response = await fetch("/api/sample", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    loadResults(await response.json(), "the bundled sample dataset");
  } catch {
    setBanner(elements.statusBanner, currentLanguage() === "Bengali" ? "স্যাম্পল ডেটাসেট লোড করা যায়নি।" : currentLanguage() === "Hindi" ? "सैंपल डाटासेट लोड नहीं हो सका।" : "Could not load the sample dataset.", "error");
  }
}

function loadBrowserResults() {
  loadApiResults("backend API");
}

async function loadApiResults(sourceLabel, focusLatest = false) {
  try {
    const response = await fetch("/api/assessments", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    loadResults(await response.json(), sourceLabel, focusLatest);
  } catch (error) {
    console.error("API load failed", error);
    setBanner(elements.statusBanner, currentLanguage() === "Bengali" ? "ব্যাকএন্ড API থেকে রেকর্ড লোড করা যায়নি।" : currentLanguage() === "Hindi" ? "बैकएंड API से रिकॉर्ड लोड नहीं हो सके।" : "Could not load records from the backend API.", "error");
  }
}

function exportFilteredResults() {
  if (!state.filteredResults.length) {
    setBanner(elements.statusBanner, "There are no filtered records to export.", "error");
    return;
  }
  const blob = new Blob([JSON.stringify(state.filteredResults, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "dashboard-filtered-records.json";
  link.click();
  URL.revokeObjectURL(url);
  setBanner(elements.statusBanner, `Exported ${state.filteredResults.length} filtered records.`, "success");
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
    renderDetailPanels();
    renderTable();
    setBanner(elements.statusBanner, tf("fetchSuccess", { id: record.assessment_id }), "success");
  } catch (error) {
    console.error("Record fetch failed", error);
    setBanner(elements.statusBanner, t("fetchMissing"), "error");
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

elements.tabButtons.forEach((button) => {
  button.addEventListener("click", () => switchView(button.dataset.view));
});

elements.assessmentForm.addEventListener("submit", submitAssessment);
elements.resetAssessmentBtn.addEventListener("click", () => {
  resetAssessmentForm();
  updateDraftPreview();
});
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

buildQuestionnaire();
wireQuestionnaireEvents();
applyLanguage();
updateCaptureUi();
resetAssessmentForm();
loadInitialBrowserRecords();
updateDraftPreview();
