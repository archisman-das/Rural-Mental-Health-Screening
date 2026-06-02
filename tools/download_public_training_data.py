import argparse
import shutil
import tarfile
import urllib.request
import zipfile
from pathlib import Path


MELD_ANNOTATION_URLS = {
    "train_sent_emo.csv": "https://raw.githubusercontent.com/declare-lab/MELD/master/data/MELD/train_sent_emo.csv",
    "dev_sent_emo.csv": "https://raw.githubusercontent.com/declare-lab/MELD/master/data/MELD/dev_sent_emo.csv",
    "test_sent_emo.csv": "https://raw.githubusercontent.com/declare-lab/MELD/master/data/MELD/test_sent_emo.csv",
}

MELD_RAW_URL = "https://huggingface.co/datasets/declare-lab/MELD/resolve/main/MELD.Raw.tar.gz"
RAVDESS_AUDIO_SPEECH_URL = "https://zenodo.org/records/1188976/files/Audio_Speech_Actors_01-24.zip?download=1"
RAVDESS_VIDEO_SPEECH_URL_TEMPLATE = "https://zenodo.org/records/1188976/files/Video_Speech_Actor_{actor:02d}.zip?download=1"
DAIC_REQUEST_URL = "https://dcapswoz.ict.usc.edu/"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download public training assets for MELD and RAVDESS into the local repo."
    )
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=Path("data") / "public_datasets",
        help="Base directory where downloaded datasets will be stored.",
    )
    parser.add_argument(
        "--include-meld-raw",
        action="store_true",
        help="Also download the large MELD.Raw.tar.gz archive. Not required for current text training.",
    )
    parser.add_argument(
        "--ravdess-video-actors",
        default="1,2,3,4",
        help="Comma-separated list of RAVDESS speech-video actor ids to download for image training.",
    )
    parser.add_argument(
        "--skip-extract",
        action="store_true",
        help="Download archives only and skip extraction.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download files even if they already exist locally.",
    )
    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def download_file(url: str, destination: Path, force: bool = False) -> Path:
    ensure_dir(destination.parent)
    if destination.exists() and not force:
        print(f"[skip] {destination}")
        return destination
    print(f"[download] {url}")
    with urllib.request.urlopen(url) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)
    return destination


def extract_zip(archive_path: Path, destination_dir: Path) -> None:
    marker = destination_dir / f".extracted-{archive_path.stem}"
    if marker.exists():
        print(f"[skip extract] {archive_path.name}")
        return
    ensure_dir(destination_dir)
    print(f"[extract] {archive_path.name}")
    with zipfile.ZipFile(archive_path, "r") as handle:
        handle.extractall(destination_dir)
    marker.write_text("ok", encoding="utf-8")


def extract_tar_gz(archive_path: Path, destination_dir: Path) -> None:
    marker = destination_dir / f".extracted-{archive_path.stem.replace('.tar', '')}"
    if marker.exists():
        print(f"[skip extract] {archive_path.name}")
        return
    ensure_dir(destination_dir)
    print(f"[extract] {archive_path.name}")
    with tarfile.open(archive_path, "r:gz") as handle:
        handle.extractall(destination_dir)
    marker.write_text("ok", encoding="utf-8")


def download_meld(base_dir: Path, include_raw: bool, skip_extract: bool, force: bool) -> None:
    meld_dir = base_dir / "MELD"
    annotations_dir = meld_dir / "annotations"
    raw_dir = meld_dir / "raw"

    for filename, url in MELD_ANNOTATION_URLS.items():
        download_file(url, annotations_dir / filename, force=force)

    if include_raw:
        archive_path = download_file(MELD_RAW_URL, raw_dir / "MELD.Raw.tar.gz", force=force)
        if not skip_extract:
            extract_tar_gz(archive_path, raw_dir)


def parse_actor_ids(value: str) -> list[int]:
    result = []
    for part in value.split(","):
        item = part.strip()
        if not item:
            continue
        actor = int(item)
        if actor < 1 or actor > 24:
            raise ValueError(f"RAVDESS actor id must be in 1..24, got {actor}")
        result.append(actor)
    if not result:
        raise ValueError("At least one RAVDESS video actor id is required.")
    return sorted(set(result))


def download_ravdess(base_dir: Path, actor_ids: list[int], skip_extract: bool, force: bool) -> None:
    ravdess_dir = base_dir / "RAVDESS"
    archives_dir = ravdess_dir / "archives"
    extracted_dir = ravdess_dir / "extracted"

    audio_zip = download_file(
        RAVDESS_AUDIO_SPEECH_URL,
        archives_dir / "Audio_Speech_Actors_01-24.zip",
        force=force,
    )
    if not skip_extract:
        extract_with_recovery(
            archive_path=audio_zip,
            destination_dir=extracted_dir / "audio_speech",
            url=RAVDESS_AUDIO_SPEECH_URL,
            force=force,
        )

    for actor in actor_ids:
        url = RAVDESS_VIDEO_SPEECH_URL_TEMPLATE.format(actor=actor)
        archive_path = download_file(
            url,
            archives_dir / f"Video_Speech_Actor_{actor:02d}.zip",
            force=force,
        )
        if not skip_extract:
            extract_with_recovery(
                archive_path=archive_path,
                destination_dir=extracted_dir / f"video_speech_actor_{actor:02d}",
                url=url,
                force=force,
            )


def extract_with_recovery(archive_path: Path, destination_dir: Path, url: str, force: bool) -> None:
    try:
        extract_zip(archive_path, destination_dir)
    except zipfile.BadZipFile:
        print(f"[recover] {archive_path.name} appears corrupted. Re-downloading once.")
        if archive_path.exists():
            archive_path.unlink()
        refreshed = download_file(url, archive_path, force=True)
        extract_zip(refreshed, destination_dir)


def write_daic_note(base_dir: Path) -> None:
    daic_dir = base_dir / "DAIC-WOZ"
    ensure_dir(daic_dir)
    note = (
        "DAIC-WOZ is not auto-downloaded because the official site requires a signed request form "
        "and an academic or non-profit research affiliation.\n\n"
        f"Request access at: {DAIC_REQUEST_URL}\n"
        "After approval, place the extracted DAIC-WOZ dataset in this folder.\n"
    )
    (daic_dir / "REQUEST_REQUIRED.txt").write_text(note, encoding="utf-8")


def main() -> int:
    args = parse_args()
    dataset_dir = args.dataset_dir.resolve()
    actor_ids = parse_actor_ids(args.ravdess_video_actors)

    download_meld(dataset_dir, args.include_meld_raw, args.skip_extract, args.force)
    download_ravdess(dataset_dir, actor_ids, args.skip_extract, args.force)
    write_daic_note(dataset_dir)

    print("\nSaved datasets under:")
    print(f"- {dataset_dir}")
    print("- MELD: annotation CSVs ready for text training")
    print(f"- RAVDESS: audio speech plus video speech actors {', '.join(f'{actor:02d}' for actor in actor_ids)}")
    print("- DAIC-WOZ: request-required note written locally")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
