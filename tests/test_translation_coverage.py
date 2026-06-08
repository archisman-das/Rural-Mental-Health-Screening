from __future__ import annotations

from pathlib import Path
import re
import unittest

from src.mental_health_screening import report as report_module


ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "web" / "app.js"


def _extract_locale_keys(text: str, locale: str) -> set[str]:
    marker = re.search(rf"\n\s+{re.escape(locale)}:\s*\{{", text)
    if not marker:
        raise AssertionError(f"Missing locale block: {locale}")
    start = marker.start()
    following = []
    for candidate in ("English", "Hindi", "Bengali"):
        if candidate == locale:
            continue
        match = re.search(rf"\n\s+{re.escape(candidate)}:\s*\{{", text[start + 1 :])
        if match:
            following.append(start + 1 + match.start())
    end = min(following) if following else len(text)
    locale_block = text[start:end]
    return set(re.findall(r"^ {4}([A-Za-z0-9_]+):", locale_block, flags=re.M))


class TranslationCoverageTests(unittest.TestCase):
    def test_report_translation_coverage_is_complete(self) -> None:
        coverage = report_module.audit_translation_coverage()
        self.assertEqual(coverage["report"], {}, coverage)
        self.assertEqual(coverage["quality_check"], {}, coverage)
        self.assertEqual(coverage["profile"], {}, coverage)
        self.assertEqual(coverage["risk"], {}, coverage)

    def test_ui_translation_coverage_is_complete(self) -> None:
        text = APP_JS.read_text(encoding="utf-8")
        english = _extract_locale_keys(text, "English")
        hindi = _extract_locale_keys(text, "Hindi")
        bengali = _extract_locale_keys(text, "Bengali")

        missing_hindi = english - hindi
        missing_bengali = english - bengali

        self.assertFalse(missing_hindi, f"Missing Hindi keys: {sorted(missing_hindi)}")
        self.assertFalse(missing_bengali, f"Missing Bengali keys: {sorted(missing_bengali)}")


if __name__ == "__main__":
    unittest.main()
