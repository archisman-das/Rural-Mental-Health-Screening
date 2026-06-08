# Deep Learning Model Guide

This document explains the deep learning models and model families mentioned in the project, how each one works at a high level, and how it is used inside the Rural Mental Health Screening AI system.

The goal is to make the model stack easy to understand for developers, researchers, and paper authors. It separates:

- true deep learning components
- supporting computer-vision or classical fallback components
- downstream classifiers that consume learned features

## 1. Model Stack Overview

The project uses a multimodal screening pipeline:

1. Text is encoded with transformer models such as BERT, DistilBERT, MuRIL, and IndicBERT.
2. Audio is processed with speech models such as wav2vec2 and Whisper.
3. Face images are processed with MediaPipe Face Mesh and an OpenCV fallback when needed.
4. The extracted representations are passed into downstream screening heads for depression, anxiety, stress, sleep disorder, burnout, loneliness, and substance abuse risk estimation.

The deep learning models are not used as isolated black boxes. They are part of a larger workflow that combines multilingual NLP, speech understanding, and visual feature extraction.

## 2. Text Models

### 2.1 BERT

**What it is**

BERT stands for Bidirectional Encoder Representations from Transformers. It is a transformer encoder trained to understand text in both left-to-right and right-to-left context at the same time.

**Working principle**

- Text is first split into tokens.
- Each token is converted into an embedding vector.
- Self-attention layers let every token attend to the other tokens in the sequence.
- The model learns contextual meaning instead of treating words independently.

**Why it matters in this project**

BERT is useful for screening text because user narratives often contain indirect expressions, mood cues, and mixed symptom descriptions. The contextual encoding helps the system interpret phrases such as:

- "I cannot sleep properly"
- "I feel exhausted and worried"
- "I do not feel like talking to anyone"

**How the project uses it**

The repository uses English BERT-family encoders as part of the text feature extraction path when local transformer support is available. Those encoders produce contextual vectors that are then passed into downstream classifiers.

### 2.2 DistilBERT

**What it is**

DistilBERT is a compressed version of BERT designed to be faster and lighter while retaining much of BERT's language understanding ability.

**Working principle**

DistilBERT is trained through knowledge distillation. A smaller student model learns to imitate a larger teacher model, which reduces size and latency while keeping useful contextual representations.

**Why it matters in this project**

The dashboard may run in resource-constrained environments. DistilBERT is a practical option when the system needs:

- lower inference latency
- lower memory usage
- acceptable performance for English text

**How the project uses it**

The text pipeline lists DistilBERT as one of the English encoder options. It is especially helpful when the application must remain responsive on modest hardware.

### 2.3 MuRIL

**What it is**

MuRIL is a multilingual transformer model built for Indian languages and code-mixed text.

**Working principle**

MuRIL learns cross-lingual and transliteration-aware representations. That means it can better handle:

- native scripts
- transliterated Indian-language text
- code-mixed phrasing

**Why it matters in this project**

Mental health screening in rural settings often involves language mixing, informal grammar, and expressions that do not map cleanly to standard English. MuRIL helps the system handle Hindi and Bengali inputs more naturally.

**How the project uses it**

MuRIL is included as a native-language transformer option for Hindi and Bengali text analysis. It supports multilingual encoding before the downstream screening logic runs.

### 2.4 IndicBERT

**What it is**

IndicBERT is another transformer model family designed for Indian languages.

**Working principle**

IndicBERT uses transformer self-attention, just like BERT, but it is adapted for Indian-language coverage. It is intended to learn useful representations from scripts and vocabulary patterns common across Indian languages.

**Why it matters in this project**

The system must remain useful for Hindi and Bengali speakers. IndicBERT helps preserve meaning in language-specific input rather than forcing all text into an English-centric representation.

**How the project uses it**

IndicBERT is listed in the repo as a supported text encoder for Hindi and Bengali, either as a primary encoder or as a fallback option when another local model is not available.

### 2.5 Text Pipeline Functionality

In this project, the text models do more than generic sentiment analysis. They support:

- symptom and distress interpretation
- contextual screening heuristics
- emotion and sentiment enrichment
- safety-related phrase detection
- multilingual understanding for English, Hindi, and Bengali

The pipeline typically works as follows:

1. User text is normalized.
2. The text is tokenized.
3. The transformer encoder generates contextual embeddings.
4. A lightweight screening head or scoring layer turns embeddings into model outputs.
5. If the transformer stack is unavailable, the application falls back to heuristic features so the dashboard still functions.

## 3. Audio Models

### 3.1 wav2vec2

**What it is**

wav2vec2 is a self-supervised speech representation model. It learns from raw audio waveforms instead of requiring hand-crafted acoustic features only.

**Working principle**

- The audio waveform is encoded into latent speech representations.
- The model learns patterns from speech structure using contrastive objectives.
- During fine-tuning, the learned speech features are adapted to transcription or classification tasks.

**Why it matters in this project**

Speech is important in rural screening because many users may prefer voice input over typing. wav2vec2 helps the system understand speech from Bengali and Hindi speakers, including dialect variation.

**How the project uses it**

The repository supports wav2vec2 as a fine-tuning family for rural speech. It can be configured for dialect-specific training and uses local cached checkpoints when available.

Typical use cases in this repo:

- speech-to-text transcription
- dialect-aware adaptation
- transcription support for downstream mental health screening

### 3.2 Whisper

**What it is**

Whisper is a multilingual speech recognition model that maps audio to text using an encoder-decoder architecture.

**Working principle**

- The audio is converted into a learned representation.
- The decoder generates the transcript token by token.
- The model is trained on large and diverse speech-text pairs, which makes it robust to accents, noise, and varied speaking styles.

**Why it matters in this project**

Whisper is useful when the user speaks in real-world conditions that are not perfectly clean. It is a strong fit for community screening environments where recording quality can vary.

**How the project uses it**

The repo includes Whisper as an alternative speech family alongside wav2vec2. It can be fine-tuned for Bengali and Hindi speech and selected through the voice training pipeline.

### 3.3 Audio Pipeline Functionality

The audio workflow typically follows this sequence:

1. A voice clip is uploaded or captured.
2. The selected ASR model converts speech to text.
3. The transcript is passed into the text screening logic.
4. The system can also attach modality quality metadata to show whether audio was usable, partial, or weak.

This design keeps the system flexible. Even when a voice model is not available, the assessment can still proceed through text and questionnaire inputs.

## 4. Vision and Image Models

### 4.1 MediaPipe Face Mesh

**What it is**

MediaPipe Face Mesh is a landmark detection system for faces. It predicts dense facial keypoints rather than only detecting the face bounding box.

**Working principle**

- The image is normalized and passed through the facial landmark detector.
- The model returns facial mesh coordinates.
- Those coordinates can be turned into derived measurements such as facial geometry, eye openness, and other visual signals.

**Why it matters in this project**

The system uses image inputs as one more modality for screening support. Face landmark extraction helps build lightweight visual features without needing a heavyweight custom image classifier for every case.

**How the project uses it**

The feature extraction path uses `MediaPipe Face Mesh` in static image mode when available. The implementation reports the backend as `mediapipe_face_mesh` when that route succeeds.

### 4.2 OpenCV Haar Fallback

**What it is**

OpenCV Haar cascades are classical computer-vision detectors, not deep learning models.

**Why it is included**

The project uses Haar-based face detection as a fallback when the primary face mesh pipeline cannot run. This improves robustness in low-dependency or partially configured environments.

**How the project uses it**

If the face mesh route is unavailable, the system can still detect or crop a face region using Haar-based detection so that downstream processing is not blocked.

## 5. Supporting Data Sources

These are not models, but they matter because they shape how the models learn:

- **MELD**: used for proxy text supervision and emotion-aligned language patterns.
- **RAVDESS**: used for proxy audio and image supervision.
- **DAIC-WOZ**: used as the clinical supervision source for more realistic depression-oriented training and evaluation.

These datasets help the project bridge the gap between broad representation learning and clinically relevant screening behavior.

## 6. Downstream Screening Heads

The repository also contains downstream trained bundles that sit on top of the deep learning feature extractors.

Important note:

- these downstream bundles are not themselves deep learning models
- they are usually classical estimators or lightweight classifier heads
- they consume embeddings, transcript features, and modality summaries

In other words, the deep learning models do the representation learning, and the screening heads do the final risk estimation and aggregation.

## 7. Multimodal Decision Flow

The final assessment is built from several signals:

- questionnaire scores
- text embeddings and safety signals
- audio transcript or audio-derived features
- image-derived facial signals
- modality quality and confidence indicators

This multimodal design is important because mental health screening in the field is rarely supported by one perfect input. The system therefore combines multiple weak-to-moderate signals into one practical screening outcome.

## 8. Practical Behavior in the App

The app does not depend on every model being available at runtime.

If a transformer or speech checkpoint is not installed locally, the application:

- falls back to lighter heuristic logic
- keeps the assessment flow working
- preserves saved records and reports

This means the project is robust enough for development machines, demo environments, and partially configured deployments.

## 9. Research and Paper Writing Notes

When you describe this system in a paper, it is useful to separate the model families by function:

- **Text understanding**: BERT, DistilBERT, MuRIL, IndicBERT
- **Speech understanding**: wav2vec2, Whisper
- **Vision landmarks**: MediaPipe Face Mesh
- **Fallback vision support**: OpenCV Haar cascades

That separation makes the methodology section clearer and avoids mixing representation-learning models with downstream decision heads.

## 10. Recommended Citation Targets

For academic writing, this document should be paired with the references already present in `paper/references.bib`, especially for:

- MuRIL
- RAVDESS
- PHQ-9 and PHQ-4
- any clinical screening references already cited in the manuscript

If you add more model families later, extend this guide so the methodology section stays synchronized with the implementation.
