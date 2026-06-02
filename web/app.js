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
  recordedAudioFile: null,
  capturedImageFile: null,
  mediaRecorder: null,
  mediaChunks: [],
  webcamStream: null,
};

const elements = {
  tabButtons: [...document.querySelectorAll(".tab-btn")],
  viewSections: [...document.querySelectorAll(".view-section")],
  questionnaireContainer: document.getElementById("questionnaireContainer"),
  assessmentForm: document.getElementById("assessmentForm"),
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
      recommendation: safeRecord.multimodal?.recommendation || "No recommendation available.",
      disclaimer: safeRecord.multimodal?.disclaimer || "No disclaimer available.",
    },
  };
}

function normalizeText(value) {
  return String(value || "").trim().toLowerCase();
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
  let currentSection = "";
  const blocks = [];
  QUESTION_BANK.forEach((question) => {
    if (question.section !== currentSection) {
      if (currentSection) {
        blocks.push("</div></section>");
      }
      currentSection = question.section;
      blocks.push(`<section class="question-group"><h4>${currentSection}</h4><div class="question-list">`);
    }
    const choices = RESPONSE_OPTIONS.map((option) => `
      <label class="choice-pill">
        <input type="radio" name="${question.id}" value="${option.value}" ${option.value === 0 ? "checked" : ""}>
        <span>${option.label}</span>
      </label>
    `).join("");
    blocks.push(`
      <div class="question-item">
        <p>${question.prompt}</p>
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
  result.notes = "Dashboard questionnaire scoring reflects symptom frequency over the last two weeks.";
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
    setBanner(elements.analysisStatusBanner, "Complete and save an assessment to open detailed analysis here.", "neutral");
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
  setBanner(elements.analysisStatusBanner, `${record.profile?.full_name || "Current user"}: detailed component-wise analysis is ready.`, "success");
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
      <text x="${startX}" y="${labelY}" class="svg-axis-text">Sentiment balance</text>
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
    elements.riskDistribution.textContent = "No assessment analysis available yet.";
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
    elements.submissionTrend.textContent = "No component breakdown available yet.";
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
    elements.riskHotspots.textContent = "No modality quality information available yet.";
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
    elements.nlpTrends.textContent = "No recommendation details available yet.";
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
    elements.villageSummary.className = "tile-grid empty-state";
    elements.villageSummary.textContent = "No model statistics available yet.";
    return;
  }

  const textFeatures = record.multimodal?.text?.features || {};
  const audioFeatures = record.multimodal?.audio?.features || {};
  const imageFeatures = record.multimodal?.image?.features || {};
  const modelCards = [
    { label: "Transformer model", value: textFeatures.transformer_model || "Unavailable" },
    { label: "Sentiment model", value: textFeatures.sentiment_model || "Unavailable" },
    { label: "Emotion model", value: textFeatures.emotion_model || "Unavailable" },
    { label: "Model source", value: textFeatures.model_source || audioFeatures.model_source || imageFeatures.model_source || "Backend heuristic" },
    { label: "Trained samples", value: textFeatures.trained_samples || audioFeatures.trained_samples || imageFeatures.trained_samples || "N/A" },
    { label: "Macro R²", value: textFeatures.model_macro_r2 ?? audioFeatures.model_macro_r2 ?? imageFeatures.model_macro_r2 ?? "N/A" },
  ];
  elements.villageSummary.className = "tile-grid";
  elements.villageSummary.innerHTML = modelCards.map((item) => `
    <div class="summary-tile">
      <div class="tile-top"><span>${item.label}</span><strong>${item.value}</strong></div>
    </div>
  `).join("");
}

function renderNlpSignalSummary() {
  const record = getAnalysisRecord();
  if (!record) {
    elements.assessorSummary.className = "tile-grid empty-state";
    elements.assessorSummary.textContent = "No NLP signal summary available yet.";
    return;
  }

  const features = record.multimodal?.text?.features || {};
  const cards = [
    { label: "Sentiment", value: features.sentiment_label || "Unknown" },
    { label: "Dominant emotion", value: features.dominant_emotion || "Unknown" },
    { label: "Safety keywords", value: features.self_harm_keyword_detected ? "Detected" : "Not detected" },
    { label: "Keyword matches", value: (features.self_harm_keyword_matches || []).join(", ") || "None" },
    { label: "Narrative word count", value: features.word_count || 0 },
    { label: "Emotion intensity", value: Number(features.emotion_intensity || 0).toFixed(2) },
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
    elements.resultsTableBody.innerHTML = '<tr><td colspan="7" class="table-empty">No assessments match the current filters.</td></tr>';
    elements.pageStatus.textContent = "Page 1 of 1";
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
  elements.pageStatus.textContent = `Page ${state.currentPage} of ${totalPages}`;
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
    elements.selectedAssessment.textContent = "No assessment selected.";
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
      <h3>Questionnaire Risk</h3>
      <div class="detail-inline">${questionnairePills}</div>
      ${scoreLine("Questionnaire Overall", record.questionnaire.overall_score)}
    </div>
    <div class="detail-card">
      <h3>Combined Dashboard Result</h3>
      <div class="detail-inline">${overallPills}</div>
      ${scoreLine("Confidence", record.multimodal.overall.confidence)}
      ${DOMAINS.map((domain) => scoreLine(`${DOMAIN_LABELS[domain]} Score`, record.multimodal.overall.scores[domain])).join("")}
    </div>
    <div class="detail-card">
      <h3>Recommendation</h3>
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
        <div class="score-header"><span>Questionnaire</span><strong>${safeQuestionnaire.toFixed(2)}</strong></div>
        <div class="dual-track"><div class="score-fill dual-fill questionnaire" style="width:${clamp01(safeQuestionnaire) * 100}%"></div></div>
      </div>
      <div class="score-line">
        <div class="score-header"><span>Dashboard</span><strong>${safeMultimodal.toFixed(2)}</strong></div>
        <div class="dual-track"><div class="score-fill dual-fill multimodal" style="width:${clamp01(safeMultimodal) * 100}%"></div></div>
      </div>
    </div>
  `;
}

function renderScoreComparison() {
  const record = state.selectedRecord;
  if (!record) {
    elements.scoreComparison.className = "empty-state";
    elements.scoreComparison.textContent = "No assessment selected.";
    return;
  }
  elements.scoreComparison.className = "compare-grid";
  elements.scoreComparison.innerHTML = `
    <div class="compare-legend">
      <span><span class="legend-dot questionnaire"></span>Questionnaire</span>
      <span><span class="legend-dot multimodal"></span>Dashboard prediction</span>
    </div>
    ${DOMAINS.map((domain) => comparisonRow(DOMAIN_LABELS[domain], record.questionnaire[`${domain}_score`], record.multimodal.overall.scores[domain])).join("")}
  `;
}

function modalityCard(title, payload) {
  const available = payload?.available;
  const uploadReceived = payload?.features?.upload_received;
  const notes = payload?.notes || "No data available for this modality.";
  const statusText = available ? "Available" : uploadReceived ? "Upload Received, Not Analyzable" : "Not available";
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
    elements.modalityBreakdown.textContent = "No assessment selected.";
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
    elements.featureSnapshot.textContent = "No assessment selected.";
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
    elements.featureSnapshot.textContent = "No raw feature values were captured for this record.";
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
    elements.workspacePrediction.textContent = "Refreshing the live preview from the Python NLP backend...";
    elements.workspaceNlp.className = "empty-state";
    elements.workspaceNlp.textContent = "Analyzing sentiment, emotion, self-harm language, and backend domain scores...";
    elements.workspaceReadiness.className = "empty-state";
    elements.workspaceReadiness.textContent = "Checking the current intake while the backend preview is updated.";
    return;
  }
  if (!record) {
    elements.workspacePrediction.className = "empty-state";
    elements.workspacePrediction.textContent = "Start filling the assessment to generate a live prediction preview.";
    elements.workspaceNlp.className = "empty-state";
    elements.workspaceNlp.textContent = "NLP signals will appear here while the narrative is being entered.";
    elements.workspaceReadiness.className = "empty-state";
    elements.workspaceReadiness.textContent = "Fill in candidate details, consent, questionnaire, and narrative to see readiness feedback.";
    return;
  }

  elements.workspacePrediction.className = "detail-stack";
  elements.workspacePrediction.innerHTML = `
    <div class="detail-card">
      <div class="detail-inline"><h3>${record.profile.full_name || "Unnamed user"}</h3><strong>${record.assessment_id}</strong></div>
      <p class="detail-muted">${state.draftRecord ? `Live preview${state.draftPreviewLoading ? " | refreshing..." : ""}` : `Saved at ${formatDate(record.created_at)}`}</p>
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
      <h3>Sentiment</h3>
      <p>${features.sentiment_label || "unknown"} via ${features.sentiment_model || "backend heuristic"}</p>
      <h3>Emotion</h3>
      <p>${features.dominant_emotion || "neutral"} via ${features.emotion_model || "backend heuristic"}</p>
      <h3>Safety Language</h3>
      <p>${features.self_harm_keyword_detected ? `Self-harm keywords detected: ${(features.self_harm_keyword_matches || []).join(", ")}` : "No self-harm keywords detected"}</p>
      <h3>Transformer</h3>
      <p>${features.transformer_model || "unavailable"}</p>
      <h3>Audio Modality</h3>
      <p>${audioStatus.text}</p>
      <h3>Image Modality</h3>
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
      <h3>Readiness Score</h3>
      ${scoreLine("Completion", readinessScore)}
      ${readinessChecks.map((item) => {
        const statusLabel = item.tone === "error"
          ? "Needs attention"
          : item.tone === "success"
            ? "Ready"
            : "Info";
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
    setBanner(elements.workspaceStatus, "Saving assessment through the Python NLP backend...", "neutral");
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
      bannerMessage: `Analytics Hub is now showing assessment ${savedRecord.assessment_id}.`,
      bannerTone: "success",
    });
    setBanner(elements.workspaceStatus, `Assessment ${savedRecord.assessment_id} saved through the backend API.`, "success");
    switchView("analyticsView");
  } catch (error) {
    console.error("Assessment save failed", error);
    setBanner(elements.workspaceStatus, "Could not save the assessment to the backend API.", "error");
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
    setBanner(elements.workspaceStatus, "Could not refresh live NLP insights from the backend.", "error");
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
    setBanner(elements.statusBanner, "Could not load records from the backend API. Import a JSON file manually instead.", "error");
  }
}

async function loadSampleResults() {
  try {
    const response = await fetch("/api/sample", { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    loadResults(await response.json(), "the bundled sample dataset");
  } catch {
    setBanner(elements.statusBanner, "Could not load the sample dataset.", "error");
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
    setBanner(elements.statusBanner, "Could not load records from the backend API.", "error");
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
    setBanner(elements.statusBanner, "Enter an assessment ID before fetching a record.", "error");
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
    setBanner(elements.statusBanner, `Fetched assessment ${record.assessment_id} from the backend API.`, "success");
  } catch (error) {
    console.error("Record fetch failed", error);
    setBanner(elements.statusBanner, "No record matched that assessment ID in the backend API.", "error");
  }
}

function loadInitialBrowserRecords() {
  state.allResults = [];
  state.filteredResults = [];
  state.selectedRecord = null;
  state.currentPage = 1;
  populateFilterOptions();
  renderDashboard();
  setBanner(elements.analysisStatusBanner, "Complete and save an assessment to open detailed analysis here.", "neutral");
  setBanner(elements.statusBanner, "Fetch a saved assessment by ID when you want to review or download an older report.", "neutral");
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
updateCaptureUi();
resetAssessmentForm();
loadInitialBrowserRecords();
updateDraftPreview();
