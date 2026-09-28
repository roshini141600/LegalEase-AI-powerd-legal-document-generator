from __future__ import annotations

from io import BytesIO
from pathlib import Path
import re

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
)
from reportlab.lib import colors

from backend.services.document_service import sanitize_text


ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"
LOGO_PATH = ASSETS_DIR / "legalease_logo.svg"


def _safe_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())
    return value.strip("_") or "legal_document"


def format_txt(text: str) -> bytes:
    return (sanitize_text(text) + "\n").encode("utf-8")


def _set_cell_shading(cell, fill: str = "E9EEF7"):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def _set_cell_margins(cell, top=100, start=100, bottom=100, end=100):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = tcPr.first_child_found_in("w:tcMar")
    if tcMar is None:
        tcMar = OxmlElement("w:tcMar")
        tcPr.append(tcMar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tcMar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tcMar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def _add_docx_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("LegalEase | AI-generated draft | Review before use")
    run.font.name = "Times New Roman"
    run.font.size = Pt(8)


def format_docx(text: str, doc_type: str) -> bytes:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(11)
    styles["Title"].font.name = "Times New Roman"
    styles["Title"].font.size = Pt(18)

    _add_docx_footer(section)

    if LOGO_PATH.exists():
        try:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str(LOGO_PATH), width=Inches(1.5))
        except Exception:
            pass

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run(doc_type.strip().upper())
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(18)

    doc.add_paragraph("")

    for line in sanitize_text(text).splitlines():
        line = line.strip()
        if not line:
            doc.add_paragraph("")
            continue

        if re.match(r"^\d+[\.\)]\s+", line) or (
            len(line) < 90 and line.isupper()
        ):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(line)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
        elif line.startswith("- "):
            p = doc.add_paragraph(style="List Bullet")
            p.add_run(line[2:])
        else:
            p = doc.add_paragraph(line)
            p.paragraph_format.space_after = Pt(5)

    # A compact terms table, when numbered terms are present.
    numbered = []
    for line in sanitize_text(text).splitlines():
        m = re.match(r"^(\d+)[\.\)]\s+(.+)$", line.strip())
        if m and len(m.group(2)) > 20:
            numbered.append((m.group(1), m.group(2)))

    if numbered:
        doc.add_page_break()
        heading = doc.add_paragraph()
        heading.add_run("Key Clauses Index").bold = True
        table = doc.add_table(rows=1, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"
        hdr = table.rows[0].cells
        hdr[0].text = "Section"
        hdr[1].text = "Clause"
        for cell in hdr:
            _set_cell_shading(cell)
            _set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for section_no, clause in numbered[:25]:
            cells = table.add_row().cells
            cells[0].text = section_no
            cells[1].text = clause[:500]
            for cell in cells:
                _set_cell_margins(cell)

    stream = BytesIO()
    doc.save(stream)
    return stream.getvalue()


def _pdf_header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawCentredString(width / 2, height - 14 * mm, "LegalEase")
    canvas.setFont("Helvetica", 7.5)
    canvas.drawCentredString(
        width / 2, 8 * mm, f"LegalEase | AI-generated draft | Page {doc.page}"
    )
    canvas.restoreState()


def format_pdf(text: str, doc_type: str) -> bytes:
    stream = BytesIO()
    doc = SimpleDocTemplate(
        stream,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=23 * mm,
        bottomMargin=16 * mm,
        title=doc_type,
        author="LegalEase",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "LegalTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=16, leading=20, alignment=TA_CENTER, spaceAfter=12
    )
    heading_style = ParagraphStyle(
        "LegalHeading", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=11, leading=14, spaceBefore=8, spaceAfter=5
    )
    body_style = ParagraphStyle(
        "LegalBody", parent=styles["BodyText"], fontName="Times-Roman",
        fontSize=10.5, leading=15, alignment=TA_LEFT, spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        "LegalBullet", parent=body_style, leftIndent=14, firstLineIndent=-7
    )

    story = [
        Spacer(1, 10 * mm),
        Paragraph("LegalEase", title_style),
        Paragraph(doc_type.strip().upper(), title_style),
        Spacer(1, 4 * mm),
    ]

    for raw in sanitize_text(text).splitlines():
        line = raw.strip()
        if not line:
            story.append(Spacer(1, 2 * mm))
        elif re.match(r"^\d+[\.\)]\s+", line) or (len(line) < 90 and line.isupper()):
            story.append(Paragraph(line.replace("&", "&amp;"), heading_style))
        elif line.startswith("- "):
            story.append(Paragraph("• " + line[2:], bullet_style))
        else:
            story.append(Paragraph(line.replace("&", "&amp;"), body_style))

    doc.build(
        story,
        onFirstPage=_pdf_header_footer,
        onLaterPages=_pdf_header_footer,
    )
    return stream.getvalue()


def export_bundle(text: str, doc_type: str) -> dict[str, bytes]:
    base = _safe_filename(doc_type)
    return {
        "txt": format_txt(text),
        "docx": format_docx(text, doc_type),
        "pdf": format_pdf(text, doc_type),
        "base_name": base.encode("utf-8"),
    }
