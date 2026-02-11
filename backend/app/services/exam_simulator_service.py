from __future__ import annotations

from datetime import datetime, timezone


OFFICIAL_PUBLIC_SETS = [
    {
        "id": "sim-2026-official-template",
        "title": "Simulator oficial (template 2026)",
        "description": "Simularea foloseste doar structura oficiala; itemii se completeaza exclusiv din seturi publice/oficiale.",
        "duration_minutes": 180,
        "status": "template",
        "source_policy": "official_or_public_only",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
]


def list_official_sim_sessions() -> list[dict]:
    return OFFICIAL_PUBLIC_SETS
