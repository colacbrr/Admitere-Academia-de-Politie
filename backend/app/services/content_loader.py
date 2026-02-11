from __future__ import annotations

from pathlib import Path
import re
from urllib.parse import quote


REPO_ROOT = Path(__file__).resolve().parents[3]
GUIDE_DIR = REPO_ROOT / "guide"
PDF_ROOT = REPO_ROOT
EXAMS_ARCHIVE_CANDIDATES = [
    REPO_ROOT / "Subiecte-raspunsuri-din-anii-precedenti" / "Subiecte-raspunsuri-din-anii-precedenti",
    REPO_ROOT / "Subiecte-raspunsuri-din-anii-precedenti",
]


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


def _extract_summary(markdown_path: Path) -> str | None:
    if not markdown_path.exists():
        return None

    lines = markdown_path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        if clean.startswith("#"):
            continue
        return clean[:260]
    return None


def _clean_md_line(line: str) -> str:
    value = line.strip()
    value = re.sub(r"^\*\*(.+)\*\*$", r"\1", value)
    return value.strip()


def _parse_markdown_chapter(markdown_path: Path) -> dict:
    title = markdown_path.stem.replace("_", " ").title()
    summary = ""
    learn: list[str] = []
    prepare: list[str] = []
    details: list[str] = []
    examples: list[str] = []
    checklist: list[str] = []
    sources: list[str] = []
    current_section = ""

    for raw_line in markdown_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            title = line[2:].strip()
            continue

        normalized = _clean_md_line(line).lower()
        section_aliases = {
            "rezumat": "rezumat",
            "detalii": "detalii",
            "explicatie detaliata": "detalii",
            "surse": "surse",
            "capitole": "detalii",
            "identificare": "ignore",
            "ce trebuie sa invete candidatul": "invata",
            "ce trebuie sa pregateasca candidatul": "pregateste",
            "exemple clare": "exemple",
            "checklist rapid (pentru utilizator)": "checklist",
        }
        if normalized in section_aliases:
            current_section = section_aliases[normalized]
            continue

        content = line.lstrip("- ").strip()
        content = re.sub(r"^\[.\]\s*", "", content)
        content = _clean_md_line(content)
        if not content:
            continue

        if current_section == "ignore":
            continue
        if current_section == "invata":
            learn.append(content)
        elif current_section == "pregateste":
            prepare.append(content)
        elif current_section == "rezumat":
            if summary:
                summary = f"{summary} {content}"
            else:
                summary = content
        elif current_section == "detalii":
            details.append(content)
        elif current_section == "exemple":
            examples.append(content)
        elif current_section == "checklist":
            checklist.append(content)
        elif current_section == "surse":
            sources.append(content)
        elif not summary:
            summary = content

    if not summary:
        summary = "Rezumat indisponibil momentan."

    return {
        "id": markdown_path.stem,
        "title": title,
        "learning_objectives": learn,
        "preparation_steps": prepare,
        "summary": summary,
        "details": details,
        "examples": examples,
        "checklist": checklist,
        "sources": sources,
        "path": str(markdown_path.relative_to(GUIDE_DIR)).replace("\\", "/"),
    }


def _topic_chapters(topic_id: str) -> list[dict]:
    topic_dir = GUIDE_DIR / topic_id
    if not topic_dir.exists() or not topic_dir.is_dir():
        return []

    chapters: list[dict] = []
    hidden_names = {
        "INDEX.MD",
        "QUALITY_90_CHECK.MD",
        "QUALITY_CHECK.MD",
        "CONTENT_CHECKLIST.MD",
        "README.MD",
    }
    for md_file in sorted(topic_dir.rglob("*.md")):
        upper_name = md_file.name.upper()
        upper_stem = md_file.stem.upper()
        if upper_name in hidden_names:
            continue
        if upper_stem.endswith("_CHECK"):
            continue
        chapters.append(_parse_markdown_chapter(md_file))

    return chapters


def _main_pdf_name() -> str | None:
    pdfs = sorted(PDF_ROOT.glob("*.pdf"))
    if not pdfs:
        return None
    return pdfs[0].name


def list_study_topics() -> list[dict]:
    pdf_name = _main_pdf_name()
    pdf_url = f"/api/assets/pdfs/{quote(pdf_name)}" if pdf_name else None
    topics = []

    for module in load_modules():
        module_id = module["id"]
        if module_id.startswith("00_"):
            continue
        summary = _extract_summary(GUIDE_DIR / module_id / "INDEX.md")
        chapter_count = len(_topic_chapters(module_id))
        topics.append(
            {
                "id": module_id,
                "title": module["title"],
                "summary": summary
                or "Rezumat in lucru. Foloseste PDF-ul oficial pentru detalii complete.",
                "chapter_count": chapter_count,
                "pdf_name": pdf_name,
                "pdf_url": pdf_url,
            }
        )

    return topics


def get_study_topic(topic_id: str) -> dict:
    module = load_module_detail(topic_id)
    topic = next((entry for entry in list_study_topics() if entry["id"] == topic_id), None)
    chapters = _topic_chapters(topic_id)
    if topic is None:
        return {
            "id": topic_id,
            "title": _module_title(topic_id),
            "summary": "Tema nu a fost gasita.",
            "chapter_count": 0,
            "pdf_name": None,
            "pdf_url": None,
            "chapters": [],
            "files": [],
        }

    return {
        **topic,
        "chapters": chapters,
        "files": module["items"],
    }


def resolve_pdf_file(pdf_name: str) -> Path | None:
    file_path = (PDF_ROOT / pdf_name).resolve()
    if not str(file_path).startswith(str(PDF_ROOT.resolve())):
        return None
    if not file_path.exists() or file_path.suffix.lower() != ".pdf":
        return None
    return file_path


def resolve_module_pdf_file(module_id: str, relative_path: str) -> Path | None:
    module_dir = (GUIDE_DIR / module_id).resolve()
    if not module_dir.exists() or not module_dir.is_dir():
        return None

    file_path = (module_dir / relative_path).resolve()
    if not str(file_path).startswith(str(module_dir)):
        return None
    if not file_path.exists() or not file_path.is_file() or file_path.suffix.lower() != ".pdf":
        return None
    return file_path


def _find_exams_archive_root() -> Path | None:
    for candidate in EXAMS_ARCHIVE_CANDIDATES:
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def list_official_exam_pdfs() -> dict:
    root = _find_exams_archive_root()
    if root is None:
        return {"root": "", "categories": []}

    categories: list[dict] = []
    for category_dir in sorted(root.iterdir()):
        if not category_dir.is_dir():
            continue
        years: list[dict] = []
        for year_dir in sorted(category_dir.iterdir()):
            if not year_dir.is_dir():
                continue
            files = []
            for pdf in sorted(year_dir.rglob("*.pdf")):
                rel = str(pdf.relative_to(root)).replace("\\", "/")
                files.append(
                    {
                        "name": pdf.name,
                        "path": rel,
                        "url": f"/api/assets/exams/{quote(rel)}",
                    }
                )
            if files:
                years.append({"year": year_dir.name, "files": files})
        if years:
            categories.append({"name": category_dir.name, "years": years})

    return {
        "root": str(root.relative_to(REPO_ROOT)).replace("\\", "/"),
        "categories": categories,
    }


def resolve_official_exam_pdf(file_path: str) -> Path | None:
    root = _find_exams_archive_root()
    if root is None:
        return None
    full = (root / file_path).resolve()
    if not str(full).startswith(str(root.resolve())):
        return None
    if not full.exists() or not full.is_file() or full.suffix.lower() != ".pdf":
        return None
    return full
