from pathlib import Path
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..services.content_loader import (
    get_study_topic,
    list_study_topics,
    list_official_exam_pdfs,
    load_module_detail,
    load_modules,
    resolve_module_pdf_file,
    resolve_official_exam_pdf,
    resolve_pdf_file,
)
from ..db.session import get_db
from ..services.user_service import (
    award_badges,
    compute_progress_summary,
    create_quiz_attempt,
    export_progress_csv,
    get_user_by_token,
    get_game_stats,
    list_chapter_progress,
    login_user,
    logout_token,
    register_user,
    reset_user_password,
    update_streak,
    upsert_game_stats,
    upsert_chapter_progress,
)
from ..services.quiz_service import get_chapter_quiz, grade_quiz
from ..services.exam_simulator_service import list_official_sim_sessions

router = APIRouter()
logger = logging.getLogger("admitere.telemetry")


class RegisterPayload(BaseModel):
    email: str
    password: str = Field(min_length=8)
    role: str = "candidate"


class LoginPayload(BaseModel):
    email: str
    password: str


class ResetPasswordPayload(BaseModel):
    email: str
    new_password: str = Field(min_length=8)


class ProgressUpsertPayload(BaseModel):
    topic_id: str
    chapter_id: str
    chapter_title: str = ""
    visited: bool = True
    checklist_done: int = 0
    checklist_total: int = 0
    checklist_state: dict[str, bool] = Field(default_factory=dict)


class QuizSubmitPayload(BaseModel):
    answers: dict[str, str]


class GameStatsPayload(BaseModel):
    xp: int = 0
    flash_played: int = 0
    flash_perfect: int = 0
    match_played: int = 0
    match_perfect: int = 0
    timeline_played: int = 0
    timeline_perfect: int = 0
    correction_played: int = 0
    correction_perfect: int = 0


class TelemetryEventPayload(BaseModel):
    event_name: str = Field(min_length=2, max_length=64)
    page: str = ""
    chapter_id: str = ""
    topic_id: str = ""
    game_type: str = ""
    score: int = 0
    meta: dict[str, str | int | float | bool] = Field(default_factory=dict)


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Invalid Authorization scheme")
    return authorization[len(prefix):].strip()


def _current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    token = _extract_bearer_token(authorization)
    user = get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user, token


def _optional_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not authorization:
        return None
    try:
        token = _extract_bearer_token(authorization)
    except HTTPException:
        return None
    return get_user_by_token(db, token)


@router.get("/health")
def health_check() -> dict:
    return {
        "status": "ok",
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/telemetry/event")
def telemetry_event(
    payload: TelemetryEventPayload,
    user=Depends(_optional_user),
) -> dict:
    logger.info(
        "telemetry_event name=%s user_id=%s page=%s topic=%s chapter=%s game=%s score=%s meta=%s",
        payload.event_name,
        getattr(user, "id", None),
        payload.page,
        payload.topic_id,
        payload.chapter_id,
        payload.game_type,
        payload.score,
        payload.meta,
    )
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


@router.get("/study/exams")
def study_exam_archive() -> dict:
    return list_official_exam_pdfs()


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


@router.get("/assets/modules/{module_id}/{file_path:path}")
def study_module_pdf(module_id: str, file_path: str) -> FileResponse:
    pdf_file = resolve_module_pdf_file(module_id, file_path)
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


@router.get("/assets/exams/{file_path:path}")
def study_exam_pdf(file_path: str) -> FileResponse:
    pdf_file = resolve_official_exam_pdf(file_path)
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


@router.post("/auth/register")
def auth_register(payload: RegisterPayload, db: Session = Depends(get_db)) -> dict:
    try:
        user = register_user(db, payload.email, payload.password, payload.role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat(),
    }


@router.post("/auth/login")
def auth_login(payload: LoginPayload, db: Session = Depends(get_db)) -> dict:
    try:
        user, token, expires_at = login_user(db, payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return {
        "token_type": "bearer",
        "access_token": token,
        "expires_at": expires_at.isoformat(),
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        },
    }


@router.post("/auth/reset-password")
def auth_reset_password(payload: ResetPasswordPayload, db: Session = Depends(get_db)) -> dict:
    try:
        reset_user_password(db, payload.email, payload.new_password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ok"}


@router.post("/auth/logout")
def auth_logout(
    current: tuple = Depends(_current_user),
    db: Session = Depends(get_db),
) -> dict:
    _, token = current
    logout_token(db, token)
    return {"status": "ok"}


@router.get("/auth/me")
def auth_me(current: tuple = Depends(_current_user)) -> dict:
    user, _ = current
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat(),
    }


@router.post("/progress/chapter")
def progress_upsert(
    payload: ProgressUpsertPayload,
    current: tuple = Depends(_current_user),
    db: Session = Depends(get_db),
) -> dict:
    user, _ = current
    row = upsert_chapter_progress(
        db,
        user_id=user.id,
        topic_id=payload.topic_id,
        chapter_id=payload.chapter_id,
        chapter_title=payload.chapter_title,
        visited=payload.visited,
        checklist_done=payload.checklist_done,
        checklist_total=payload.checklist_total,
        checklist_state=payload.checklist_state,
    )
    update_streak(db, user.id, did_activity=True)
    summary = compute_progress_summary(db, user.id)
    award_badges(db, user.id, summary)
    return {
        "id": row.id,
        "topic_id": row.topic_id,
        "chapter_id": row.chapter_id,
        "visited": row.visited,
        "checklist_done": row.checklist_done,
        "checklist_total": row.checklist_total,
        "checklist_state": payload.checklist_state,
        "summary": summary,
    }


@router.get("/progress/summary")
def progress_summary(
    current: tuple = Depends(_current_user),
    db: Session = Depends(get_db),
) -> dict:
    user, _ = current
    summary = compute_progress_summary(db, user.id)
    badges = award_badges(db, user.id, summary)
    summary["badges"] = badges
    return summary


@router.get("/progress/chapters")
def progress_chapters(
    current: tuple = Depends(_current_user),
    db: Session = Depends(get_db),
) -> dict:
    user, _ = current
    return {"items": list_chapter_progress(db, user.id)}


@router.get("/progress/games")
def progress_games(
    current: tuple = Depends(_current_user),
    db: Session = Depends(get_db),
) -> dict:
    user, _ = current
    return get_game_stats(db, user.id)


@router.post("/progress/games")
def progress_games_upsert(
    payload: GameStatsPayload,
    current: tuple = Depends(_current_user),
    db: Session = Depends(get_db),
) -> dict:
    user, _ = current
    return upsert_game_stats(db, user.id, payload.model_dump())


@router.get("/export/progress.csv")
def progress_export_csv(
    current: tuple = Depends(_current_user),
    db: Session = Depends(get_db),
):
    user, _ = current
    csv_text = export_progress_csv(db, user.id)
    filename = f"progress_user_{user.id}.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return PlainTextResponse(content=csv_text, media_type="text/csv", headers=headers)


@router.get("/quiz/{chapter_id}")
def chapter_quiz(chapter_id: str) -> dict:
    try:
        return get_chapter_quiz(chapter_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/quiz/{chapter_id}/submit")
def chapter_quiz_submit(
    chapter_id: str,
    payload: QuizSubmitPayload,
    current: tuple = Depends(_current_user),
    db: Session = Depends(get_db),
) -> dict:
    user, _ = current
    try:
        quiz = get_chapter_quiz(chapter_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    result = grade_quiz(quiz, payload.answers)
    attempt = create_quiz_attempt(
        db,
        user_id=user.id,
        topic_id=quiz.get("topic_id", ""),
        chapter_id=chapter_id,
        score=result["score"],
        max_score=result["max_score"],
        difficulty="medium",
        answers=payload.answers,
    )
    update_streak(db, user.id, did_activity=True)
    return {
        "attempt_id": attempt.id,
        "score": result["score"],
        "max_score": result["max_score"],
        "pct": result["pct"],
    }


@router.get("/exam/sessions/official")
def exam_sessions_official() -> dict:
    return {"items": list_official_sim_sessions()}
