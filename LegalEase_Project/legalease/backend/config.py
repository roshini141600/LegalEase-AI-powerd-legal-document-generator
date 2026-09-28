from functools import lru_cache
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class Settings(BaseModel):
    app_name: str = "LegalEase - AI Legal Document Generator"
    brand_name: str = Field(default_factory=lambda: os.getenv("BRAND_NAME", "LegalEase"))
    gemini_api_key: str | None = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    gemini_model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-3.8-flash"))
    backend_url: str = Field(default_factory=lambda: os.getenv("BACKEND_URL", "http://127.0.0.1:8000"))
    temperature: float = Field(default_factory=lambda: float(os.getenv("TEMPERATURE", "0.25")))
    max_output_tokens: int = Field(default_factory=lambda: int(os.getenv("MAX_OUTPUT_TOKENS", "6000")))

@lru_cache
def get_settings() -> Settings:
    return Settings()
