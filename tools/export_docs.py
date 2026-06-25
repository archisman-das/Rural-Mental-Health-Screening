from __future__ import annotations

import argparse
import html
import re
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path


DOCX_CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

DOCX_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = unicodedata.normalize("NFKD", text)
    return text.encode("ascii", "ignore").decode("ascii")


def markdown_to_lines(markdown_text: str) -> list[str]:
    lines: list[str] = []
    in_code = False
    for raw_line in normalize_text(markdown_text).split("\n"):
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if not stripped:
            lines.append("")
            continue
        if not in_code:
            line = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", line)
            line = line.replace("`", "")
        lines.append(line)
    return lines


def escape_xml(text: str) -> str:
    return html.escape(text, quote=False)


def build_docx_document_xml(lines: list[str]) -> str:
    paragraphs = []
    for line in lines:
        text = escape_xml(line)
        if not text:
            paragraphs.append("<w:p/>")
            continue
        paragraphs.append(
            "<w:p><w:r><w:t xml:space=\"preserve\">"
            + text
            + "</w:t></w:r></w:p>"
        )
    body = "".join(paragraphs)
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:wpc=\"http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas\" "
        "xmlns:mc=\"http://schemas.openxmlformats.org/markup-compatibility/2006\" "
        "xmlns:o=\"urn:schemas-microsoft-com:office:office\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:m=\"http://schemas.openxmlformats.org/officeDocument/2006/math\" "
        "xmlns:v=\"urn:schemas-microsoft-com:vml\" "
        "xmlns:wp14=\"http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing\" "
        "xmlns:wp=\"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing\" "
        "xmlns:w10=\"urn:schemas-microsoft-com:office:word\" "
        "xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\" "
        "xmlns:w14=\"http://schemas.microsoft.com/office/word/2010/wordml\" "
        "xmlns:wpg=\"http://schemas.microsoft.com/office/word/2010/wordprocessingGroup\" "
        "xmlns:wpi=\"http://schemas.microsoft.com/office/word/2010/wordprocessingInk\" "
        "xmlns:wne=\"http://schemas.microsoft.com/office/word/2006/wordml\" "
        "xmlns:wps=\"http://schemas.microsoft.com/office/word/2010/wordprocessingShape\" "
        "mc:Ignorable=\"w14 wp14\">"
        "<w:body>"
        f"{body}"
        "<w:sectPr><w:pgSz w:w=\"12240\" w:h=\"15840\"/><w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\" w:header=\"708\" w:footer=\"708\" w:gutter=\"0\"/></w:sectPr>"
        "</w:body></w:document>"
    )


def write_docx(output_path: Path, lines: list[str]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    document_xml = build_docx_document_xml(lines)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", DOCX_CONTENT_TYPES)
        zf.writestr("_rels/.rels", DOCX_RELS)
        zf.writestr("word/document.xml", document_xml)


def _pdf_escape(text: str) -> str:
    text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return text


@dataclass
class PdfPage:
    lines: list[str]


def chunk_lines_for_pdf(lines: list[str], lines_per_page: int = 44) -> list[PdfPage]:
    pages: list[PdfPage] = []
    current: list[str] = []
    for line in lines:
        current.append(line)
        if len(current) >= lines_per_page:
            pages.append(PdfPage(lines=current))
            current = []
    if current or not pages:
        pages.append(PdfPage(lines=current))
    return pages


def build_pdf(output_path: Path, lines: list[str], title: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pages = chunk_lines_for_pdf(lines)
    width = 612
    height = 792
    margin_left = 54
    margin_top = 54
    line_height = 13
    font_size = 10

    objects: list[bytes] = []

    def add_object(content: str) -> int:
        objects.append(content.encode("latin-1"))
        return len(objects)

    font_obj = add_object("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    pages_obj_index = len(objects) + len(pages) * 2 + 1
    page_object_ids: list[int] = []
    content_object_ids: list[int] = []

    for page in pages:
        content_lines = [
            "BT",
            f"/F1 {font_size} Tf",
            f"1 0 0 1 {margin_left} {height - margin_top} Tm",
            f"{line_height} TL",
        ]
        first_line = True
        for line in page.lines:
            text = _pdf_escape(line)
            if first_line:
                content_lines.append(f"({text}) Tj")
                first_line = False
            else:
                content_lines.append("T*")
                content_lines.append(f"({text}) Tj")
        content_lines.append("ET")
        stream = "\n".join(content_lines)
        content_obj = add_object(
            f"<< /Length {len(stream.encode('latin-1'))} >>\nstream\n{stream}\nendstream"
        )
        content_object_ids.append(content_obj)
        page_obj = add_object(
            f"<< /Type /Page /Parent {pages_obj_index} 0 R /MediaBox [0 0 {width} {height}] "
            f"/Resources << /Font << /F1 {font_obj} 0 R >> >> /Contents {content_obj} 0 R >>"
        )
        page_object_ids.append(page_obj)

    kids = " ".join(f"{obj_id} 0 R" for obj_id in page_object_ids)
    pages_obj = add_object(f"<< /Type /Pages /Kids [ {kids} ] /Count {len(page_object_ids)} >>")
    catalog_obj = add_object(f"<< /Type /Catalog /Pages {pages_obj} 0 R >>")
    info_obj = add_object(
        "<< /Producer (Codex Markdown Exporter) "
        f"/Title ({_pdf_escape(title)}) "
        "/Creator (Codex) >>"
    )

    # Rebuild object ids because pages_obj and catalog_obj were appended after page objects.
    # PDF objects are referenced by their position in the final list, so we assemble in order below.
    ordered_objects: list[bytes] = []
    ordered_objects.append(objects[font_obj - 1])
    # Interleave page content and page objects in creation order.
    for content_obj, page_obj in zip(content_object_ids, page_object_ids, strict=False):
        ordered_objects.append(objects[content_obj - 1])
        ordered_objects.append(objects[page_obj - 1])
    ordered_objects.append(objects[pages_obj - 1])
    ordered_objects.append(objects[catalog_obj - 1])
    ordered_objects.append(objects[info_obj - 1])

    # Recompute object numbers in the final file.
    total_objects = len(ordered_objects)
    object_numbers = list(range(1, total_objects + 1))
    font_number = 1
    page_numbers = [2 + i * 2 + 1 for i in range(len(pages))]
    content_numbers = [2 + i * 2 for i in range(len(pages))]
    pages_number = total_objects - 2
    catalog_number = total_objects - 1
    info_number = total_objects

    # Rebuild pages and contents with correct references.
    rebuilt_objects: list[bytes] = []
    rebuilt_objects.append(objects[font_obj - 1])
    for idx, page in enumerate(pages):
        content_lines = [
            "BT",
            f"/F1 {font_size} Tf",
            f"1 0 0 1 {margin_left} {height - margin_top} Tm",
            f"{line_height} TL",
        ]
        first_line = True
        for line in page.lines:
            text = _pdf_escape(line)
            if first_line:
                content_lines.append(f"({text}) Tj")
                first_line = False
            else:
                content_lines.append("T*")
                content_lines.append(f"({text}) Tj")
        content_lines.append("ET")
        stream = "\n".join(content_lines)
        rebuilt_objects.append(
            f"<< /Length {len(stream.encode('latin-1'))} >>\nstream\n{stream}\nendstream".encode("latin-1")
        )
        rebuilt_objects.append(
            (
                f"<< /Type /Page /Parent {pages_number} 0 R /MediaBox [0 0 {width} {height}] "
                f"/Resources << /Font << /F1 {font_number} 0 R >> >> /Contents {content_numbers[idx]} 0 R >>"
            ).encode("latin-1")
        )
    kids = " ".join(f"{num} 0 R" for num in page_numbers)
    rebuilt_objects.append(f"<< /Type /Pages /Kids [ {kids} ] /Count {len(pages)} >>".encode("latin-1"))
    rebuilt_objects.append(f"<< /Type /Catalog /Pages {pages_number} 0 R >>".encode("latin-1"))
    rebuilt_objects.append(
        (
            "<< /Producer (Codex Markdown Exporter) "
            f"/Title ({_pdf_escape(title)}) "
            "/Creator (Codex) >>"
        ).encode("latin-1")
    )

    offsets: list[int] = []
    body = bytearray()
    body.extend(b"%PDF-1.4\n")
    for index, obj in enumerate(rebuilt_objects, start=1):
        offsets.append(len(body))
        body.extend(f"{index} 0 obj\n".encode("latin-1"))
        body.extend(obj)
        body.extend(b"\nendobj\n")
    xref_offset = len(body)
    body.extend(f"xref\n0 {len(rebuilt_objects) + 1}\n".encode("latin-1"))
    body.extend(b"0000000000 65535 f \n")
    for offset in offsets:
        body.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    body.extend(
        (
            "trailer\n"
            f"<< /Size {len(rebuilt_objects) + 1} /Root {len(rebuilt_objects) - 1} 0 R /Info {len(rebuilt_objects)} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("latin-1")
    )
    output_path.write_bytes(bytes(body))


def export_documents(source_dir: Path, output_dir: Path) -> list[tuple[Path, Path]]:
    exported: list[tuple[Path, Path]] = []
    for markdown_path in sorted(source_dir.glob("*.md")):
        lines = markdown_to_lines(markdown_path.read_text(encoding="utf-8"))
        stem = markdown_path.stem
        docx_path = output_dir / "docx" / f"{stem}.docx"
        pdf_path = output_dir / "pdf" / f"{stem}.pdf"
        write_docx(docx_path, lines)
        build_pdf(pdf_path, lines, title=stem.replace("_", " ").title())
        exported.append((docx_path, pdf_path))
    return exported


def main() -> None:
    parser = argparse.ArgumentParser(description="Export markdown docs to DOCX and PDF.")
    parser.add_argument("--source-dir", type=Path, default=Path("docs"), help="Directory containing markdown files.")
    parser.add_argument("--output-dir", type=Path, default=Path("doc_exports"), help="Directory for exported docx/pdf files.")
    args = parser.parse_args()
    export_documents(args.source_dir, args.output_dir)


if __name__ == "__main__":
    main()
