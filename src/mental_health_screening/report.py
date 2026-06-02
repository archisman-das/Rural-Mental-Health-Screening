from io import BytesIO

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import simpleSplit
    from reportlab.pdfgen import canvas
except ImportError:
    A4 = None
    simpleSplit = None
    canvas = None

from .constants import PREDICTION_DOMAINS, PREDICTION_LABELS


def _write_line(pdf, text: str, x: float, y: float, width: float, font_name: str = "Helvetica", font_size: int = 11):
    pdf.setFont(font_name, font_size)
    lines = simpleSplit(text, font_name, font_size, width)
    for line in lines:
        pdf.drawString(x, y, line)
        y -= font_size + 4
    return y


def create_assessment_pdf_bytes(record: dict) -> bytes:
    if canvas is None or A4 is None or simpleSplit is None:
        lines = [
            "Rural Mental Health Screening Report",
            f"Assessment ID: {record['assessment_id']}",
            f"Created At: {record['created_at']}",
        ]
        for key, value in record["profile"].items():
            lines.append(f"{key.replace('_', ' ').title()}: {value}")
        for domain in PREDICTION_DOMAINS:
            lines.append(
                f"{PREDICTION_LABELS[domain]} Questionnaire: "
                f"{record['questionnaire'].get(f'{domain}_risk', 'unknown')}"
            )
        for domain in PREDICTION_DOMAINS:
            lines.append(
                f"{PREDICTION_LABELS[domain]} Multimodal: "
                f"{record['multimodal']['overall'].get(domain, 'unknown')}"
            )
        lines.append(f"Recommendation: {record['multimodal']['recommendation']}")
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

    pdf.setTitle(f"Assessment Report {record['assessment_id']}")
    y = _write_line(pdf, "Rural Mental Health Screening Report", margin, y, width - (2 * margin), "Helvetica-Bold", 18)
    y -= 6
    y = _write_line(pdf, f"Assessment ID: {record['assessment_id']}", margin, y, width - (2 * margin))
    y = _write_line(pdf, f"Created At: {record['created_at']}", margin, y, width - (2 * margin))
    y -= 8

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(margin, y, "Candidate Profile")
    y -= 20
    for key, value in record["profile"].items():
        y = _write_line(pdf, f"{key.replace('_', ' ').title()}: {value}", margin, y, width - (2 * margin))
    y -= 8

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(margin, y, "Questionnaire Risk Summary")
    y -= 20
    for domain in PREDICTION_DOMAINS:
        label = PREDICTION_LABELS[domain]
        risk = record["questionnaire"].get(f"{domain}_risk", "unknown")
        score = record["questionnaire"].get(f"{domain}_score", 0.0)
        y = _write_line(pdf, f"{label}: {risk.capitalize()} ({score:.2f})", margin, y, width - (2 * margin))
    y -= 8

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(margin, y, "Multimodal Screening Summary")
    y -= 20
    for domain in PREDICTION_DOMAINS:
        label = PREDICTION_LABELS[domain]
        risk = record["multimodal"]["overall"].get(domain, "unknown")
        score = record["multimodal"]["overall"]["scores"].get(domain, 0.0)
        y = _write_line(pdf, f"{label}: {risk.capitalize()} ({score:.2f})", margin, y, width - (2 * margin))

    y -= 8
    y = _write_line(
        pdf,
        f"Recommendation: {record['multimodal']['recommendation']}",
        margin,
        y,
        width - (2 * margin),
        "Helvetica",
        11,
    )
    y -= 4
    y = _write_line(
        pdf,
        f"Disclaimer: {record['multimodal']['disclaimer']}",
        margin,
        y,
        width - (2 * margin),
        "Helvetica-Oblique",
        10,
    )

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
