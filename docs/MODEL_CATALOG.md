# Model Catalog

This file lists every model family and saved bundle used in the project, along with its purpose in the screening workflow.

## Text

- `text_transformer`: primary transformer-based text scorer for narrative screening; used when the local transformer bundle is available.
- `text`: classical text scorer and fallback bundle; used when the transformer bundle is unavailable or as a stability backup.

## Audio

- `audio`: primary acoustic screening bundle; the main audio scorer for mood-heavy and speech-derived signals.
- `audio_spectrogram`: secondary audio branch trained on spectrograms; used as a stabilizer when available.
- `audio_sequence`: secondary audio branch trained on chunk sequences; used as a fallback stabilizer until it improves further.

## Image

- `image_dl`: primary image scorer; the current CNN-based image bundle with stronger augmentation and better diversity.
- `image`: classical image bundle; used as a fallback and stabilizer for face-derived features.

## Comorbidity

- `comorbidity`: classifier-chain ensemble for joint label prediction; used to estimate co-occurring domain patterns and now blends upstream text, audio, and image consensus.

## Supporting Runtime Components

These are not final decision models, but they support the screening stack:

- `questionnaire` scoring: structured symptom scoring from the assessment workspace.
- `passive biomarkers`: typing and phone-camera-derived adjunct signals for low-hardware screening support.
- `heuristic NLP features`: sentiment, emotion, distress phrases, and safety-language cues that keep the app usable when transformers are unavailable.

## Practical Priority Order

The runtime currently prefers:

1. `text_transformer` over `text`
2. `audio` over `audio_spectrogram` and `audio_sequence`
3. `image_dl` over `image`
4. `comorbidity` after upstream modality consensus is available

## Where These Models Are Used

- Preview scoring in the dashboard
- Saved assessment scoring
- Analytics Hub model statistics
- PDF report summaries
- Quality-check and trajectory views
- Training and retraining workflows

## Related Files

- [`docs/MODEL_COMPARISON_MATRIX.md`](MODEL_COMPARISON_MATRIX.md)
- [`docs/MULTIMODAL_FUSION.md`](MULTIMODAL_FUSION.md)
- [`docs/DEEP_LEARNING_MODEL_GUIDE.md`](DEEP_LEARNING_MODEL_GUIDE.md)
- [`README.md`](../README.md)
