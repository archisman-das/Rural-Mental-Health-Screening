# Multimodal Fusion Guide

This document summarizes the current bundle priorities and fusion logic used by the screening runtime.

## 1. Bundle Priorities

The current runtime preference order is:

- Text: `text_transformer` primary, `text` fallback
- Audio: `audio` primary, `audio_spectrogram` and `audio_sequence` secondary
- Image: `image_dl` primary, `image` fallback
- Comorbidity: classifier-chain ensemble blended with upstream text, audio, and image consensus

These priorities are intentional. The project keeps the strongest trained bundle in front for each modality and uses the other bundles as stabilizers or fallback signals.

## 2. Why The Priorities Matter

The system is designed to be robust in field use:

- strong modality bundles carry most of the final signal,
- auxiliary branches help when the primary bundle is uncertain,
- weaker bundle families do not overrule the stronger ones,
- the final score remains stable even when one modality is missing.

## 3. Audio Fusion

Audio uses:

- the main `audio` bundle as the primary scorer,
- `audio_spectrogram` as a secondary stabilizer,
- `audio_sequence` as a fallback stabilizer.

The runtime gives mood-heavy domains like depression, loneliness, anxiety, sleep disorder, and burnout slightly more room to move than the stronger substance-abuse domain.

## 4. Image Fusion

Image uses:

- `image_dl` as the primary scorer,
- the classical `image` bundle as a stabilizer.

The DL model gets a slightly higher influence when both are available.

## 5. Text Fusion

Text uses:

- `text_transformer` when installed and available,
- the classical `text` bundle as fallback,
- small label-specific retuning for weaker text domains such as depression, loneliness, anxiety, substance abuse, sleep disorder, and stress.

The stronger labels are left mostly unchanged.

## 6. Comorbidity Fusion

The comorbidity head combines:

- classifier-chain ensemble probabilities,
- upstream modality consensus from text, audio, and image,
- calibration and pairwise lift metadata.

This helps the weakest bundle benefit more from stabilized upstream predictions instead of relying only on deeper chain tuning.

## 7. Related Files

- [`README.md`](../README.md)
- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)
- [`docs/MODEL_COMPARISON_MATRIX.md`](MODEL_COMPARISON_MATRIX.md)
- [`docs/PROJECT_DOCUMENTATION.md`](PROJECT_DOCUMENTATION.md)
- [`docs/DEEP_LEARNING_MODEL_GUIDE.md`](DEEP_LEARNING_MODEL_GUIDE.md)
