from backend.services.export_service import format_docx, format_pdf, format_txt

SAMPLE = """FREELANCE WORK CONTRACT

Effective Date: 28/09/2026

1. PARTIES
Jane Doe (Service Provider), Example Corp (Client)

2. TERMS
- Payment within 30 days
- Confidentiality applies

3. SIGNATURES
Party 1: __________________
Party 2: __________________
"""

def test_txt_export():
    assert b"FREELANCE WORK CONTRACT" in format_txt(SAMPLE)

def test_docx_export():
    data = format_docx(SAMPLE, "Freelance Work Contract")
    assert data[:2] == b"PK"

def test_pdf_export():
    data = format_pdf(SAMPLE, "Freelance Work Contract")
    assert data.startswith(b"%PDF")
