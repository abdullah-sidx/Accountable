"""
Accountable Platform — Application Settings
============================================
All config is loaded from environment variables (12-factor).
Create a `.env` file in `backend/` for local development.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str = "sqlite+aiosqlite:///./accountable.db"
    DB_ECHO: bool = False

    # ------------------------------------------------------------------
    # SMTP (escalation notifications)
    # ------------------------------------------------------------------
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USE_TLS: bool = True
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@accountable.gov.in"

    # ------------------------------------------------------------------
    # Default escalation authority contacts
    # ------------------------------------------------------------------
    DEFAULT_WARD_OFFICER_EMAIL: str = "ward.officer@municipality.gov.in"
    DEFAULT_MLA_EMAIL: str = "mla.office@assembly.gov.in"
    DEFAULT_COLLECTOR_EMAIL: str = "collector@district.gov.in"
    DEFAULT_STATE_AUTHORITY_EMAIL: str = "grievance@state.gov.in"

    # ------------------------------------------------------------------
    # RTI
    # ------------------------------------------------------------------
    RTI_PDF_DIR: str = "/tmp/accountable/rti_pdfs"
    DEFAULT_PIO_ADDRESS: str = (
        "The Public Information Officer, Concerned Department, Government of India"
    )


settings = Settings()
