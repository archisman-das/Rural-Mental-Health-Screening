# Model Comparison Matrix

This document gives a single-place reference for the current model stack: what each model does, how it is used, and how it compares to the other bundles in the runtime.

The metrics below are read from the saved bundle metadata in `web/model-stats.json` and the current model bundles.

## 1. Bundle Inventory

| Bundle | Modality | Working purpose | Runtime role | Primary input | Current status |
| --- | --- | --- | --- | --- | --- |
| `text_transformer` | Text | Transformer-based multilabel text scorer for narrative screening | Primary text scorer | Free text / transcript | Active |
| `text` | Text | Classical text bundle for fallback screening | Fallback text scorer | Text features | Active |
| `audio` | Audio | Main acoustic screening bundle for mood-heavy signals | Primary audio scorer | Acoustic summary features | Active |
| `audio_spectrogram` | Audio | CNN on spectrogram features | Secondary audio stabilizer | Spectrogram tensor | Active |
| `audio_sequence` | Audio | BiLSTM on chunk sequences | Fallback audio stabilizer | Sequence features | Active |
| `image_dl` | Image | CNN-based image scorer with stronger augmentation and diversity | Primary image scorer | Face/image tensor | Active |
| `image` | Image | Classical face-feature bundle | Fallback image scorer | Face-derived features | Active |
| `comorbidity` | Multimodal | Classifier-chain ensemble for joint label interaction modeling | Downstream comorbidity head | Text, audio, image consensus features | Active |

## 2. Current Comparison Matrix

| Bundle | Sample count | Macro F1 | Label accuracy | Exact match | Strengths | Weak spots |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `text` | 420,000 | 0.5956 | - | - | Large training footprint, stable fallback text scorer | Classical features only, less expressive than transformer text |
| `text_transformer` | 8,000 | 0.5762 | 0.7621 | 0.3731 | Better language modeling and better label-specific behavior on current text stack | Smaller training set than classical text |
| `audio` | 10,080 | 0.6019 | - | - | Best overall audio bundle, strongest practical audio scorer | Mood-heavy domains still need careful calibration |
| `audio_spectrogram` | 1,082 | 0.5328 | 0.6715 | 0.2074 | Helpful secondary acoustic view | Not yet better than main audio bundle |
| `audio_sequence` | 1,440 | 0.3893 | 0.4940 | 0.0069 | Captures temporal chunk patterns | Weakest audio branch, fallback only |
| `image` | 3,360 | 0.6019 | - | - | Stable classical image fallback | Less expressive than the DL image bundle |
| `image_dl` | 395 | 0.6168 | 0.7215 | 0.2152 | Best current image scorer | Needs more data diversity to generalize further |
| `comorbidity` | 24 | 0.4081 | 0.6786 | 0.3750 | Joint label interaction model, now blended with upstream modality consensus | Weakest bundle, highly sensitive to upstream quality |

## 3. Runtime Priority Order

The runtime currently prefers:

1. `text_transformer` over `text`
2. `audio` over `audio_spectrogram` and `audio_sequence`
3. `image_dl` over `image`
4. `comorbidity` after upstream text/audio/image consensus is available

## 4. Practical Interpretation

- `text_transformer` is the best text choice when installed, but the classical `text` bundle remains a useful fallback and can still be stronger in some aggregate settings.
- `audio` is the main audio scorer, while the spectrogram and sequence branches are secondary stabilizers.
- `image_dl` is currently the strongest image bundle and should be treated as the default image scorer.
- `comorbidity` is intentionally last in the stack and should be retrained after text, audio, and image stabilize.

## 5. How To Use This Matrix

Use this file when you need to answer questions like:

- Which model is primary for a modality?
- Which model is only a fallback?
- Which bundle has the weakest current validation signal?
- Which model should be retrained first?

## 6. Related Documentation

- [`README.md`](../README.md)
- [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)
- [`docs/MULTIMODAL_FUSION.md`](MULTIMODAL_FUSION.md)
- [`docs/PROJECT_DOCUMENTATION.md`](PROJECT_DOCUMENTATION.md)
- [`docs/DEEP_LEARNING_MODEL_GUIDE.md`](DEEP_LEARNING_MODEL_GUIDE.md)
