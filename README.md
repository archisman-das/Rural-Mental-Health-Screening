# Rural Mental Health Screening AI

An AI-based rural mental health screening dashboard for questionnaire intake, multimodal signals, adaptive screening, multilingual analysis views, saved result retrieval, and PDF reporting.

**Render-ready Flask web service**: `dashboard_server.py` + `gunicorn dashboard_server:app` + `/health`

Deployment quick check:

- Render service type: `Web Service`
- Backend entrypoint: `dashboard_server.py`
- Start command: `gunicorn dashboard_server:app`
- Health check: `/healthz`
- Host bind on Render: `0.0.0.0`

## What This Project Includes

- Multilingual dashboard UI with English, Hindi, and Bengali switching
- Assessment Workspace for profile intake, questionnaire capture, text narrative, audio, and image inputs
- Adaptive Test workflow for one-question-at-a-time screening
- Analytics Hub for live preview, component-wise analysis, model insights, trajectory tracking, and trend summaries
- Records and Reports for record lookup, detailed assessment review, and PDF export
- Flask backend with SQLite persistence and local offline fallback support

## Prediction Scope

The current model targets:

- Depression
- Anxiety
- Stress
- Sleep disorder
- Burnout
- Loneliness
- Substance abuse

The current scoring stack is intentionally hierarchical:

- text uses the `text_transformer` bundle when available, with the classical `text` bundle as fallback
- audio uses the main `audio` bundle as the primary scorer, with `audio_sequence` and `audio_spectrogram` as secondary stabilizers
- image uses `image_dl` as the primary scorer, with the classical `image` bundle as fallback
- comorbidity combines the upstream text, audio, and image consensus with the classifier-chain ensemble

The `comorbidity` bundle performs joint multi-label prediction so the model can estimate co-occurring patterns such as depression + anxiety rather than treating each label independently.

## Included

- `dashboard_server.py`: Flask backend for dashboard serving, assessment saves, record fetches, and PDF reports.
- `app.py`: earlier Streamlit prototype retained here.
- `src/mental_health_screening/assessment.py`: questionnaire definition and scoring logic.
- `src/mental_health_screening/feature_extract.py`: feature extraction helpers for text, audio, and image inputs.
- `src/mental_health_screening/predict.py`: screening heuristics, confidence estimation, and score aggregation.
- `src/mental_health_screening/storage.py`: SQLite-backed assessment storage with JSON cache sync.
- `src/mental_health_screening/report.py`: PDF report generation for saved assessments.
- `src/mental_health_screening/training.py`: training CLI and model-bundle builder for text, audio, and image.
- `src/mental_health_screening/training.py`: training CLI and model-bundle builder for text, audio, image, and comorbidity.
- `src/mental_health_screening/utils.py`: shared utility helpers.
- `docs/PROJECT_DOCUMENTATION.md`: detailed project documentation, architecture, API, and workflow guide.
- `docs/ARCHITECTURE.md`: standalone architecture guide that explains the working system in detail.
- `docs/MULTIMODAL_FUSION.md`: bundle-priority and fusion guide for the current text/audio/image/comorbidity stack.
- `docs/MODEL_CATALOG.md`: purpose-only catalog of every model family and saved bundle used in the project.
- `docs/MODEL_COMPARISON_MATRIX.md`: model-by-model working purpose and comparison matrix with current bundle metrics.
- `docs/PROJECT_PROPOSAL.md`: formal project proposal with motivation, scope, methodology, and evaluation plan.
- `docs/DEEP_LEARNING_MODEL_GUIDE.md`: detailed explanation of the text, audio, and vision model families used in the project.
- `models/mental_health_screening/onnx/`: exported ONNX artifacts for the sklearn bundle estimators, kept alongside the original `.pkl` bundles.
- `tools/export_model_bundles_to_onnx.py`: exporter that regenerates the ONNX artifacts from the saved pickle bundles.

## NLP Layer

The text pipeline supports:

- Language-native transformer encoders when available locally:
  - English: DistilBERT / BERT
  - Hindi: MuRIL or IndicBERT
  - Bengali: IndicBERT or MuRIL
- Validated PHQ-9 instrument translations for Hindi and Bengali
- Culturally adapted distress idioms and safety phrases for English, Hindi, and Bengali
- Emotion detection
- Sentiment analysis
- Self-harm keyword detection

If transformer packages or model weights are unavailable, the app falls back to lighter heuristic NLP features.

## Dashboard Stack

- Frontend: HTML, CSS, and JavaScript in `web/`
- Backend API: Flask
- Database: SQLite
- Assessment flow: dashboard intake with questionnaire, live Python NLP preview, and adaptive screening
- Data exchange: backend persistence and JSON import/export
- Reporting: backend PDF export

## Dashboard Usage

Run the dashboard:

```powershell
python dashboard_server.py
```

Open `http://127.0.0.1:8000/`.

Use it to:

- Create and save assessments directly from the `Assessment Workspace`
- Switch the interface between English, Hindi, and Bengali
- Review live prediction previews before saving
- Run the `Adaptive Test` for an IRT-style question flow that asks the next most informative item first
- Reuse workspace uploads in the adaptive flow instead of asking for a second upload set
- Review detailed single-assessment analysis in the `Analytics Hub`
- Track longitudinal trajectory, domain drift, trend summaries, and report-ready insights
- Fetch records and export PDF reports from `Records and Reports`
- Persist records through the API into the SQLite database
- Use the local offline fallback when the adaptive endpoint is unavailable

Optional zero-hardware passive inputs:

- `passive_video_file` for rPPG-style heart-rate estimation from a phone camera clip
- `typing_events` for typing-rhythm signals that act as an anxiety and stress adjunct

Passive payload:

```json
{
  "passive_video_file": "sample_phone_clip.mp4",
  "typing_events": {"intervals_ms": [180, 240, 210, 260]}
}
```

### API Examples

Use these payloads with the dashboard API.

```json
{
  "profile": {"language": "English"},
  "questionnaire": {},
  "text_input": "",
  "passive_video_file": "sample_phone_clip.mp4",
  "typing_events": {"intervals_ms": [180, 240, 210, 260]}
}
```

`/api/preview`:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/preview -H "Content-Type: application/json" -d "{\"profile\":{\"language\":\"English\"},\"questionnaire\":{},\"text_input\":\"\",\"passive_video_file\":\"sample_phone_clip.mp4\",\"typing_events\":{\"intervals_ms\":[180,240,210,260]}}"
```

`/api/assessments`:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/assessments -H "Content-Type: application/json" -d "{\"profile\":{\"full_name\":\"Demo User\",\"village\":\"Demo Village\",\"assessor\":\"CHW Demo\",\"consent_received\":true,\"language\":\"English\"},\"questionnaire\":{\"depression_score\":2,\"anxiety_score\":1,\"stress_score\":1,\"sleep_disorder_score\":1,\"burnout_score\":1},\"text_input\":\"\",\"passive_video_file\":\"sample_phone_clip.mp4\",\"typing_events\":{\"intervals_ms\":[180,240,210,260]}}"
```

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

3. Run the backend.

```powershell
python dashboard_server.py
```

4. Open `http://127.0.0.1:8000/` in your browser.

## Render Deployment

Deploy this project on Render as a **Web Service**, not a Static Site.

Use these settings:

- **Environment**: `Python`
- **Build command**: `pip install -r requirements.txt`
- **Start command**: `gunicorn dashboard_server:app`
- **Health check path**: `/healthz` or `/health`
- **Version check**: `/version`

Important:

- The Flask backend lives in `dashboard_server.py`.
- Render should launch the app with Gunicorn; local development can still use `python dashboard_server.py`.
- Do not point Render at `app.py`; that file is the older Streamlit prototype.
- The frontend assets are served by the Flask app from `web/`, so the backend must stay active for the dashboard and API routes to work.
- `/healthz` is the preferred Render probe and `/health` remains an alias for compatibility.

## App Usage

- Open the dashboard and complete the candidate profile, narrative, and symptom questionnaire in `Assessment Workspace`.
- The live workspace calls the Python backend so preview sentiment, emotion, self-harm detection, and transformer-backed text scoring match the saved analysis path.
- Audio and image uploads go to the backend during preview and save; if dependencies are installed and the media is usable, those modalities contribute real inference instead of metadata-only placeholders.
- The `Adaptive Test` workflow uses the same workspace uploads and can continue with a local fallback selector if the adaptive API is temporarily offline.
- Save the assessment to generate a persistent `assessment_id` in the API and SQLite database.
- Open `Analytics Hub` after save to review component-wise analysis, model statistics, modality quality, trajectory, trend summary, and recommendation details.
- Use `Records and Reports` to fetch a saved record by `assessment_id`, inspect the detailed result, and download a PDF report.

## Local Run

```powershell
python dashboard_server.py
```

Open `http://127.0.0.1:8000/` in your browser.

## Notes

This repo includes heuristic fallbacks and trained bundles from real manifests. At runtime, `predict.py` uses trained domain models when they exist and falls back to heuristics for unlabeled or untrained domains.
You can also run `python tools/evaluate_saved_assessments.py --input data/screening_results.json` to get a proxy precision/recall and calibration report on saved assessments.
For a one-command workflow, run `python tools/run_quality_check.py --input data/screening_results.json --output data/assessment_quality_report.json`.
On Windows, you can also double-click `tools\run_quality_check.bat` or run `tools\run_quality_check.ps1` directly.
Inside the dashboard, the Analytics Hub now includes a `Run Quality Check` button that pulls the same saved-assessment report into the page.

## Training

The training path has two honest stages:

- proxy pretraining from open emotion datasets such as `MELD` and `RAVDESS`
- clinical retraining from `DAIC-WOZ` once you have approved access

### Quick Start

If the datasets are already on disk, the orchestration script validates roots, generates manifests, and runs the training commands in one flow.

It also regenerates the bootstrapped comorbidity manifest from the MELD and RAVDESS proxy outputs before training, then retrains the joint comorbidity head from that larger file. By default, the pipeline writes a balanced `60,000` rows to `tmp_datasets/comorbidity_60k.csv` so it avoids the locked file in `data/manifests/` and gives the joint head more training volume.

See [docs/config_examples.md](/D:/Project/Rural%20Mental%20Heath%20Screening%20AI/docs/config_examples.md) for a short explanation of the example JSON config files and the writable manifest path.

1. Copy the example config and update the dataset paths:

```powershell
Copy-Item examples\dataset_roots.example.json examples\dataset_roots.local.json
```

For a pure federated demo, start from:

```powershell
Copy-Item examples\dataset_roots_and_federated.example.json examples\dataset_roots_and_federated.local.json
```

Then run the full federated flow as a single command:

```powershell
python tools\run_real_training_pipeline.py --config examples\dataset_roots_and_federated.local.json
```

2. Dry-run the full pipeline first:

```powershell
python tools\run_real_training_pipeline.py --config examples\dataset_roots.local.json --dry-run
```

3. Run the full manifest + training pipeline:

```powershell
python tools\run_real_training_pipeline.py --config examples\dataset_roots.local.json
```

Outputs:

- generated manifests to `data/manifests/`
- extracted `RAVDESS` video frames to `data/ravdess_frames/`
- trained bundles to `models/mental_health_screening/`
- a pipeline run summary to `models/mental_health_screening/training_pipeline_summary.json`

You can also pass the dataset roots directly instead of using a config file:

```powershell
python tools\run_real_training_pipeline.py `
  --daic-woz-root C:\datasets\DAIC-WOZ `
  --meld-root C:\datasets\MELD `
  --ravdess-root C:\datasets\RAVDESS
```

Useful flags:

- `--dry-run`: print the exact commands without executing them
- `--skip-manifest-build`: reuse existing manifests in `data/manifests/`
- `--skip-training`: build manifests only
- `--skip-daic-woz`: run only the public proxy datasets until clinical access is approved
- `--min-samples-per-domain 10`: require more labeled rows before domain training starts

To split a combined field manifest by centre and run federated training from the top-level pipeline, pass it directly:

```powershell
python tools\run_real_training_pipeline.py `
  --federated-manifest data\manifests\combined_field_manifest.csv `
  --federated-modality all `
  --skip-manifest-build
```

### Federated Helper

Use the federated helper for one-manifest-per-centre runs.

| Case | Command |
| --- | --- |
| Default centre column | `python tools\run_federated_training.py data\manifests\combined_field_manifest.csv --modality all` |
| Custom centre column | `python tools\run_federated_training.py data\manifests\combined_field_manifest.csv --centre-column clinic_name --modality text` |

The helper writes the split manifests to `data/manifests/federated_centres/` by default and then calls the trainer with `--federated-manifests`.

### Download Public Data

Use the helper below to download the public training data into `data/public_datasets/`.

```powershell
python tools\download_public_training_data.py --ravdess-video-actors 1,2,3,4
```

It downloads:

- `MELD` annotation CSVs for text training
- `RAVDESS` speech audio for all 24 actors
- `RAVDESS` speech-video archives for the chosen actor ids, so image training has local video data to extract frames from
- a local `DAIC-WOZ` request note, because that dataset cannot be auto-downloaded from the official site

After download, these dataset roots work with the pipeline:

```powershell
python tools\run_real_training_pipeline.py `
  --daic-woz-root data\public_datasets\DAIC-WOZ `
  --meld-root data\public_datasets\MELD `
  --ravdess-root data\public_datasets\RAVDESS `
  --skip-daic-woz
```

Notes:

- `DAIC-WOZ` requires official approval before real clinical training can happen
- the `MELD` prep path uses the public annotation CSVs for text proxy training
- for stronger image training from `RAVDESS`, download more speech-video actor archives over time, for example `--ravdess-video-actors 1,2,3,4,5,6,7,8`

### Build Manifests

Build a proxy text manifest from `MELD`:

```powershell
python -m src.mental_health_screening.dataset_prep meld C:\path\to\MELD data\manifests\meld_proxy.csv
```

Build a proxy audio/image manifest from `RAVDESS` and extract one frame per clip:

```powershell
python -m src.mental_health_screening.dataset_prep ravdess C:\path\to\RAVDESS data\manifests\ravdess_proxy.csv --extract-frames data\ravdess_frames
```

Build a clinically labeled manifest from `DAIC-WOZ`:

```powershell
python -m src.mental_health_screening.dataset_prep daic-woz C:\path\to\DAIC-WOZ data\manifests\daic_clinical.csv
```

Build the balanced comorbidity training manifest from the proxy datasets:

```powershell
python -m src.mental_health_screening.dataset_prep comorbidity-expand `
  data\manifests\meld_proxy.csv `
  data\manifests\ravdess_proxy.csv `
  --output-path tmp_datasets\comorbidity_60k.csv `
  --target-rows 60000 `
  --bucket-targets 0:12000,1:12000,2:12000,3:12000,4:12000
```

If you need a smaller copy under `data/manifests/`, use a different output path only after the file lock is cleared.

### Train Modality Models

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

### Train Your Own Manifest

If you are collecting your own field data, use `data/training_manifest_template.csv` and provide:

- `text`: free-text response or transcript
- `audio_path`: relative or absolute path to the audio file
- `image_path`: relative or absolute path to the face image
- any subset of numeric label columns in the `[0.0, 1.0]` range

Then train:

```powershell
python -m src.mental_health_screening.training data\training_manifest_template.csv --modality all
```

Saved model bundles are written under `models/mental_health_screening/`.

Implementation notes:

- the trainer works per domain, so datasets that only supervise some outcomes can still be used honestly
- `DAIC-WOZ` is treated as clinical supervision mainly for `depression`, with conservative derived support for `sleep_disorder` and `burnout` when PHQ item columns are present
- proxy datasets are useful for representation learning, but they are not a substitute for clinically validated labels
- the comorbidity head uses a classifier-chain ensemble so it can learn label co-occurrence and emit joint probabilities for combinations like depression + anxiety
- the final comorbidity score now also blends upstream text, audio, and image consensus so the weakest head benefits from stronger modality stabilization

### Current Bundle Priorities

The runtime bundle priorities are:

- `text_transformer` primary for text, `text` as fallback
- `image_dl` primary for image, `image` as fallback
- `audio` primary for audio, with `audio_sequence` and `audio_spectrogram` as secondary support
- `comorbidity` retrained on the improved upstream modality outputs and blended with them at inference

### Rural Voice Models

This repo includes dialect-aware ASR fine-tuning for rural Bengali and Hindi speech. It fine-tunes either `wav2vec2` or `Whisper` from a local Hugging Face checkpoint and trains one model per `dialect` value by default.

Use a manifest with these columns:

- `audio_path`: path to the speech clip
- `transcript` or `text`: the transcript for supervised fine-tuning
- `language`: `bengali` or `hindi`
- `dialect`: a rural dialect label, such as `west_bengal_rural` or `up_rural`

Config-driven runs:

| Template | Copy local | Run command |
| --- | --- | --- |
| wav2vec2 | `Copy-Item examples\voice_training.example.json examples\voice_training.local.json` | `python tools\run_real_training_pipeline.py --config examples\voice_training.local.json` |
| Whisper | `Copy-Item examples\voice_training.whisper.example.json examples\voice_training.whisper.local.json` | `python tools\run_real_training_pipeline.py --config examples\voice_training.whisper.local.json` |

Use a checkpoint you already have cached locally, or point `voice_base_model_name` at a local model path.

Useful flags:

- `--base-model-name`: use a specific local Whisper or wav2vec2 checkpoint
- `--output-dir`: choose where the dialect-specific models are saved
- `--min-samples-per-dialect`: skip tiny dialect slices
- `--no-per-dialect`: train a single shared voice model instead of separate dialect slices

Direct helper:

```powershell
python tools\run_voice_finetuning.py examples\voice_manifest.example.csv --model-family wav2vec2
python tools\run_voice_finetuning.py examples\voice_manifest.example.csv --model-family whisper
```
