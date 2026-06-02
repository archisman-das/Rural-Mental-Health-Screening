# Rural Mental Health Screening AI

A prototype for an AI-based rural mental health screening tool designed around a dashboard workflow with questionnaire intake, multimodal AI signals, analytics, saved result retrieval, and PDF reporting.

## Current Prediction Scope

The current implementation predicts:

- Depression
- Anxiety
- Stress
- Sleep disorder
- Burnout
- Loneliness
- Substance abuse

## What is included

- `dashboard_server.py`: Flask backend API that serves the dashboard, saves assessments, fetches records, and generates PDF reports.
- `app.py`: earlier Streamlit prototype interface retained in the repo, but the active product flow is now dashboard-based.
- `src/mental_health_screening/assessment.py`: structured questionnaire definition and questionnaire scoring logic.
- `src/mental_health_screening/feature_extract.py`: feature extraction helpers for text, audio, and image inputs with graceful dependency fallbacks.
- `src/mental_health_screening/predict.py`: rule-based screening heuristics, confidence estimation, and score aggregation.
- `src/mental_health_screening/storage.py`: SQLite-backed assessment storage with JSON cache sync for dashboard compatibility.
- `src/mental_health_screening/report.py`: PDF report generation for saved assessments.
- `src/mental_health_screening/training.py`: training CLI and model-bundle builder for text, audio, and image modalities.
- `src/mental_health_screening/utils.py`: shared utility helpers.

## NLP Layer

The text pipeline now supports:

- DistilBERT / BERT text representations when transformer models are available locally
- Emotion detection
- Sentiment analysis
- Self-harm keyword detection

If transformer packages or model weights are unavailable, the app falls back to lighter heuristic NLP features instead of failing completely.

## Dashboard-First Stack

- Frontend: HTML, CSS, JavaScript dashboard in `web/`
- Backend API: Flask
- Database: SQLite
- Assessment flow: dashboard intake form with questionnaire and live Python NLP preview
- Data exchange: backend persistence plus JSON import/export
- Reporting: backend PDF export

## Dashboard Usage

Run the Flask dashboard server:

```powershell
python dashboard_server.py
```

Then open `http://127.0.0.1:8000/`.

Inside the dashboard you can:

- Create and save assessments directly from the `Assessment Workspace`
- Review trends in the `Analytics Hub`
- Fetch records and export PDF reports from `Records and Reports`
- Persist records through the backend API into the SQLite database

## Setup

1. Create and activate a Python virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Run the dashboard backend.

```powershell
python dashboard_server.py
```

4. Open `http://127.0.0.1:8000/` in your browser.

## Usage

- Open the dashboard and complete the candidate profile, narrative, and symptom questionnaire in `Assessment Workspace`.
- The live workspace now calls the Python backend so preview sentiment, emotion, self-harm detection, and transformer-backed text scoring match the saved analysis path.
- Audio and image uploads are also sent to the backend during preview and save; if dependencies are installed and the media is usable, those modalities contribute real inference instead of metadata-only placeholders.
- Audio must meet a minimum backend duration threshold before it is treated as analyzable, and image analysis requires a detectable face before facial cues are accepted as a live modality signal.
- Save the assessment to generate a persistent `assessment_id` in the backend API and SQLite database.
- Use `Analytics Hub` to filter the saved dataset by assessment ID, candidate name, risk, village, and assessor.
- Use `Records and Reports` to fetch a saved record by `assessment_id`, inspect the detailed result, and download a PDF report.
- Use JSON import/export only when you want to demo, migrate, or share dashboard datasets outside the backend database.

## Notes

This prototype still includes heuristic fallbacks, but the repo now also supports trained bundles from real manifests. At runtime, `predict.py` will use trained domain models when they exist and fall back to heuristics only for domains that are still unlabeled or untrained.

## Training Real Models

The training path now supports two honest stages:

- proxy pretraining from open emotion datasets such as `MELD` and `RAVDESS`
- clinical retraining from `DAIC-WOZ` once you have approved access

### 1. Build manifests from supported datasets

Generate a proxy text manifest from `MELD`:

```powershell
python -m src.mental_health_screening.dataset_prep meld C:\path\to\MELD data\manifests\meld_proxy.csv
```

Generate a proxy audio/image manifest from `RAVDESS` and extract one frame per video clip:

```powershell
python -m src.mental_health_screening.dataset_prep ravdess C:\path\to\RAVDESS data\manifests\ravdess_proxy.csv --extract-frames data\ravdess_frames
```

Generate a clinically labeled manifest from `DAIC-WOZ`:

```powershell
python -m src.mental_health_screening.dataset_prep daic-woz C:\path\to\DAIC-WOZ data\manifests\daic_clinical.csv
```

### 2. Train modality models from the generated manifests

Train text from `MELD` proxy labels:

```powershell
python -m src.mental_health_screening.training data\manifests\meld_proxy.csv --modality text
```

Train audio and image from `RAVDESS` proxy labels:

```powershell
python -m src.mental_health_screening.training data\manifests\ravdess_proxy.csv --modality audio
python -m src.mental_health_screening.training data\manifests\ravdess_proxy.csv --modality image
```

Retrain text and audio on `DAIC-WOZ` clinical labels:

```powershell
python -m src.mental_health_screening.training data\manifests\daic_clinical.csv --modality text
python -m src.mental_health_screening.training data\manifests\daic_clinical.csv --modality audio
```

### 3. Train from your own manifest too

If you are collecting your own field data, use the template at `data/training_manifest_template.csv` and provide:

- `text`: free-text response or transcript
- `audio_path`: relative or absolute path to the audio file
- `image_path`: relative or absolute path to the face image
- any subset of numeric label columns in the `[0.0, 1.0]` range

Then train:

```powershell
python -m src.mental_health_screening.training data\training_manifest_template.csv --modality all
```

Saved model bundles are written under `models/mental_health_screening/`.

Important implementation detail:

- the trainer now works per domain, so datasets that only supervise some outcomes can still be used honestly
- `DAIC-WOZ` is treated as clinical supervision mainly for `depression`, with conservative derived support for `sleep_disorder` and `burnout` when PHQ item columns are present
- proxy datasets are useful for representation learning, but they are not a substitute for clinically validated labels
