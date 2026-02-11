from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..services.content_loader import (
    get_study_topic,
    list_study_topics,
    load_module_detail,
    load_modules,
    resolve_pdf_file,
)

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@router.get("/modules")
def list_modules() -> list[dict]:
    return load_modules()


@router.get("/modules/{module_id}")
def get_module(module_id: str) -> dict:
    return load_module_detail(module_id)


@router.get("/study/topics")
def study_topics() -> list[dict]:
    return list_study_topics()


@router.get("/study/topics/{topic_id}")
def study_topic_detail(topic_id: str) -> dict:
    return get_study_topic(topic_id)


@router.get("/assets/pdfs/{pdf_name:path}")
def study_pdf(pdf_name: str) -> FileResponse:
    pdf_file = resolve_pdf_file(pdf_name)
    if pdf_file is None:
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        path=Path(pdf_file),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{pdf_file.name}"',
            "Cache-Control": "public, max-age=3600",
        },
    )
