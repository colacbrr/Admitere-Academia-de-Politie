from __future__ import annotations

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[3]
GUIDE_DIR = REPO_ROOT / "guide"


def _module_title(dirname: str) -> str:
    name = re.sub(r"^\d+_", "", dirname)
    name = name.replace("_", " ").strip()
    return name.title() if name else dirname


def load_modules() -> list[dict]:
    if not GUIDE_DIR.exists():
        return []

    modules: list[dict] = []
    for entry in sorted(GUIDE_DIR.iterdir()):
        if entry.is_dir():
            modules.append(
                {
                    "id": entry.name,
                    "title": _module_title(entry.name),
                }
            )
    return modules


def load_module_detail(module_id: str) -> dict:
    module_dir = GUIDE_DIR / module_id
    if not module_dir.exists() or not module_dir.is_dir():
        return {
            "id": module_id,
            "title": _module_title(module_id),
            "items": [],
        }

    items = []
    for entry in sorted(module_dir.rglob("*")):
        if entry.is_file():
            items.append(
                {
                    "path": str(entry.relative_to(module_dir)).replace("\\", "/"),
                    "name": entry.name,
                }
            )

    return {
        "id": module_id,
        "title": _module_title(module_id),
        "items": items,
    }
