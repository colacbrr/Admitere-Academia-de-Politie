from __future__ import annotations

from pathlib import Path
import logging
from logging.config import dictConfig

from .config import settings


def setup_logging() -> None:
    telemetry_path = Path(settings.telemetry_log_file)
    telemetry_path.parent.mkdir(parents=True, exist_ok=True)

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
                },
                "telemetry": {
                    "format": "%(asctime)s event=%(message)s"
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": settings.log_level,
                    "formatter": "default",
                },
                "telemetry_file": {
                    "class": "logging.FileHandler",
                    "level": "INFO",
                    "filename": str(telemetry_path),
                    "formatter": "telemetry",
                    "encoding": "utf-8",
                },
            },
            "root": {
                "level": settings.log_level,
                "handlers": ["console"],
            },
            "loggers": {
                "admitere.telemetry": {
                    "level": "INFO",
                    "handlers": ["telemetry_file", "console"],
                    "propagate": False,
                }
            },
        }
    )

    logging.getLogger(__name__).info(
        "logging configured level=%s telemetry_file=%s",
        settings.log_level,
        telemetry_path,
    )
