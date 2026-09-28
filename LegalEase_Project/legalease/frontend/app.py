from __future__ import annotations

import html
import os
from datetime import date
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv

from backend.services.document_service import markdownish_to_html
from backend.services.export_service import format_docx, format_pdf, format_txt

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]
LOGO_PATH = BASE_DIR / "assets" / "legalease_logo.svg"
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .block-container {max-width: 1050px; padding-top: 2rem;}
    .hero {
        padding: 28px 24px; border-radius: 18px; margin-bottom: 20px;
        background: linear-gradient(135deg, #0b1220, #17243a);
        color: white; border: 1px solid #26364f;
    }
    .hero h1 {margin: 0; font-size: 2.2rem;}
    .hero p {margin: 8px 0 0; color: #c9d5e8;}
    .preview {
        background: #0e1420; color: #eef3fa; border: 1px solid #2c3a50;
        border-radius: 14px; padding: 24px; max-height: 620px; overflow-y: auto;
        line-height: 1.6;
    }
    .preview h2 {font-size: 1.15rem; margin-top: 1.2rem;}
    .preview h3 {font-size: 1rem; margin-top: 1rem;}
    .legal-spacer {height: 5px;}
    .notice {padding: 12px 14px; border-radius: 10px; background: #fff7df; color: #513d00;}
</style>
""",
    unsafe_allow_html=True,
)

if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=110)

st.markdown(
    """
<div class="hero">
  <h1>LegalEase</h1>
  <p>AI-powered legal document drafting, editing and export.</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("LegalEase")
    st.caption("Drafting assistant — not a substitute for legal advice.")
    st.divider()
    if st.button("Check backend", use_container_width=True):
        try:
            r = requests.get(f"{BACKEND_URL}/health", timeout=5)
            r.raise_for_status()
            data = r.json()
            st.success(f"Backend: {data['status']}")
            if data.get("ai_configured"):
                st.info("Gemini API key detected.")
            else:
                st.warning("No Gemini key: demo mode is active.")
        except requests.RequestException as exc:
            st.error(f"Backend unavailable: {exc}")

st.subheader("1. Document details")

document_type = st.text_input(
    "Document type",
    placeholder="e.g. Freelance Work Contract, NDA, Lease Agreement",
)

parties = st.text_area(
    "Parties involved",
    placeholder="e.g. Jane Doe (Service Provider), TechNova Inc. (Client)",
    height=110,
)

terms = st.text_area(
    "Terms & conditions",
    placeholder=(
        "Use semicolons for separate clauses. Example: "
        "Payment within 30 days; Confidentiality applies; "
        "Either party may terminate with 15 days notice"
    ),
    height=150,
)

dates = st.text_input(
    "Effective date / dates",
    value=date.today().strftime("%d/%m/%Y"),
)

generate = st.button(
    "⚖️ Generate Document",
    type="primary",
    use_container_width=True,
)

if generate:
    missing = [
        label
        for label, value in [
            ("Document type", document_type),
            ("Parties involved", parties),
            ("Terms & conditions", terms),
            ("Effective date / dates", dates),
        ]
        if not value.strip()
    ]
    if missing:
        st.error("Please complete: " + ", ".join(missing))
    else:
        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "dates": dates,
        }
        try:
            with st.spinner("Generating your legal draft..."):
                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=180,
                )
            if response.status_code >= 400:
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                raise RuntimeError(detail)

            data = response.json()
            st.session_state["generated_text"] = data["document"]
            st.session_state["model"] = data.get("model", "unknown")
            st.session_state["source"] = data.get("source", "unknown")
            st.success(
                f"Document generated successfully using {st.session_state['model']}."
            )
        except (requests.RequestException, RuntimeError) as exc:
            st.error(f"Generation failed: {exc}")

if "generated_text" in st.session_state:
    st.divider()
    st.subheader("2. Preview and edit")
    st.caption(
        f"Generation source: {st.session_state.get('source', 'unknown')} | "
        "You can edit the text before exporting."
    )

    edited_text = st.text_area(
        "Edit document",
        value=st.session_state["generated_text"],
        height=500,
        key="editor",
    )
    st.session_state["generated_text"] = edited_text

    with st.expander("Formatted preview", expanded=True):
        preview_html = markdownish_to_html(edited_text)
        st.markdown(
            f'<div class="preview">{preview_html}</div>',
            unsafe_allow_html=True,
        )

    st.subheader("3. Download")
    safe_name = "".join(
        c if c.isalnum() or c in " _-" else "_"
        for c in document_type
    ).strip() or "legal_document"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "⬇️ Download TXT",
            data=format_txt(edited_text),
            file_name=f"{safe_name}.txt",
            mime="text/plain",
            width="stretch",
            on_click="ignore",
        )
    with col2:
        st.download_button(
            "⬇️ Download DOCX",
            data=format_docx(edited_text, document_type),
            file_name=f"{safe_name}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            width="stretch",
            on_click="ignore",
        )
    with col3:
        st.download_button(
            "⬇️ Download PDF",
            data=format_pdf(edited_text, document_type),
            file_name=f"{safe_name}.pdf",
            mime="application/pdf",
            width="stretch",
            on_click="ignore",
        )

    st.markdown(
        '<div class="notice"><b>Review before signing:</b> '
        'AI-generated legal drafts may contain omissions or jurisdiction-specific issues. '
        'Have a qualified legal professional review the final document.</div>',
        unsafe_allow_html=True,
    )
