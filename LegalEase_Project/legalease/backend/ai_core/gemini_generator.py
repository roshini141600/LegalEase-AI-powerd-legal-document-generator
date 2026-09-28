from __future__ import annotations

from backend.config import get_settings


class GeminiDocumentGenerator:
    """Generate structured legal-document drafts with Google's current GenAI SDK."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None
        if self.settings.gemini_api_key:
            try:
                from google import genai
            except ImportError as exc:
                raise RuntimeError(
                    "google-genai is not installed. Run: pip install -r requirements.txt"
                ) from exc
            self._client = genai.Client(api_key=self.settings.gemini_api_key)

    @property
    def configured(self) -> bool:
        return self._client is not None

    def _build_prompt(
        self, document_type: str, parties: str, terms: str, dates: str
    ) -> str:
        return f"""
You are LegalEase, an AI assistant that drafts legal-document templates.

IMPORTANT:
- Produce a DRAFT TEMPLATE for review, not legal advice.
- Do not claim that the document is legally valid, enforceable, or suitable for a specific jurisdiction.
- Do not invent missing names, addresses, amounts, laws, registration numbers, or signatures.
- Preserve user-provided facts exactly where possible.
- Use placeholders such as [ADDRESS], [AMOUNT], [NOTICE PERIOD] when information is missing.
- Write in professional, neutral legal language.
- Include a short "Important Review Note" at the end stating that a qualified lawyer should review the document before use.
- Return plain text only. Do not use Markdown tables, code fences, or HTML.
- Use clear numbered sections and sub-sections.

Requested document type:
{document_type}

Parties:
{parties}

Effective date / dates:
{dates}

Terms and conditions:
{terms}

Required structure:
1. Document title
2. Introductory / agreement statement
3. Parties and definitions
4. Purpose / scope
5. Core terms and obligations
6. Confidentiality / intellectual property where relevant
7. Payment / consideration where relevant
8. Term and termination
9. Representations / warranties where relevant
10. Liability / dispute / governing-law placeholders where relevant
11. General provisions
12. Signatures
13. Important Review Note
""".strip()

    def generate_document(
        self, document_type: str, parties: str, terms: str, dates: str
    ) -> tuple[str, str]:
        prompt = self._build_prompt(document_type, parties, terms, dates)

        if not self._client:
            return self._demo_document(document_type, parties, terms, dates), "demo"

        try:
            from google.genai import types

            response = self._client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=self.settings.temperature,
                    max_output_tokens=self.settings.max_output_tokens,
                    candidate_count=1,
                ),
            )
            text = (response.text or "").strip()
            if not text:
                raise RuntimeError("Gemini returned an empty response.")
            return text, self.settings.gemini_model
        except Exception as exc:
            raise RuntimeError(f"Gemini generation failed: {exc}") from exc

    @staticmethod
    def _demo_document(document_type: str, parties: str, terms: str, dates: str) -> str:
        clauses = [x.strip() for x in terms.replace("\n", ";").split(";") if x.strip()]
        clause_lines = "\n".join(
            f"{index}. {clause}" for index, clause in enumerate(clauses, start=1)
        )
        return f"""{document_type.upper()}

Effective Date: {dates}

BETWEEN

{parties}

1. PURPOSE
This draft sets out the principal terms agreed by the parties for the above document type.

2. PARTIES
The parties are identified in the information supplied by the user. Any missing legal names,
addresses, registration details, or authority information should be completed before signing.

3. TERMS AND CONDITIONS
{clause_lines or "1. [INSERT AGREED TERMS]"}

4. TERM AND TERMINATION
The parties should specify the commencement period, renewal provisions, termination rights,
notice period, and consequences of termination.

5. GENERAL PROVISIONS
Any governing-law, dispute-resolution, notices, severability, amendment, assignment, and
entire-agreement clauses should be completed to match the applicable jurisdiction and deal.

6. SIGNATURES

Party 1: ______________________________
Name: __________________________________
Date: ___________________________________

Party 2: ______________________________
Name: __________________________________
Date: ___________________________________

IMPORTANT REVIEW NOTE
This is a generated template for drafting and educational purposes. It is not legal advice
and should be reviewed and adapted by a qualified legal professional before use.
"""
