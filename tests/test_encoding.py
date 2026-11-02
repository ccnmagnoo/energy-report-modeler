from __future__ import annotations

from pathlib import Path

MARKERS = ("Ã", "Â", "â€", "ï»¿")
SUFFIXES = {".py", ".html", ".css", ".js", ".md", ".txt"}


def test_app_sources_are_utf8_without_mojibake():
    root = Path(__file__).resolve().parents[1]
    for path in (root / "app").rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for marker in MARKERS:
            assert marker not in text, f"Mojibake {marker!r} found in {path}"
