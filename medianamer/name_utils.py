"""Heuristics for detecting whether a filename is descriptive."""

from __future__ import annotations

import re
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif", ".heic", ".heif"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv", ".m4v", ".flv", ".mpeg", ".mpg", ".3gp"}
MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

# Generic placeholder words — not treated as human-chosen names
_GENERIC_WORDS = {
    "unknown", "untitled", "image", "photo", "video", "picture", "file",
    "document", "download", "attachment", "media", "copy", "temp", "tmp",
    "new", "imported", "export", "scan", "scanned", "img", "pic", "recording",
    "audio", "clip", "movie", "screenshot", "screen", "shot", "default",
}

# Camera / phone auto-generated name patterns
_CAMERA_PATTERNS = [
    re.compile(r"^IMG[-_]?\d+$", re.IGNORECASE),
    re.compile(r"^DSC[-_]?\d+$", re.IGNORECASE),
    re.compile(r"^PXL[-_]?\d+$", re.IGNORECASE),
    re.compile(r"^VID[-_]?\d+$", re.IGNORECASE),
    re.compile(r"^MVIMG[-_]?\d+$", re.IGNORECASE),
    re.compile(r"^GOPR\d+$", re.IGNORECASE),
    re.compile(r"^GH\d+$", re.IGNORECASE),
    re.compile(r"^Screenshot[-_]?\d*$", re.IGNORECASE),
    re.compile(r"^Screen[- ]?Shot", re.IGNORECASE),
    re.compile(r"^image[-_]?\d+$", re.IGNORECASE),
    re.compile(r"^video[-_]?\d+$", re.IGNORECASE),
    re.compile(r"^photo[-_]?\d+$", re.IGNORECASE),
    re.compile(r"^snap[-_]?\d+$", re.IGNORECASE),
    re.compile(r"^recording[-_]?\d+$", re.IGNORECASE),
    re.compile(r"^unknown[-_]?\d", re.IGNORECASE),
    re.compile(r"^untitled[-_]?\d*$", re.IGNORECASE),
]

_UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)

# Downloader / CDN / auto-export prefixes
_AUTO_SOURCE_PATTERNS = [
    re.compile(r"(ssstwitter|saveclip|snaptik|tiktok|twimg|instagram|facebook|fbcdn)", re.IGNORECASE),
    re.compile(r"\.com_\d", re.IGNORECASE),
    re.compile(r"^trim\.", re.IGNORECASE),
    re.compile(r"^(videoplayback|download|clip)\.", re.IGNORECASE),
]

# Numeric ID blobs (Facebook, Instagram, timestamps)
_NUMERIC_ID_PATTERNS = [
    re.compile(r"^\d+_\d+"),
    re.compile(r"_\d{8,}"),
    re.compile(r"^\d{8,}"),
]


def _camel_case_words(name: str) -> list[str]:
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", spaced)
    return [part for part in re.split(r"[\s_\-]+", spaced) if part]


def _split_segments(name: str) -> list[str]:
    return [part for part in re.split(r"[_.\-]+", name) if part]


def _is_meaningful_word(word: str) -> bool:
    letters = re.sub(r"\d", "", word)
    if len(letters) < 4:
        return False
    if letters.lower() in _GENERIC_WORDS:
        return False
    if not re.search(r"[aeiouAEIOU]", letters):
        return False
    if letters.islower() or (letters[0].isupper() and letters[1:].islower()):
        return True
    # Intentional all-caps names (e.g. THEONEPIECEIS)
    if letters.isupper() and len(letters) >= 6:
        return True
    return False


def _has_human_phrase(name: str) -> bool:
    """True when the name contains at least one clear human-chosen word."""
    if re.search(r"['\u2019]", name):
        letters = re.sub(r"[^a-zA-Z]", "", name)
        if len(letters) >= 3:
            return True

    if " " in name:
        return any(_is_meaningful_word(word) for word in name.split())

    camel_words = _camel_case_words(name)
    meaningful = [word for word in camel_words if _is_meaningful_word(word)]
    if len(meaningful) >= 2:
        return True
    if len(meaningful) == 1 and len(re.sub(r"\d", "", meaningful[0])) >= 4:
        return True

    segments = _split_segments(name)
    if len(segments) > 1:
        return any(_is_meaningful_word(segment) for segment in segments)

    return False


def _looks_like_random_id(name: str) -> bool:
    """Detect auto-generated IDs (e.g. Twitter/X downloads like G88xPUkWAAAYKvk)."""
    if not re.fullmatch(r"[A-Za-z0-9]+", name):
        return False
    if len(name) < 10:
        return False

    if re.fullmatch(r"[a-zA-Z]{4,}\d{2,4}", name):
        return False

    words = _camel_case_words(name)
    meaningful = [word for word in words if _is_meaningful_word(word)]
    if len(meaningful) >= 2:
        return False
    if len(meaningful) == 1 and len(re.sub(r"\d", "", meaningful[0])) >= 5:
        return False

    if re.search(r"\d", name) and not re.fullmatch(r"[a-zA-Z]+\d{2,4}", name):
        return True

    if re.search(r"[A-Z]{3,}", name):
        return True

    if len(name) >= 12 and not meaningful:
        return True

    return False


def _has_auto_generated_pattern(name: str) -> bool:
    if _UUID_PATTERN.search(name):
        return True

    for pattern in _AUTO_SOURCE_PATTERNS:
        if pattern.search(name):
            return True

    for pattern in _NUMERIC_ID_PATTERNS:
        if pattern.search(name):
            return True

    for pattern in _CAMERA_PATTERNS:
        if pattern.search(name):
            return True

    segments = _split_segments(name)
    if len(segments) > 1 and not _has_human_phrase(name):
        return True

    if _looks_like_random_id(name):
        return True

    return False


def is_media_file(path: Path) -> bool:
    return path.suffix.lower() in MEDIA_EXTENSIONS


def is_image_file(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


def is_descriptive_name(stem: str) -> bool:
    """Return True when the filename (without extension) looks human-chosen."""
    if not stem or not stem.strip():
        return False

    name = stem.strip()

    if name.isdigit():
        return False

    if re.fullmatch(r"[0-9a-f]{10,}", name, re.IGNORECASE):
        return False

    if not re.search(r"[a-zA-Z]", name):
        return False

    if _has_auto_generated_pattern(name):
        return False

    return _has_human_phrase(name) or not re.search(r"[_\-.]", name)


def needs_rename(path: Path) -> bool:
    if not path.is_file() or not is_media_file(path):
        return False
    return not is_descriptive_name(path.stem)


def find_files_needing_rename(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []

    files = [
        entry
        for entry in folder.iterdir()
        if entry.is_file() and needs_rename(entry)
    ]
    return sorted(files, key=lambda p: p.name.lower())
