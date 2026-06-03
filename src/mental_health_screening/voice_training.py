from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SUPPORTED_VOICE_FAMILIES = ("wav2vec2", "whisper")
DEFAULT_VOICE_MODEL_CANDIDATES = {
    "wav2vec2": {
        "bengali": (
            "ai4bharat/indicwav2vec-bengali",
            "facebook/wav2vec2-large-xlsr-53",
        ),
        "hindi": (
            "ai4bharat/indicwav2vec-hindi",
            "facebook/wav2vec2-large-xlsr-53",
        ),
        "default": (
            "facebook/wav2vec2-base-960h",
            "facebook/wav2vec2-large-xlsr-53",
        ),
    },
    "whisper": {
        "bengali": (
            "openai/whisper-small",
            "openai/whisper-base",
        ),
        "hindi": (
            "openai/whisper-small",
            "openai/whisper-base",
        ),
        "default": (
            "openai/whisper-small",
            "openai/whisper-base",
        ),
    },
}


def _normalize_text(value: object) -> str:
    return str(value or "").strip()


def _normalize_language(value: object) -> str:
    text = _normalize_text(value).lower()
    if text in {"bn", "bengali", "bangla", "বাংলা"}:
        return "bengali"
    if text in {"hi", "hindi", "हिंदी", "हिन्दी"}:
        return "hindi"
    return "unknown"


def _normalize_dialect(value: object) -> str:
    text = _normalize_text(value).lower()
    if not text or text in {"nan", "none", "null"}:
        return "shared"
    cleaned = []
    for character in text:
        cleaned.append(character if character.isalnum() else "_")
    result = "".join(cleaned).strip("_")
    return result or "shared"


def _resolve_audio_path(base_dir: Path, raw_value: object) -> Path | None:
    text = _normalize_text(raw_value)
    if not text:
        return None
    path = Path(text)
    if not path.is_absolute():
        path = (base_dir / path).resolve()
    return path if path.exists() else None


def _load_manifest(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Voice training manifest not found: {path}")
    if path.suffix.lower() == ".jsonl":
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        return pd.DataFrame(rows)
    if path.suffix.lower() == ".json":
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        return pd.DataFrame(payload)
    return pd.read_csv(path)


def _require_torch():
    try:
        import torch  # type: ignore
    except ImportError as error:  # pragma: no cover - dependency guard
        raise ImportError("PyTorch is required for voice fine-tuning.") from error
    return torch


def _require_librosa():
    try:
        import librosa  # type: ignore
    except ImportError as error:  # pragma: no cover - dependency guard
        raise ImportError("librosa is required for voice fine-tuning.") from error
    return librosa


def _require_transformers():
    try:
        from transformers import AutoProcessor, WhisperForConditionalGeneration, Wav2Vec2ForCTC  # type: ignore
    except ImportError as error:  # pragma: no cover - dependency guard
        raise ImportError("transformers is required for voice fine-tuning.") from error
    return AutoProcessor, WhisperForConditionalGeneration, Wav2Vec2ForCTC


def _select_base_model(model_family: str, language: str, model_name: str | None) -> str:
    if model_name:
        return model_name
    family_candidates = DEFAULT_VOICE_MODEL_CANDIDATES[model_family]
    candidates = family_candidates.get(language) or family_candidates["default"]
    return candidates[0]


def _text_to_normalized_string(transcript: object) -> str:
    return " ".join(_normalize_text(transcript).split())


def _edit_distance(reference: list[str], hypothesis: list[str]) -> int:
    if not reference:
        return len(hypothesis)
    if not hypothesis:
        return len(reference)
    previous_row = list(range(len(hypothesis) + 1))
    for index, ref_token in enumerate(reference, start=1):
        current_row = [index]
        for jndex, hyp_token in enumerate(hypothesis, start=1):
            insert_cost = current_row[jndex - 1] + 1
            delete_cost = previous_row[jndex] + 1
            substitute_cost = previous_row[jndex - 1] + int(ref_token != hyp_token)
            current_row.append(min(insert_cost, delete_cost, substitute_cost))
        previous_row = current_row
    return previous_row[-1]


def _character_error_rate(reference: str, hypothesis: str) -> float:
    reference_chars = list(reference.replace(" ", ""))
    hypothesis_chars = list(hypothesis.replace(" ", ""))
    if not reference_chars:
        return float(len(hypothesis_chars) > 0)
    return float(_edit_distance(reference_chars, hypothesis_chars) / max(len(reference_chars), 1))


def _word_error_rate(reference: str, hypothesis: str) -> float:
    reference_words = reference.split()
    hypothesis_words = hypothesis.split()
    if not reference_words:
        return float(len(hypothesis_words) > 0)
    return float(_edit_distance(reference_words, hypothesis_words) / max(len(reference_words), 1))


@dataclass
class VoiceRecord:
    audio_path: Path
    transcript: str
    language: str
    dialect: str
    speaker_id: str


def _records_from_frame(frame: pd.DataFrame, base_dir: Path) -> list[VoiceRecord]:
    records: list[VoiceRecord] = []
    for record in frame.to_dict(orient="records"):
        audio_path = _resolve_audio_path(base_dir, record.get("audio_path"))
        transcript = _text_to_normalized_string(record.get("transcript") or record.get("text"))
        if audio_path is None or not transcript:
            continue
        records.append(
            VoiceRecord(
                audio_path=audio_path,
                transcript=transcript,
                language=_normalize_language(record.get("language")),
                dialect=_normalize_dialect(record.get("dialect")),
                speaker_id=_normalize_text(record.get("speaker_id")) or _normalize_text(record.get("sample_id")) or audio_path.stem,
            )
        )
    return records


class VoiceASRDataset:
    def __init__(self, records: list[VoiceRecord], processor, sample_rate: int = 16000):
        self.records = records
        self.processor = processor
        self.sample_rate = sample_rate

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> dict:
        record = self.records[index]
        librosa = _require_librosa()
        speech_array, _ = librosa.load(str(record.audio_path), sr=self.sample_rate, mono=True)
        inputs = self.processor(
            speech_array,
            sampling_rate=self.sample_rate,
            return_attention_mask=True,
        )
        with self.processor.as_target_processor():
            labels = self.processor(record.transcript).input_ids
        input_key = "input_features" if "input_features" in inputs else "input_values"
        return {
            "input_key": input_key,
            "input_values": inputs["input_values"][0] if "input_values" in inputs else None,
            "input_features": inputs["input_features"][0] if "input_features" in inputs else None,
            "attention_mask": inputs.get("attention_mask", [None])[0],
            "labels": labels,
            "transcript": record.transcript,
            "audio_path": str(record.audio_path),
            "language": record.language,
            "dialect": record.dialect,
            "speaker_id": record.speaker_id,
        }


class VoiceDataCollator:
    def __init__(self, processor, model_family: str):
        self.processor = processor
        self.model_family = model_family

    def __call__(self, features: list[dict]) -> dict:
        input_key = features[0]["input_key"]
        if input_key == "input_features":
            audio_features = [{"input_features": feature["input_features"]} for feature in features]
            batch = self.processor.feature_extractor.pad(audio_features, return_tensors="pt")
        else:
            audio_features = [{"input_values": feature["input_values"]} for feature in features]
            batch = self.processor.pad(audio_features, return_tensors="pt")
        label_features = [{"input_ids": feature["labels"]} for feature in features]
        labels_batch = self.processor.tokenizer.pad(label_features, return_tensors="pt")
        labels = labels_batch["input_ids"].masked_fill(labels_batch["attention_mask"].ne(1), -100)
        batch["labels"] = labels
        batch["transcripts"] = [feature["transcript"] for feature in features]
        batch["audio_paths"] = [feature["audio_path"] for feature in features]
        batch["dialects"] = [feature["dialect"] for feature in features]
        batch["languages"] = [feature["language"] for feature in features]
        batch["speaker_ids"] = [feature["speaker_id"] for feature in features]
        batch["input_key"] = input_key
        return batch


def _build_train_eval_split(records: list[VoiceRecord], random_state: int) -> tuple[list[VoiceRecord], list[VoiceRecord]]:
    if len(records) < 4:
        return records, []
    shuffled = records[:]
    rng = random.Random(random_state)
    rng.shuffle(shuffled)
    eval_size = max(1, int(math.ceil(len(shuffled) * 0.2)))
    return shuffled[eval_size:], shuffled[:eval_size]


def _select_model_class(model_family: str):
    _, WhisperForConditionalGeneration, Wav2Vec2ForCTC = _require_transformers()
    if model_family == "wav2vec2":
        return Wav2Vec2ForCTC
    if model_family == "whisper":
        return WhisperForConditionalGeneration
    raise ValueError(f"Unsupported model family: {model_family}")


def _prefer_dialect_groups(records: list[VoiceRecord]) -> dict[str, list[VoiceRecord]]:
    grouped: dict[str, list[VoiceRecord]] = {}
    for record in records:
        grouped.setdefault(record.dialect, []).append(record)
    if len(grouped) <= 1:
        return {"shared": records}
    return grouped


def _load_processor(model_name: str):
    AutoProcessor, _, _ = _require_transformers()
    try:
        return AutoProcessor.from_pretrained(model_name, local_files_only=True)
    except Exception as error:
        raise FileNotFoundError(
            f"Unable to load tokenizer/processor for '{model_name}' from local files. "
            "Install or cache the model weights locally first."
        ) from error


def _load_model(model_family: str, model_name: str):
    model_class = _select_model_class(model_family)
    try:
        return model_class.from_pretrained(model_name, local_files_only=True)
    except Exception as error:
        raise FileNotFoundError(
            f"Unable to load base voice model '{model_name}' from local files."
        ) from error


def _freeze_feature_extractor(model, model_family: str) -> None:
    if model_family == "wav2vec2" and hasattr(model, "freeze_feature_encoder"):
        model.freeze_feature_encoder()
    if model_family == "whisper" and hasattr(model, "model") and hasattr(model.model, "encoder"):
        for parameter in model.model.encoder.parameters():
            parameter.requires_grad = False


def _greedy_decode(processor, model_family: str, batch: dict, model) -> list[str]:
    if model_family == "wav2vec2":
        predicted_ids = torch.argmax(batch, dim=-1)
        return processor.batch_decode(predicted_ids)
    if model_family == "whisper":
        generated_ids = model.generate(
            batch,
            max_new_tokens=128,
        )
        return processor.batch_decode(generated_ids, skip_special_tokens=True)
    raise ValueError(f"Unsupported model family: {model_family}")


def train_voice_dialect_model(
    manifest_path: str | Path,
    model_family: str = "wav2vec2",
    base_model_name: str | None = None,
    output_dir: str | Path | None = None,
    min_samples_per_dialect: int = 8,
    per_dialect: bool = True,
    random_state: int = 42,
    epochs: int = 3,
    batch_size: int = 4,
    learning_rate: float = 3e-5,
) -> dict:
    model_family = model_family.lower().strip()
    if model_family not in SUPPORTED_VOICE_FAMILIES:
        raise ValueError(f"Unsupported voice model family '{model_family}'. Expected one of {SUPPORTED_VOICE_FAMILIES}.")
    torch = _require_torch()
    from torch.utils.data import DataLoader

    manifest_path = Path(manifest_path)
    base_dir = manifest_path.parent
    frame = _load_manifest(manifest_path)
    records = _records_from_frame(frame, base_dir)
    if not records:
        raise ValueError("No usable voice training rows were found. Need audio_path + transcript/text columns.")

    output_root = Path(output_dir) if output_dir else Path(__file__).resolve().parents[2] / "models" / "mental_health_screening" / "voice"
    output_root.mkdir(parents=True, exist_ok=True)

    grouped_records = _prefer_dialect_groups(records) if per_dialect else {"shared": records}
    results: dict[str, dict] = {}
    trained_at = datetime.now(timezone.utc).isoformat()

    for dialect, dialect_records in grouped_records.items():
        if len(dialect_records) < min_samples_per_dialect:
            results[dialect] = {
                "status": "skipped",
                "reason": f"Need at least {min_samples_per_dialect} samples for dialect '{dialect}'.",
                "sample_count": len(dialect_records),
            }
            continue

        language = dialect_records[0].language
        model_name = _select_base_model(model_family, language, base_model_name)
        processor = _load_processor(model_name)
        model = _load_model(model_family, model_name)
        _freeze_feature_extractor(model, model_family)
        if model_family == "whisper":
            model.config.forced_decoder_ids = None
            model.config.suppress_tokens = []
            model.config.use_cache = False
        model.to("cuda" if torch.cuda.is_available() else "cpu")

        train_records, eval_records = _build_train_eval_split(dialect_records, random_state)
        train_dataset = VoiceASRDataset(train_records, processor)
        eval_dataset = VoiceASRDataset(eval_records, processor) if eval_records else None
        data_collator = VoiceDataCollator(processor, model_family=model_family)

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, collate_fn=data_collator)
        eval_loader = DataLoader(eval_dataset, batch_size=batch_size, shuffle=False, collate_fn=data_collator) if eval_dataset else None

        device = next(model.parameters()).device
        optimizer = torch.optim.AdamW((parameter for parameter in model.parameters() if parameter.requires_grad), lr=learning_rate)
        model.train()

        for _epoch in range(epochs):
            for batch in train_loader:
                optimizer.zero_grad()
                inputs = {
                    "input_features": batch["input_features"].to(device) if batch["input_key"] == "input_features" else None,
                    "input_values": batch["input_values"].to(device) if batch["input_key"] == "input_values" else None,
                    "attention_mask": batch["attention_mask"].to(device) if batch.get("attention_mask") is not None else None,
                    "labels": batch["labels"].to(device),
                }
                inputs = {key: value for key, value in inputs.items() if value is not None}
                outputs = model(**inputs)
                loss = outputs.loss
                loss.backward()
                optimizer.step()

        eval_metrics = {}
        if eval_loader is not None:
            model.eval()
            losses: list[float] = []
            reference_texts: list[str] = []
            hypothesis_texts: list[str] = []
            with torch.no_grad():
                for batch in eval_loader:
                    inputs = {
                        "input_features": batch["input_features"].to(device) if batch["input_key"] == "input_features" else None,
                        "input_values": batch["input_values"].to(device) if batch["input_key"] == "input_values" else None,
                        "attention_mask": batch["attention_mask"].to(device) if batch.get("attention_mask") is not None else None,
                        "labels": batch["labels"].to(device),
                    }
                    inputs = {key: value for key, value in inputs.items() if value is not None}
                    outputs = model(**inputs)
                    losses.append(float(outputs.loss.item()))
                    if model_family == "whisper":
                        decoded = _greedy_decode(processor, model_family, inputs["input_features"], model)
                    else:
                        decoded = _greedy_decode(processor, model_family, outputs.logits.detach().cpu(), model)
                    hypothesis_texts.extend([_normalize_text(text) for text in decoded])
                    reference_texts.extend(batch["transcripts"])
            eval_metrics = {
                "eval_loss": float(np.mean(losses)) if losses else None,
                "eval_cer": float(np.mean([
                    _character_error_rate(reference, hypothesis)
                    for reference, hypothesis in zip(reference_texts, hypothesis_texts)
                ])) if reference_texts else None,
                "eval_wer": float(np.mean([
                    _word_error_rate(reference, hypothesis)
                    for reference, hypothesis in zip(reference_texts, hypothesis_texts)
                ])) if reference_texts else None,
            }

        dialect_dir = output_root / model_family / _normalize_language(language) / dialect
        dialect_dir.mkdir(parents=True, exist_ok=True)
        model.save_pretrained(dialect_dir)
        processor.save_pretrained(dialect_dir)

        metadata = {
            "model_family": model_family,
            "base_model_name": model_name,
            "language": language,
            "dialect": dialect,
            "sample_count": len(dialect_records),
            "train_count": len(train_records),
            "eval_count": len(eval_records),
            "trained_at": trained_at,
            "output_dir": str(dialect_dir.resolve()),
            "voice_strategy": "dialect_specific_fine_tuning",
            "metrics": eval_metrics,
            "samples": [
                {
                    "audio_path": str(record.audio_path),
                    "speaker_id": record.speaker_id,
                }
                for record in dialect_records[:10]
            ],
        }
        (dialect_dir / "voice_training_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        results[dialect] = {
            "status": "trained",
            "metadata": metadata,
        }

    summary = {
        "manifest_path": str(manifest_path.resolve()),
        "base_dir": str(base_dir.resolve()),
        "model_family": model_family,
        "per_dialect": per_dialect,
        "trained_at": trained_at,
        "results": results,
    }
    (output_root / f"{manifest_path.stem}_{model_family}_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _parse_voice_manifest_list(raw_value: str | None) -> list[str]:
    if not raw_value:
        return []
    return [value.strip() for value in raw_value.split(",") if value.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fine-tune Whisper or wav2vec2 on Bengali/Hindi rural speech with dialect-specific splits."
    )
    parser.add_argument("manifest", help="CSV, JSON, or JSONL manifest with audio_path, transcript/text, language, and dialect columns.")
    parser.add_argument("--model-family", choices=SUPPORTED_VOICE_FAMILIES, default="wav2vec2", help="Choose Whisper or wav2vec2 fine-tuning.")
    parser.add_argument("--base-model-name", default=None, help="Optional local Hugging Face model name or path to fine-tune from.")
    parser.add_argument("--output-dir", default=None, help="Directory where per-dialect fine-tuned models will be written.")
    parser.add_argument("--min-samples-per-dialect", type=int, default=8, help="Minimum rows required to train a dialect slice.")
    parser.add_argument("--no-per-dialect", dest="per_dialect", action="store_false", help="Train one shared model instead of separate dialect slices.")
    parser.add_argument("--epochs", type=int, default=3, help="Number of fine-tuning epochs.")
    parser.add_argument("--batch-size", type=int, default=4, help="Training batch size.")
    parser.add_argument("--learning-rate", type=float, default=3e-5, help="Fine-tuning learning rate.")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed for train/eval splitting.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    train_voice_dialect_model(
        manifest_path=args.manifest,
        model_family=args.model_family,
        base_model_name=args.base_model_name,
        output_dir=args.output_dir,
        min_samples_per_dialect=args.min_samples_per_dialect,
        per_dialect=args.per_dialect,
        random_state=args.random_state,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
