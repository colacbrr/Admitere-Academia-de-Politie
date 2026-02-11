import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Ghid Admitere API"
    app_version: str = "0.1.0"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@127.0.0.1:5432/admitere_ap"
    )
    create_tables_on_startup: bool = os.getenv("CREATE_TABLES_ON_STARTUP", "0") == "1"
    auth_token_ttl_hours: int = int(os.getenv("AUTH_TOKEN_TTL_HOURS", "48"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    telemetry_log_file: str = os.getenv("TELEMETRY_LOG_FILE", "backend/logs/telemetry.log")
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


settings = Settings()
