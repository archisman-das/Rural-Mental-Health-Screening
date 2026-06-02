from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import cv2
import pandas as pd

from .constants import PREDICTION_DOMAINS


MANIFEST_COLUMNS = [
    "source_dataset",
    "source_split",
    "sample_id",
    "text",
    "audio_path",
    "image_path",
    *PREDICTION_DOMAINS,
]

MELD_EMOTION_SCORES = {
    "neutral": {"depression": 0.16, "anxiety": 0.12, "stress": 0.12, "sleep_disorder": 0.1, "burnout": 0.1, "loneliness": 0.1, "substance_abuse": 0.05},
    "joy": {"depression": 0.04, "anxiety": 0.05, "stress": 0.06, "sleep_disorder": 0.04, "burnout": 0.05, "loneliness": 0.03, "substance_abuse": 0.03},
    "sadness": {"depression": 0.82, "anxiety": 0.32, "stress": 0.4, "sleep_disorder": 0.34, "burnout": 0.38, "loneliness": 0.72, "substance_abuse": 0.1},
    "anger": {"depression": 0.28, "anxiety": 0.44, "stress": 0.82, "sleep_disorder": 0.26, "burnout": 0.66, "loneliness": 0.18, "substance_abuse": 0.22},
    "fear": {"depression": 0.34, "anxiety": 0.9, "stress": 0.78, "sleep_disorder": 0.3, "burnout": 0.28, "loneliness": 0.16, "substance_abuse": 0.08},
    "disgust": {"depression": 0.24, "anxiety": 0.3, "stress": 0.58, "sleep_disorder": 0.18, "burnout": 0.44, "loneliness": 0.12, "substance_abuse": 0.18},
    "surprise": {"depression": 0.14, "anxiety": 0.42, "stress": 0.36, "sleep_disorder": 0.14, "burnout": 0.12, "loneliness": 0.08, "substance_abuse": 0.06},
}

MELD_SENTIMENT_ADJUSTMENTS = {
    "positive": {"depression": -0.08, "anxiety": -0.05, "stress": -0.06, "sleep_disorder": -0.03, "burnout": -0.04, "loneliness": -0.05, "substance_abuse": -0.03},
    "neutral": {},
    "negative": {"depression": 0.06, "anxiety": 0.08, "stress": 0.08, "sleep_disorder": 0.04, "burnout": 0.05, "loneliness": 0.05, "substance_abuse": 0.03},
}

RAVDESS_EMOTION_CODE_MAP = {
    "01": "neutral",
    "02": "calm",
    "03": "happy",
    "04": "sad",
    "05": "angry",
    "06": "fearful",
    "07": "disgust",
    "08": "surprised",
}

RAVDESS_PROXY_SCORES = {
    "neutral": {"depression": 0.12, "anxiety": 0.1, "stress": 0.1, "sleep_disorder": 0.08, "burnout": 0.08, "loneliness": 0.08, "substance_abuse": 0.04},
    "calm": {"depression": 0.08, "anxiety": 0.06, "stress": 0.06, "sleep_disorder": 0.06, "burnout": 0.06, "loneliness": 0.06, "substance_abuse": 0.04},
    "happy": {"depression": 0.04, "anxiety": 0.04, "stress": 0.05, "sleep_disorder": 0.04, "burnout": 0.04, "loneliness": 0.03, "substance_abuse": 0.03},
    "sad": {"depression": 0.8, "anxiety": 0.28, "stress": 0.34, "sleep_disorder": 0.28, "burnout": 0.34, "loneliness": 0.7, "substance_abuse": 0.08},
    "angry": {"depression": 0.26, "anxiety": 0.4, "stress": 0.84, "sleep_disorder": 0.22, "burnout": 0.64, "loneliness": 0.12, "substance_abuse": 0.18},
    "fearful": {"depression": 0.32, "anxiety": 0.92, "stress": 0.8, "sleep_disorder": 0.24, "burnout": 0.22, "loneliness": 0.12, "substance_abuse": 0.08},
    "disgust": {"depression": 0.22, "anxiety": 0.28, "stress": 0.54, "sleep_disorder": 0.18, "burnout": 0.4, "loneliness": 0.1, "substance_abuse": 0.18},
    "surprised": {"depression": 0.12, "anxiety": 0.44, "stress": 0.38, "sleep_disorder": 0.14, "burnout": 0.12, "loneliness": 0.08, "substance_abuse": 0.05},
}


def _empty_row() -> dict:
    return {column: "" for column in MANIFEST_COLUMNS}


def _clip_score(value: float) -> float:
    return round(max(0.0, min(1.0, float(value))), 4)


def _discover_file(root: Path, name: str) -> Path | None:
    exact = root / name
    if exact.exists():
        return exact
    matches = list(root.rglob(name))
    return matches[0] if matches else None


def _write_manifest(rows: list[dict], output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANIFEST_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in MANIFEST_COLUMNS})
    return output_path


def _meld_proxy_scores(emotion: str, sentiment: str) -> dict:
    emotion_scores = dict(MELD_EMOTION_SCORES.get(str(emotion).strip().lower(), MELD_EMOTION_SCORES["neutral"]))
    for domain, adjustment in MELD_SENTIMENT_ADJUSTMENTS.get(str(sentiment).strip().lower(), {}).items():
        emotion_scores[domain] = _clip_score(emotion_scores[domain] + adjustment)
    return {domain: _clip_score(emotion_scores.get(domain, 0.0)) for domain in PREDICTION_DOMAINS}


def build_meld_manifest(dataset_root: str | Path, output_path: str | Path) -> Path:
    dataset_root = Path(dataset_root)
    rows: list[dict] = []
    split_files = {
        "train": _discover_file(dataset_root, "train_sent_emo.csv"),
        "dev": _discover_file(dataset_root, "dev_sent_emo.csv"),
        "test": _discover_file(dataset_root, "test_sent_emo.csv"),
    }

    missing = [split_name for split_name, path in split_files.items() if path is None]
    if missing:
        raise FileNotFoundError(f"MELD annotation files not found for splits: {missing}")

    for split_name, csv_path in split_files.items():
        frame = pd.read_csv(csv_path)
        for record in frame.to_dict(orient="records"):
            sample_id = f"meld-{split_name}-dia{record.get('Dialogue_ID')}-utt{record.get('Utterance_ID')}"
            row = _empty_row()
            row.update(
                {
                    "source_dataset": "MELD",
                    "source_split": split_name,
                    "sample_id": sample_id,
                    "text": str(record.get("Utterance", "") or "").strip(),
                }
            )
            row.update(_meld_proxy_scores(record.get("Emotion", "neutral"), record.get("Sentiment", "neutral")))
            rows.append(row)

    return _write_manifest(rows, output_path)


def _ravdess_proxy_scores(emotion_code: str, intensity_code: str) -> dict:
    emotion_name = RAVDESS_EMOTION_CODE_MAP.get(emotion_code, "neutral")
    base_scores = dict(RAVDESS_PROXY_SCORES[emotion_name])
    if intensity_code == "02":
        for domain in ("anxiety", "stress", "burnout", "substance_abuse"):
            base_scores[domain] = _clip_score(base_scores[domain] + 0.05)
    return {domain: _clip_score(base_scores.get(domain, 0.0)) for domain in PREDICTION_DOMAINS}


def _extract_video_frame(video_path: Path, frame_output_dir: Path) -> Path | None:
    frame_output_dir.mkdir(parents=True, exist_ok=True)
    output_path = frame_output_dir / f"{video_path.stem}.jpg"
    if output_path.exists():
        return output_path

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        return None

    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    target_index = max(frame_count // 2, 0)
    capture.set(cv2.CAP_PROP_POS_FRAMES, target_index)
    success, frame = capture.read()
    capture.release()
    if not success or frame is None:
        return None

    if cv2.imwrite(str(output_path), frame):
        return output_path
    return None


def build_ravdess_manifest(
    dataset_root: str | Path,
    output_path: str | Path,
    frame_output_dir: str | Path | None = None,
    speech_only: bool = True,
) -> Path:
    dataset_root = Path(dataset_root)
    frame_dir = Path(frame_output_dir) if frame_output_dir else None
    rows: list[dict] = []

    for path in dataset_root.rglob("*"):
        if path.suffix.lower() not in {".wav", ".mp4"}:
            continue

        parts = path.stem.split("-")
        if len(parts) != 7:
            continue

        modality_code, channel_code, emotion_code, intensity_code, statement_code, repetition_code, actor_code = parts
        if speech_only and channel_code != "01":
            continue

        row = _empty_row()
        row.update(
            {
                "source_dataset": "RAVDESS",
                "source_split": "full",
                "sample_id": f"ravdess-{path.stem}",
            }
        )
        row.update(_ravdess_proxy_scores(emotion_code, intensity_code))

        suffix = path.suffix.lower()
        if suffix == ".wav":
            row["audio_path"] = str(path.resolve())
        elif suffix == ".mp4" and frame_dir is not None:
            frame_path = _extract_video_frame(path, frame_dir)
            if frame_path is not None:
                row["image_path"] = str(frame_path.resolve())

        if row["audio_path"] or row["image_path"]:
            row["text"] = (
                f"RAVDESS {RAVDESS_EMOTION_CODE_MAP.get(emotion_code, 'neutral')} speech clip "
                f"statement {statement_code} repetition {repetition_code} actor {actor_code}"
            )
            rows.append(row)

    if not rows:
        raise ValueError("No usable RAVDESS audio or video samples were found.")

    return _write_manifest(rows, output_path)


def _find_row_value(record: dict, exact_names: tuple[str, ...] = (), contains_any: tuple[str, ...] = ()) -> float | None:
    normalized = {str(key).strip().lower(): value for key, value in record.items()}
    for name in exact_names:
        if name.lower() in normalized:
            return _safe_float(normalized[name.lower()])
    for key, value in normalized.items():
        if all(token in key for token in contains_any):
            return _safe_float(value)
    return None


def _safe_float(value) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _find_daic_session_dir(dataset_root: Path, participant_id: int) -> Path | None:
    expected = dataset_root / f"{participant_id}_P"
    if expected.exists():
        return expected
    matches = list(dataset_root.rglob(f"{participant_id}_P"))
    return matches[0] if matches else None


def _load_daic_transcript_text(transcript_path: Path) -> str:
    try:
        frame = pd.read_csv(transcript_path, sep="\t", engine="python")
    except Exception:
        frame = pd.read_csv(transcript_path)

    columns = {column.lower(): column for column in frame.columns}
    speaker_column = columns.get("speaker")
    value_column = None
    for candidate in ("value", "utterance", "text", "content"):
        if candidate in columns:
            value_column = columns[candidate]
            break
    if value_column is None:
        value_column = frame.columns[-1]

    if speaker_column:
        participant_rows = frame[frame[speaker_column].astype(str).str.lower().str.contains("participant")]
        if participant_rows.empty:
            participant_rows = frame[~frame[speaker_column].astype(str).str.lower().str.contains("ellie")]
        frame = participant_rows

    utterances = [str(value).strip() for value in frame[value_column].tolist() if str(value).strip() and str(value).strip().lower() != "nan"]
    return " ".join(utterances)


def _daic_labels(record: dict) -> dict:
    labels = {domain: "" for domain in PREDICTION_DOMAINS}
    phq_total = _find_row_value(record, exact_names=("PHQ8_Score", "PHQ_Score"), contains_any=("phq8", "score"))
    if phq_total is not None:
        labels["depression"] = _clip_score(phq_total / 24.0)

    sleep_item = _find_row_value(record, contains_any=("sleep",))
    if sleep_item is None:
        sleep_item = _find_row_value(record, exact_names=("PHQ8_3", "Q3"))
    if sleep_item is not None:
        labels["sleep_disorder"] = _clip_score(sleep_item / 3.0)

    energy_item = _find_row_value(record, contains_any=("energy",))
    if energy_item is None:
        energy_item = _find_row_value(record, contains_any=("tired",))
    if energy_item is None:
        energy_item = _find_row_value(record, exact_names=("PHQ8_4", "Q4"))
    if energy_item is not None:
        labels["burnout"] = _clip_score(energy_item / 3.0)

    return labels


def build_daic_woz_manifest(dataset_root: str | Path, output_path: str | Path) -> Path:
    dataset_root = Path(dataset_root)
    rows: list[dict] = []

    split_files = {
        "train": _discover_file(dataset_root, "train_split_Depression_AVEC2017.csv"),
        "dev": _discover_file(dataset_root, "dev_split_Depression_AVEC2017.csv"),
    }
    missing = [split_name for split_name, path in split_files.items() if path is None]
    if missing:
        raise FileNotFoundError(f"DAIC-WOZ split files not found for splits: {missing}")

    for split_name, split_path in split_files.items():
        frame = pd.read_csv(split_path)
        participant_column = next((column for column in frame.columns if column.lower() == "participant_id"), None)
        if participant_column is None:
            raise ValueError(f"Participant_ID column missing in {split_path}")

        for record in frame.to_dict(orient="records"):
            participant_id = int(record[participant_column])
            session_dir = _find_daic_session_dir(dataset_root, participant_id)
            if session_dir is None:
                continue

            transcript_path = session_dir / f"{participant_id}_TRANSCRIPT.csv"
            audio_path = session_dir / f"{participant_id}_AUDIO.wav"
            text = _load_daic_transcript_text(transcript_path) if transcript_path.exists() else ""

            row = _empty_row()
            row.update(
                {
                    "source_dataset": "DAIC-WOZ",
                    "source_split": split_name,
                    "sample_id": f"daic-{split_name}-{participant_id}",
                    "text": text,
                    "audio_path": str(audio_path.resolve()) if audio_path.exists() else "",
                }
            )
            row.update(_daic_labels(record))
            rows.append(row)

    if not rows:
        raise ValueError("No usable DAIC-WOZ sessions were found.")

    return _write_manifest(rows, output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build training manifests from supported public datasets.")
    subparsers = parser.add_subparsers(dest="dataset", required=True)

    meld_parser = subparsers.add_parser("meld", help="Build a proxy-label text manifest from MELD.")
    meld_parser.add_argument("dataset_root", help="Path to the MELD dataset root.")
    meld_parser.add_argument("output_path", help="Where to write the generated manifest CSV.")

    ravdess_parser = subparsers.add_parser("ravdess", help="Build proxy-label audio/image manifests from RAVDESS.")
    ravdess_parser.add_argument("dataset_root", help="Path to the RAVDESS dataset root.")
    ravdess_parser.add_argument("output_path", help="Where to write the generated manifest CSV.")
    ravdess_parser.add_argument(
        "--extract-frames",
        dest="extract_frames",
        default=None,
        help="Optional directory used to extract representative JPG frames from RAVDESS MP4 files.",
    )
    ravdess_parser.add_argument(
        "--include-song",
        dest="include_song",
        action="store_true",
        help="Include song clips in addition to speech clips.",
    )

    daic_parser = subparsers.add_parser("daic-woz", help="Build a clinically labeled text/audio manifest from DAIC-WOZ.")
    daic_parser.add_argument("dataset_root", help="Path to the DAIC-WOZ dataset root.")
    daic_parser.add_argument("output_path", help="Where to write the generated manifest CSV.")

    args = parser.parse_args()
    if args.dataset == "meld":
        output_path = build_meld_manifest(args.dataset_root, args.output_path)
    elif args.dataset == "ravdess":
        output_path = build_ravdess_manifest(
            dataset_root=args.dataset_root,
            output_path=args.output_path,
            frame_output_dir=args.extract_frames,
            speech_only=not args.include_song,
        )
    else:
        output_path = build_daic_woz_manifest(args.dataset_root, args.output_path)

    summary = {
        "dataset": args.dataset,
        "output_path": str(Path(output_path).resolve()),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
