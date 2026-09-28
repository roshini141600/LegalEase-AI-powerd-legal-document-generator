from __future__ import annotations

import re
from html import escape


def sanitize_text(text: str) -> str:
    """Normalize common typography while keeping readable legal text."""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
        "\u2022": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()


def terms_to_list(terms: str) -> list[str]:
    return [
        item.strip(" -\t")
        for item in re.split(r";|\n", terms)
        if item.strip(" -\t")
    ]


def markdownish_to_html(text: str) -> str:
    """Convert the generated plain text into safe, readable HTML for Streamlit."""
    text = sanitize_text(text)
    blocks = []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            blocks.append("<div class='legal-spacer'></div>")
            continue
        escaped = escape(line)
        if re.match(r"^\d+[\.\)]\s+", line):
            blocks.append(f"<h3>{escaped}</h3>")
        elif len(line) < 90 and line.isupper():
            blocks.append(f"<h2>{escaped}</h2>")
        elif line.startswith("- "):
            blocks.append(f"<li>{escape(line[2:])}</li>")
        else:
            blocks.append(f"<p>{escaped}</p>")
    return "\n".join(blocks)
