from fastapi import APIRouter

from ..services.content_loader import load_modules, load_module_detail

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
