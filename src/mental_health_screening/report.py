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
        "recommendation": "Recommendation",
        "disclaimer": "Disclaimer",
        "questionnaire_suffix": "Questionnaire",
        "multimodal_suffix": "Multimodal",
        "comorbidity_signal": "Comorbidity signal",
        "comorbidity_confidence": "Comorbidity confidence",
        "unknown": "unknown",
    },
    "hindi": {
        "title": "ग्रामीण मानसिक स्वास्थ्य स्क्रीनिंग रिपोर्ट",
        "assessment_id": "आकलन आईडी",
        "created_at": "समय",
        "candidate_profile": "उम्मीदवार प्रोफ़ाइल",
        "questionnaire_summary": "प्रश्नावली जोखिम सारांश",
        "multimodal_summary": "मल्टीमॉडल स्क्रीनिंग सारांश",
        "recommendation": "सिफारिश",
        "disclaimer": "अस्वीकरण",
        "questionnaire_suffix": "प्रश्नावली",
        "multimodal_suffix": "मल्टीमॉडल",
        "comorbidity_signal": "कॉमॉर्बिडिटी संकेत",
        "comorbidity_confidence": "कॉमॉर्बिडिटी विश्वास",
        "unknown": "अज्ञात",
    },
    "bengali": {
        "title": "গ্রামীণ মানসিক স্বাস্থ্য স্ক্রিনিং রিপোর্ট",
        "assessment_id": "মূল্যায়ন আইডি",
        "created_at": "সময়",
        "candidate_profile": "প্রার্থীর প্রোফাইল",
        "questionnaire_summary": "প্রশ্নমালার ঝুঁকি সংক্ষিপ্তসার",
        "multimodal_summary": "মাল্টিমোডাল স্ক্রিনিং সংক্ষিপ্তসার",
        "recommendation": "পরামর্শ",
        "disclaimer": "সতর্কীকরণ",
        "questionnaire_suffix": "প্রশ্নমালা",
        "multimodal_suffix": "মাল্টিমোডাল",
        "comorbidity_signal": "কমোরবিডিটি সংকেত",
        "comorbidity_confidence": "কমোরবিডিটি আত্মবিশ্বাস",
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


def create_assessment_pdf_bytes(record: dict) -> bytes:
    language = _normalize_language(record.get("profile", {}).get("language", "english"))
    if canvas is None or A4 is None or simpleSplit is None:
        lines = [
            _report_text(language, "title"),
            f"{_report_text(language, 'assessment_id')}: {record['assessment_id']}",
            f"{_report_text(language, 'created_at')}: {record['created_at']}",
        ]
        for key, value in record["profile"].items():
            lines.append(f"{_profile_label(language, key)}: {value}")
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

    pdf.setTitle(f"Assessment Report {record['assessment_id']}")
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
