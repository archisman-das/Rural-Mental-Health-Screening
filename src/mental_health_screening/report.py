from io import BytesIO
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import simpleSplit
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    A4 = None
    simpleSplit = None
    canvas = None
    pdfmetrics = None
    TTFont = None

from .constants import PREDICTION_DOMAINS, PREDICTION_LABELS


REPORT_TRANSLATIONS = {
    "english": {
        "title": "Rural Mental Health Screening Report",
        "assessment_id": "Assessment ID",
        "created_at": "Created At",
        "candidate_profile": "Candidate Profile",
        "questionnaire_summary": "Questionnaire Risk Summary",
        "multimodal_summary": "Multimodal Screening Summary",
        "sdoh_summary": "SDOH and agrarian distress",
        "risk_score": "Risk score",
        "detected": "Detected",
        "not_detected": "Not detected",
        "matches": "Matches",
        "no_sdoh_data": "No agrarian distress cues were available in the exported record.",
        "recommendation": "Recommendation",
        "disclaimer": "Disclaimer",
        "screening_mode": "Screening mode",
        "review_required": "Review required",
        "model_version": "Model version",
        "validated_instrument": "Validated instrument",
        "questionnaire_suffix": "Questionnaire",
        "multimodal_suffix": "Multimodal",
        "comorbidity_signal": "Comorbidity signal",
        "comorbidity_confidence": "Comorbidity confidence",
        "unknown": "unknown",
    },
    "hindi": {
        "title": "??????? ?????? ????????? ?????????? ???????",
        "assessment_id": "???? ????",
        "created_at": "???",
        "candidate_profile": "????????? ?????????",
        "questionnaire_summary": "?????????? ????? ??????",
        "multimodal_summary": "????????? ?????????? ??????",
        "sdoh_summary": "SDOH ?? ???? ????",
        "risk_score": "????? ?????",
        "detected": "???? ???",
        "not_detected": "???? ???? ???",
        "matches": "?????",
        "no_sdoh_data": "????????? ??????? ??? ???? ???? ?? ??? ????? ?????? ???? ???",
        "recommendation": "???????",
        "disclaimer": "????????",
        "screening_mode": "?????????? ???",
        "review_required": "??????? ??????",
        "model_version": "???? ???????",
        "validated_instrument": "????????? ??????????",
        "questionnaire_suffix": "??????????",
        "multimodal_suffix": "?????????",
        "comorbidity_signal": "???????????? ?????",
        "comorbidity_confidence": "???????????? ???????",
        "unknown": "??????",
    },
    "bengali": {
        "title": "??????? ?????? ????????? ????????? ???????",
        "assessment_id": "????????? ????",
        "created_at": "????",
        "candidate_profile": "????????? ????????",
        "questionnaire_summary": "??????????? ????? ??????",
        "multimodal_summary": "??????????? ????????? ??????",
        "sdoh_summary": "SDOH ? ????? ????",
        "risk_score": "????? ?????",
        "detected": "?????? ??????",
        "not_detected": "?????? ?????",
        "matches": "???",
        "no_sdoh_data": "????????? ??????? ????? ?????? ???? ????? ?????? ???????",
        "recommendation": "???????",
        "disclaimer": "?????????",
        "screening_mode": "????????? ???",
        "review_required": "?????????? ????????",
        "model_version": "???? ???????",
        "validated_instrument": "?????????????? ??????????",
        "questionnaire_suffix": "??????????",
        "multimodal_suffix": "???????????",
        "comorbidity_signal": "?????????? ?????",
        "comorbidity_confidence": "?????????? ???????????",
        "unknown": "?????",
    },
}

QUALITY_CHECK_TRANSLATIONS = {
    "english": {
        "title": "Saved Assessment Quality Check",
        "generated_at": "Generated at",
        "summary": "Summary",
        "records": "Records",
        "examples": "Examples",
        "accuracy": "Accuracy",
        "macro_f1": "Macro F1",
        "brier_score": "Brier score",
        "roc_auc": "ROC AUC",
        "quality_gate": "Quality gate",
        "thresholds": "Thresholds",
        "min_accuracy": "Minimum accuracy",
        "min_macro_f1": "Minimum macro F1",
        "max_brier_score": "Maximum Brier score",
        "mismatches": "Top mismatches",
        "assessment_id": "Assessment ID",
        "domain": "Domain",
        "questionnaire": "Questionnaire",
        "dashboard": "Dashboard",
        "confidence": "Confidence",
        "score_gap": "Score gap",
        "pass": "PASS",
        "fail": "FAIL",
        "unknown": "Unknown",
    },
    "hindi": {
        "title": "सहेजे गए आकलनों की गुणवत्ता जाँच",
        "generated_at": "जनरेट किया गया",
        "summary": "सारांश",
        "records": "रिकॉर्ड",
        "examples": "उदाहरण",
        "accuracy": "सटीकता",
        "macro_f1": "मैक्रो F1",
        "brier_score": "ब्रियर स्कोर",
        "roc_auc": "ROC AUC",
        "quality_gate": "क्वालिटी गेट",
        "thresholds": "सीमाएँ",
        "min_accuracy": "न्यूनतम सटीकता",
        "min_macro_f1": "न्यूनतम मैक्रो F1",
        "max_brier_score": "अधिकतम ब्रियर स्कोर",
        "mismatches": "शीर्ष असंगतियाँ",
        "assessment_id": "आकलन आईडी",
        "domain": "डोमेन",
        "questionnaire": "प्रश्नावली",
        "dashboard": "डैशबोर्ड",
        "confidence": "विश्वास",
        "score_gap": "स्कोर अंतर",
        "pass": "पास",
        "fail": "फेल",
        "unknown": "अज्ञात",
    },
    "bengali": {
        "title": "সংরক্ষিত মূল্যায়নের মান যাচাই",
        "generated_at": "তৈরি হয়েছে",
        "summary": "সারাংশ",
        "records": "রেকর্ড",
        "examples": "উদাহরণ",
        "accuracy": "নির্ভুলতা",
        "macro_f1": "ম্যাক্রো F1",
        "brier_score": "ব্রায়ার স্কোর",
        "roc_auc": "ROC AUC",
        "quality_gate": "গুণগত মানের গেট",
        "thresholds": "সীমা",
        "min_accuracy": "ন্যূনতম নির্ভুলতা",
        "min_macro_f1": "ন্যূনতম ম্যাক্রো F1",
        "max_brier_score": "সর্বোচ্চ ব্রায়ার স্কোর",
        "mismatches": "প্রধান অমিল",
        "assessment_id": "মূল্যায়ন আইডি",
        "domain": "ডোমেইন",
        "questionnaire": "প্রশ্নমালা",
        "dashboard": "ড্যাশবোর্ড",
        "confidence": "আত্মবিশ্বাস",
        "score_gap": "স্কোর পার্থক্য",
        "pass": "PASS",
        "fail": "FAIL",
        "unknown": "অজানা",
    },
}

PROFILE_LABELS = {
    "english": {
        "full_name": "Full Name",
        "age": "Age",
        "gender": "Gender",
        "village": "Village",
        "phone": "Phone",
        "assessor": "Assessor",
        "language": "Language",
    },
    "hindi": {
        "full_name": "पूरा नाम",
        "age": "आयु",
        "gender": "लिंग",
        "village": "गाँव",
        "phone": "फ़ोन",
        "assessor": "आकलनकर्ता",
        "language": "भाषा",
    },
    "bengali": {
        "full_name": "পূর্ণ নাম",
        "age": "বয়স",
        "gender": "লিঙ্গ",
        "village": "গ্রাম",
        "phone": "ফোন",
        "assessor": "মূল্যায়নকারী",
        "language": "ভাষা",
    },
}

RISK_LABELS = {
    "english": {"low": "Low", "moderate": "Moderate", "high": "High", "unknown": "Unknown"},
    "hindi": {"low": "कम", "moderate": "मध्यम", "high": "उच्च", "unknown": "अज्ञात"},
    "bengali": {"low": "কম", "moderate": "মাঝারি", "high": "উচ্চ", "unknown": "অজানা"},
}


def audit_translation_coverage() -> dict:
    def _compare(table: dict) -> dict:
        source = table.get("english", {})
        source_keys = set(source.keys())
        result = {}
        for locale, entries in table.items():
            if locale == "english":
                continue
            entry_keys = set(entries.keys())
            missing = sorted(source_keys - entry_keys)
            extra = sorted(entry_keys - source_keys)
            if missing or extra:
                result[locale] = {"missing": missing, "extra": extra}
        return result

    return {
        "report": _compare(REPORT_TRANSLATIONS),
        "quality_check": _compare(QUALITY_CHECK_TRANSLATIONS),
        "profile": _compare(PROFILE_LABELS),
        "risk": _compare(RISK_LABELS),
    }

UNICODE_FONT_CANDIDATES = {
    "hindi": [
        Path("C:/Windows/Fonts/mangal.ttf"),
        Path("C:/Windows/Fonts/Nirmala.ttf"),
        Path("C:/Windows/Fonts/NirmalaB.ttf"),
    ],
    "bengali": [
        Path("C:/Windows/Fonts/Nirmala.ttf"),
        Path("C:/Windows/Fonts/NirmalaB.ttf"),
        Path("C:/Windows/Fonts/Vrinda.ttf"),
    ],
}


def _normalize_language(value: str | None) -> str:
    text = str(value or "english").strip().lower()
    if text in {"hindi", "hi", "हिंदी", "हिन्दी"}:
        return "hindi"
    if text in {"bengali", "bangla", "bn", "বাংলা"}:
        return "bengali"
    return "english"


def _report_text(language: str, key: str) -> str:
    lang = _normalize_language(language)
    return REPORT_TRANSLATIONS.get(lang, REPORT_TRANSLATIONS["english"]).get(key, key)


def _profile_label(language: str, key: str) -> str:
    lang = _normalize_language(language)
    return PROFILE_LABELS.get(lang, PROFILE_LABELS["english"]).get(key, key.replace("_", " ").title())


def _risk_label(language: str, risk: str) -> str:
    lang = _normalize_language(language)
    return RISK_LABELS.get(lang, RISK_LABELS["english"]).get(str(risk or "unknown").lower(), str(risk or "unknown"))


def _domain_label(language: str, domain: str) -> str:
    lang = _normalize_language(language)
    if lang == "hindi":
        mapping = {
            "depression": "डिप्रेशन",
            "anxiety": "एंग्जायटी",
            "stress": "तनाव",
            "sleep_disorder": "नींद संबंधी समस्या",
            "burnout": "बर्नआउट",
            "loneliness": "अकेलापन",
            "substance_abuse": "पदार्थ दुरुपयोग",
        }
        return mapping.get(domain, PREDICTION_LABELS[domain])
    if lang == "bengali":
        mapping = {
            "depression": "বিষণ্নতা",
            "anxiety": "উদ্বেগ",
            "stress": "চাপ",
            "sleep_disorder": "ঘুমের সমস্যা",
            "burnout": "বার্নআউট",
            "loneliness": "একাকীত্ব",
            "substance_abuse": "পদার্থের অপব্যবহার",
        }
        return mapping.get(domain, PREDICTION_LABELS[domain])
    return PREDICTION_LABELS[domain]


def _sdoh_label(language: str, key: str) -> str:
    lang = _normalize_language(language)
    if lang == "hindi":
        mapping = {
            "agrarian_distress": "कृषि संकट",
            "crop_failure": "फसल खराबी",
            "debt_distress": "कर्ज दबाव",
            "food_security": "खाद्य सुरक्षा",
        }
        return mapping.get(key, key.replace("_", " ").title())
    if lang == "bengali":
        mapping = {
            "agrarian_distress": "কৃষিজ সংকট",
            "crop_failure": "ফসলহানি",
            "debt_distress": "দেনার চাপ",
            "food_security": "খাদ্য নিরাপত্তা",
        }
        return mapping.get(key, key.replace("_", " ").title())
    mapping = {
        "agrarian_distress": "Agrarian Distress",
        "crop_failure": "Crop Failure",
        "debt_distress": "Debt Pressure",
        "food_security": "Food Security",
    }
    return mapping.get(key, key.replace("_", " ").title())


def _sdoh_summary_lines(record: dict, language: str) -> list[str]:
    multimodal = record.get("multimodal") or {}
    text_result = multimodal.get("text") or {}
    features = text_result.get("features") or {}
    if not isinstance(features, dict):
        features = {}

    risk_score = features.get("agrarian_distress_risk_score")
    if risk_score is None:
        return [_report_text(language, "no_sdoh_data")]

    lines = []
    lines.append(f"{_report_text(language, 'risk_score')}: {float(risk_score):.2f}")
    for key in ("agrarian_distress", "crop_failure", "debt_distress", "food_security"):
        detected = bool(features.get(f"{key}_detected"))
        matches = features.get(f"{key}_matches") or []
        line = f"{_sdoh_label(language, key)}: {_report_text(language, 'detected') if detected else _report_text(language, 'not_detected')}"
        if matches:
            line += f" ({_report_text(language, 'matches')}: {', '.join(matches)})"
        lines.append(line)
    return lines


def _is_demo_record(record: dict) -> bool:
    assessment_id = str((record or {}).get("assessment_id") or "").upper()
    profile = (record or {}).get("profile") or {}
    record_origin = str((record or {}).get("record_origin") or profile.get("record_origin") or "").strip().lower()
    return assessment_id.startswith("MHS-DEMO") or record_origin == "demo"


def _unicode_font_name(language: str) -> str | None:
    lang = _normalize_language(language)
    if lang == "english" or pdfmetrics is None or TTFont is None:
        return None
    for candidate in UNICODE_FONT_CANDIDATES.get(lang, []):
        if candidate.exists():
            font_name = f"dashboard_{lang}_font"
            try:
                pdfmetrics.getFont(font_name)
            except KeyError:
                pdfmetrics.registerFont(TTFont(font_name, str(candidate)))
            return font_name
    return None


def _write_line(pdf, text: str, x: float, y: float, width: float, font_name: str = "Helvetica", font_size: int = 11):
    pdf.setFont(font_name, font_size)
    lines = simpleSplit(text, font_name, font_size, width)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= font_size + 4
    return y


def _quality_text(language: str, key: str) -> str:
    lang = _normalize_language(language)
    return QUALITY_CHECK_TRANSLATIONS.get(lang, QUALITY_CHECK_TRANSLATIONS["english"]).get(
        key,
        QUALITY_CHECK_TRANSLATIONS["english"].get(key, key),
    )


def _new_page_if_needed(pdf, y: float, margin: float, width: float, body_font: str, heading_font: str) -> float:
    if y > margin + 30:
        return y
    pdf.showPage()
    pdf.setFont(heading_font, 18)
    return A4[1] - 50


def create_quality_check_pdf_bytes(report: dict, language: str = "english") -> bytes:
    if canvas is None or A4 is None or simpleSplit is None:
        raise ImportError("reportlab is required to generate quality check PDFs.")

    lang = _normalize_language(language)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - 50
    body_font = _unicode_font_name(lang) or "Helvetica"
    heading_font = body_font

    overall = report.get("overall") or {}
    thresholds = report.get("quality_thresholds") or {}
    mismatch_rows = list(report.get("top_mismatches") or [])[:5]
    gate_pass = (
        overall.get("accuracy") is not None
        and overall.get("macro_f1") is not None
        and overall.get("brier_score") is not None
        and float(overall.get("accuracy") or 0.0) >= float(thresholds.get("min_accuracy", 0.0) or 0.0)
        and float(overall.get("macro_f1") or 0.0) >= float(thresholds.get("min_macro_f1", 0.0) or 0.0)
        and float(overall.get("brier_score") or 0.0) <= float(thresholds.get("max_brier_score", 999.0) or 999.0)
    )

    pdf.setTitle(_quality_text(lang, "title"))
    y = _write_line(pdf, _quality_text(lang, "title"), margin, y, width - (2 * margin), heading_font, 18)
    y -= 6
    y = _write_line(
        pdf,
        f"{_quality_text(lang, 'generated_at')}: {report.get('generated_at') or report.get('source') or _quality_text(lang, 'unknown')}",
        margin,
        y,
        width - (2 * margin),
        body_font,
        11,
    )
    y -= 8

    pdf.setFont(heading_font, 13)
    pdf.drawString(margin, y, _quality_text(lang, "summary"))
    y -= 20
    summary_lines = [
        f"{_quality_text(lang, 'records')}: {report.get('record_count', 0)}",
        f"{_quality_text(lang, 'examples')}: {report.get('example_count', 0)}",
        f"{_quality_text(lang, 'accuracy')}: {float(overall.get('accuracy', 0.0)):.3f}" if overall.get("accuracy") is not None else f"{_quality_text(lang, 'accuracy')}: {_quality_text(lang, 'unknown')}",
        f"{_quality_text(lang, 'macro_f1')}: {float(overall.get('macro_f1', 0.0)):.3f}" if overall.get("macro_f1") is not None else f"{_quality_text(lang, 'macro_f1')}: {_quality_text(lang, 'unknown')}",
        f"{_quality_text(lang, 'brier_score')}: {float(overall.get('brier_score', 0.0)):.3f}" if overall.get("brier_score") is not None else f"{_quality_text(lang, 'brier_score')}: {_quality_text(lang, 'unknown')}",
        f"{_quality_text(lang, 'roc_auc')}: {float(overall.get('roc_auc', 0.0)):.3f}" if overall.get("roc_auc") is not None else f"{_quality_text(lang, 'roc_auc')}: {_quality_text(lang, 'unknown')}",
        f"{_quality_text(lang, 'quality_gate')}: {_quality_text(lang, 'pass') if gate_pass else _quality_text(lang, 'fail')}",
    ]
    for line in summary_lines:
        y = _write_line(pdf, line, margin, y, width - (2 * margin), body_font, 11)
        y = _new_page_if_needed(pdf, y, margin, width, body_font, heading_font)

    y -= 4
    pdf.setFont(heading_font, 13)
    pdf.drawString(margin, y, _quality_text(lang, "thresholds"))
    y -= 20
    threshold_lines = [
        f"{_quality_text(lang, 'min_accuracy')}: {float(thresholds.get('min_accuracy', 0.0) or 0.0):.3f}",
        f"{_quality_text(lang, 'min_macro_f1')}: {float(thresholds.get('min_macro_f1', 0.0) or 0.0):.3f}",
        f"{_quality_text(lang, 'max_brier_score')}: {float(thresholds.get('max_brier_score', 0.0) or 0.0):.3f}",
    ]
    for line in threshold_lines:
        y = _write_line(pdf, line, margin, y, width - (2 * margin), body_font, 11)
        y = _new_page_if_needed(pdf, y, margin, width, body_font, heading_font)

    y -= 4
    pdf.setFont(heading_font, 13)
    pdf.drawString(margin, y, _quality_text(lang, "mismatches"))
    y -= 20
    if not mismatch_rows:
        y = _write_line(pdf, _quality_text(lang, "unknown"), margin, y, width - (2 * margin), body_font, 11)
    else:
        for item in mismatch_rows:
            domain = item.get("domain") or _quality_text(lang, "unknown")
            label = item.get("assessment_id") or _quality_text(lang, "unknown")
            question_label = item.get("questionnaire_label") or _quality_text(lang, "unknown")
            predicted_label = item.get("predicted_label") or _quality_text(lang, "unknown")
            confidence = float(item.get("confidence", 0.0) or 0.0)
            score_gap = float(item.get("score_gap", 0.0) or 0.0)
            mismatch_text = (
                f"{_quality_text(lang, 'assessment_id')}: {label} | "
                f"{_quality_text(lang, 'domain')}: {domain} | "
                f"{_quality_text(lang, 'questionnaire')}: {question_label} -> "
                f"{_quality_text(lang, 'dashboard')}: {predicted_label} | "
                f"{_quality_text(lang, 'confidence')}: {confidence:.3f} | "
                f"{_quality_text(lang, 'score_gap')}: {score_gap:.3f}"
            )
            y = _write_line(pdf, mismatch_text, margin, y, width - (2 * margin), body_font, 10)
            y = _new_page_if_needed(pdf, y, margin, width, body_font, heading_font)

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()


def create_assessment_pdf_bytes(record: dict) -> bytes:
    if _is_demo_record(record):
        raise ValueError("Demo records are excluded from assessment reports.")
    language = _normalize_language(record.get("profile", {}).get("language", "english"))
    if canvas is None or A4 is None or simpleSplit is None:
        lines = [
            _report_text(language, "title"),
            f"{_report_text(language, 'assessment_id')}: {record['assessment_id']}",
            f"{_report_text(language, 'created_at')}: {record['created_at']}",
        ]
        for key, value in record["profile"].items():
            lines.append(f"{_profile_label(language, key)}: {value}")
        validated_instrument = (record.get("questionnaire") or {}).get("validated_instrument") or {}
        if isinstance(validated_instrument, dict) and validated_instrument.get("label"):
            lines.append(f"{_report_text(language, 'validated_instrument')}: {validated_instrument.get('localized_label') or validated_instrument.get('label')}")
        for domain in PREDICTION_DOMAINS:
            lines.append(
                f"{_domain_label(language, domain)} {_report_text(language, 'questionnaire_suffix')}: "
                f"{_risk_label(language, record['questionnaire'].get(f'{domain}_risk', 'unknown'))}"
            )
        for domain in PREDICTION_DOMAINS:
            lines.append(
                f"{_domain_label(language, domain)} {_report_text(language, 'multimodal_suffix')}: "
                f"{_risk_label(language, record['multimodal']['overall'].get(domain, 'unknown'))}"
            )
        lines.append(_report_text(language, "sdoh_summary"))
        lines.extend(_sdoh_summary_lines(record, language))
        comorbidity = record.get("multimodal", {}).get("comorbidity") or {}
        top_pairs = comorbidity.get("top_pairs") or []
        if top_pairs:
            top_pair = top_pairs[0]
            domains = top_pair.get("domains") or []
        if len(domains) == 2:
            pair_label = f"{_domain_label(language, domains[0])} + {_domain_label(language, domains[1])}"
            lines.append(
                f"{_report_text(language, 'comorbidity_signal')}: {pair_label} "
                f"({float(top_pair.get('probability', 0.0) or 0.0):.2f})"
            )
        if comorbidity.get("confidence") is not None:
            lines.append(
                f"{_report_text(language, 'comorbidity_confidence')}: "
                f"{float(comorbidity.get('confidence', 0.0) or 0.0):.2f}"
            )
        governance = (record.get("model_stats") or {}).get("screening_governance") or record.get("screening_governance") or {}
        if governance:
            lines.append(f"{_report_text(language, 'screening_mode')}: {governance.get('screening_mode', 'screening_only')}")
            lines.append(f"{_report_text(language, 'review_required')}: {bool(governance.get('review_required', False))}")
        lines.append(f"{_report_text(language, 'recommendation')}: {record['multimodal']['recommendation']}")
        text_stream = ["BT", "/F1 11 Tf", "40 800 Td"]
        for line in lines:
            escaped = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            text_stream.append(f"({escaped}) Tj")
            text_stream.append("0 -16 Td")
        text_stream.append("ET")
        content = "\n".join(text_stream).encode("latin-1", errors="replace")
        objects = []
        objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
        objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
        objects.append(
            b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n"
        )
        objects.append(
            f"4 0 obj << /Length {len(content)} >> stream\n".encode("latin-1")
            + content
            + b"\nendstream endobj\n"
        )
        objects.append(b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")

        pdf = BytesIO()
        pdf.write(b"%PDF-1.4\n")
        offsets = [0]
        for obj in objects:
            offsets.append(pdf.tell())
            pdf.write(obj)
        xref_start = pdf.tell()
        pdf.write(f"xref\n0 {len(offsets)}\n".encode("latin-1"))
        pdf.write(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            pdf.write(f"{offset:010d} 00000 n \n".encode("latin-1"))
        pdf.write(
            (
                f"trailer << /Size {len(offsets)} /Root 1 0 R >>\n"
                f"startxref\n{xref_start}\n%%EOF"
            ).encode("latin-1")
        )
        return pdf.getvalue()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - 50
    body_font = _unicode_font_name(language) or "Helvetica"
    heading_font = body_font

    pdf.setTitle(f"{_report_text(language, 'title')} {record['assessment_id']}")
    y = _write_line(pdf, _report_text(language, "title"), margin, y, width - (2 * margin), heading_font, 18)
    y -= 6
    y = _write_line(pdf, f"{_report_text(language, 'assessment_id')}: {record['assessment_id']}", margin, y, width - (2 * margin), body_font, 11)
    y = _write_line(pdf, f"{_report_text(language, 'created_at')}: {record['created_at']}", margin, y, width - (2 * margin), body_font, 11)
    y -= 8

    pdf.setFont(heading_font, 13)
    pdf.drawString(margin, y, _report_text(language, "candidate_profile"))
    y -= 20
    for key, value in record["profile"].items():
        y = _write_line(pdf, f"{_profile_label(language, key)}: {value}", margin, y, width - (2 * margin), body_font, 11)
    validated_instrument = (record.get("questionnaire") or {}).get("validated_instrument") or {}
    if isinstance(validated_instrument, dict) and validated_instrument.get("label"):
        y = _write_line(
            pdf,
            f"{_report_text(language, 'validated_instrument')}: {validated_instrument.get('localized_label') or validated_instrument.get('label')}",
            margin,
            y,
            width - (2 * margin),
            body_font,
            11,
        )
    y -= 8

    pdf.setFont(heading_font, 13)
    pdf.drawString(margin, y, _report_text(language, "questionnaire_summary"))
    y -= 20
    for domain in PREDICTION_DOMAINS:
        label = _domain_label(language, domain)
        risk = _risk_label(language, record["questionnaire"].get(f"{domain}_risk", "unknown"))
        score = record["questionnaire"].get(f"{domain}_score", 0.0)
        y = _write_line(pdf, f"{label}: {risk} ({score:.2f})", margin, y, width - (2 * margin), body_font, 11)
    y -= 8

    pdf.setFont(heading_font, 13)
    pdf.drawString(margin, y, _report_text(language, "multimodal_summary"))
    y -= 20
    for domain in PREDICTION_DOMAINS:
        label = _domain_label(language, domain)
        risk = _risk_label(language, record["multimodal"]["overall"].get(domain, "unknown"))
        score = record["multimodal"]["overall"]["scores"].get(domain, 0.0)
        y = _write_line(pdf, f"{label}: {risk} ({score:.2f})", margin, y, width - (2 * margin), body_font, 11)

    y -= 8
    pdf.setFont(heading_font, 13)
    pdf.drawString(margin, y, _report_text(language, "sdoh_summary"))
    y -= 20
    for line in _sdoh_summary_lines(record, language):
        y = _write_line(pdf, line, margin, y, width - (2 * margin), body_font, 11)
        y = _new_page_if_needed(pdf, y, margin, width, body_font, heading_font)

    y -= 8
    comorbidity = record.get("multimodal", {}).get("comorbidity") or {}
    top_pairs = comorbidity.get("top_pairs") or []
    if top_pairs:
        top_pair = top_pairs[0]
        domains = top_pair.get("domains") or []
        if len(domains) == 2:
            pair_label = f"{_domain_label(language, domains[0])} + {_domain_label(language, domains[1])}"
            y = _write_line(
                pdf,
                f"{_report_text(language, 'comorbidity_signal')}: {pair_label} ({float(top_pair.get('probability', 0.0) or 0.0):.2f})",
                margin,
                y,
                width - (2 * margin),
                body_font,
                11,
            )
            y -= 4
    if comorbidity.get("confidence") is not None:
        y = _write_line(
            pdf,
            f"{_report_text(language, 'comorbidity_confidence')}: {float(comorbidity.get('confidence', 0.0) or 0.0):.2f}",
            margin,
            y,
            width - (2 * margin),
            body_font,
            11,
        )
        y -= 4
    governance = (record.get("model_stats") or {}).get("screening_governance") or record.get("screening_governance") or {}
    if governance:
        y = _write_line(
            pdf,
            f"{_report_text(language, 'screening_mode')}: {governance.get('screening_mode', 'screening_only')}",
            margin,
            y,
            width - (2 * margin),
            body_font,
            11,
        )
        y = _write_line(
            pdf,
            f"{_report_text(language, 'review_required')}: {bool(governance.get('review_required', False))}",
            margin,
            y,
            width - (2 * margin),
            body_font,
            11,
        )
    y = _write_line(
        pdf,
        f"{_report_text(language, 'recommendation')}: {record['multimodal']['recommendation']}",
        margin,
        y,
        width - (2 * margin),
        body_font,
        11,
    )
    y -= 4
    y = _write_line(
        pdf,
        f"{_report_text(language, 'disclaimer')}: {record['multimodal']['disclaimer']}",
        margin,
        y,
        width - (2 * margin),
        body_font,
        10,
    )

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
