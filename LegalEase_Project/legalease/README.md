# LegalEase — AI-Powered Legal Document Generator

LegalEase is a Streamlit + FastAPI application for generating editable legal-document drafts with Google Gemini and exporting them as TXT, DOCX, and PDF.

## What is included

- Streamlit frontend
- FastAPI backend
- Google GenAI SDK integration
- Configurable Gemini model through `.env`
- Legal-document prompt with structured sections
- Demo mode when no API key is configured
- Editable document preview
- TXT export
- DOCX export with branding and footer
- PDF export with header/footer
- Health-check endpoint
- Automated tests
- Windows batch files for one-click local startup

## Important update from the supplied documentation

The supplied project documentation specifies `gemini-1.5-pro`. That model is no longer available through the Gemini API. The application therefore defaults to the current configurable model `gemini-3.8-flash`. You can change `GEMINI_MODEL` in `.env` to a model available to your API key.

The project also uses the current `google-genai` SDK rather than the older `google-generativeai` package.

## Project structure

```text
LegalEase/
├── backend/
│   ├── ai_core/
│   │   └── gemini_generator.py
│   ├── services/
│   │   ├── document_service.py
│   │   └── export_service.py
│   ├── config.py
│   ├── main.py
│   ├── routes.py
│   └── schemas.py
├── frontend/
│   └── app.py
├── assets/
│   └── legalease_logo.svg
├── tests/
│   ├── test_exports.py
│   └── test_health.py
├── .env.example
├── .gitignore
├── requirements.txt
├── run_backend.bat
├── run_frontend.bat
└── README.md
```

## 1. Requirements

- Windows 10/11
- Python 3.10 or newer
- VS Code
- Internet connection for Gemini API generation
- A Gemini API key for real AI generation

## 2. Open in VS Code

Open the `LegalEase` folder in VS Code.

Then open **Terminal → New Terminal**.

## 3. Create virtual environment

PowerShell:

```powershell
py -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate
```

## 4. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure Gemini

Copy `.env.example` to `.env`.

Put your Gemini API key in:

```env
GEMINI_API_KEY=YOUR_REAL_KEY
```

The default model is:

```env
GEMINI_MODEL=gemini-3.8-flash
```

If your account does not have access to that model, set `GEMINI_MODEL` to another currently available Gemini text model.

## 6. Start the backend

Terminal 1:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## 7. Start the frontend

Open a second VS Code terminal and activate the environment again if necessary.

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run frontend/app.py
```

Open the URL printed by Streamlit, normally:

```text
http://localhost:8501
```

## 8. Test the complete workflow

1. Enter a document type.
2. Enter the parties.
3. Enter terms separated by semicolons.
4. Enter an effective date.
5. Click **Generate Document**.
6. Review and edit the generated text.
7. Open **Formatted preview**.
8. Download TXT, DOCX, and PDF.
9. Open the generated DOCX and PDF to verify formatting.

## 9. Run automated tests

With the virtual environment activated:

```powershell
pytest -q
```

The tests cover:
- FastAPI root endpoint
- FastAPI health endpoint
- TXT export
- DOCX creation
- PDF creation

## 10. Demo mode

If `GEMINI_API_KEY` is missing, LegalEase still starts and the Generate button returns a clearly labeled deterministic demo draft. This is useful for checking the frontend and export pipeline before configuring the API.

## 11. API example

POST `/generate`:

```json
{
  "document_type": "Non-Disclosure Agreement",
  "parties": "Jane Doe (Disclosing Party), Example Corp (Receiving Party)",
  "terms": "Confidentiality for 2 years; No unauthorized disclosure; Return confidential information on termination",
  "dates": "28/09/2026"
}
```

Response:

```json
{
  "document": "...",
  "model": "gemini-3.8-flash",
  "source": "gemini"
}
```

## 12. Troubleshooting

### `ModuleNotFoundError`

Make sure VS Code is using `.venv`:

- `Ctrl + Shift + P`
- `Python: Select Interpreter`
- choose `.venv`

Then run:

```powershell
pip install -r requirements.txt
```

### Backend connection error in Streamlit

Make sure the backend terminal is still running:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Then check:

```text
http://127.0.0.1:8000/health
```

### Gemini error

Check `.env` and make sure:

```env
GEMINI_API_KEY=...
```

is valid and that `GEMINI_MODEL` is available to your API key.

### PDF/DOCX generation works but AI does not

The export modules are independent from Gemini. Check `/health`; if `ai_configured` is false, the backend did not detect the API key.

## Disclaimer

LegalEase generates drafts for educational and drafting assistance. Generated text can contain omissions or jurisdiction-specific problems. A qualified legal professional should review any document before it is signed, filed, or relied upon.
