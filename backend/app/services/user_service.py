from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from ..core.config import settings
from ..db.models import ChapterProgress, QuizAttempt, SessionToken, User, UserBadge, UserGameStats, UserStreak
from .security_service import create_session_token, hash_password, verify_password


def register_user(db: Session, email: str, password: str, role: str = "candidate") -> User:
    existing = db.scalar(select(User).where(User.email == email.lower().strip()))
    if existing:
        raise ValueError("Exista deja un cont cu acest email.")
    user = User(email=email.lower().strip(), password_hash=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, email: str, password: str) -> tuple[User, str, datetime]:
    user = db.scalar(select(User).where(User.email == email.lower().strip()))
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Credentiale invalide.")
    token, expires_at = create_session_token(settings.auth_token_ttl_hours)
    db.add(SessionToken(user_id=user.id, token=token, expires_at=expires_at))
    db.commit()
    return user, token, expires_at


def get_user_by_token(db: Session, token: str) -> User | None:
    now = datetime.now(timezone.utc)
    stmt = (
        select(User)
        .join(SessionToken, SessionToken.user_id == User.id)
        .where(SessionToken.token == token)
        .where(SessionToken.expires_at > now)
    )
    return db.scalar(stmt)


def logout_token(db: Session, token: str) -> None:
    db.execute(delete(SessionToken).where(SessionToken.token == token))
    db.commit()


def reset_user_password(db: Session, email: str, new_password: str) -> None:
    user = db.scalar(select(User).where(User.email == email.lower().strip()))
    if not user:
        raise ValueError("Nu exista cont pentru acest email.")
    user.password_hash = hash_password(new_password)
    db.commit()


def upsert_chapter_progress(
    db: Session,
    *,
    user_id: int,
    topic_id: str,
    chapter_id: str,
    chapter_title: str,
    visited: bool,
    checklist_done: int,
    checklist_total: int,
    checklist_state: dict[str, bool] | None = None,
) -> ChapterProgress:
    item = db.scalar(
        select(ChapterProgress)
        .where(ChapterProgress.user_id == user_id)
        .where(ChapterProgress.topic_id == topic_id)
        .where(ChapterProgress.chapter_id == chapter_id)
    )
    if not item:
        item = ChapterProgress(
            user_id=user_id,
            topic_id=topic_id,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            visited=visited,
            checklist_done=checklist_done,
            checklist_total=checklist_total,
            checklist_state_json=json.dumps(checklist_state or {}, ensure_ascii=False),
        )
        db.add(item)
    else:
        item.chapter_title = chapter_title
        item.visited = visited
        item.checklist_done = checklist_done
        item.checklist_total = checklist_total
        if checklist_state is not None:
            item.checklist_state_json = json.dumps(checklist_state, ensure_ascii=False)
    db.commit()
    db.refresh(item)
    return item


def compute_progress_summary(db: Session, user_id: int) -> dict:
    rows = db.scalars(select(ChapterProgress).where(ChapterProgress.user_id == user_id)).all()
    chapters = len(rows)
    visited = sum(1 for row in rows if row.visited)
    checklist_total = sum(row.checklist_total for row in rows)
    checklist_done = sum(row.checklist_done for row in rows)

    chapter_pct = (visited / chapters) if chapters > 0 else 0
    checklist_pct = (checklist_done / checklist_total) if checklist_total > 0 else 0
    pct = round((chapter_pct * 0.5 + checklist_pct * 0.5) * 100)
    level = min(10, max(1, (pct + 9) // 10 if pct else 1))

    streak = db.scalar(select(UserStreak).where(UserStreak.user_id == user_id))
    badges = db.scalars(select(UserBadge.badge_name).where(UserBadge.user_id == user_id)).all()

    game_stats = get_or_create_game_stats(db, user_id)
    return {
        "visited": visited,
        "chapters": chapters,
        "checklist_done": checklist_done,
        "checklist_total": checklist_total,
        "pct": pct,
        "level": level,
        "xp": calculate_xp(rows, user_id, db),
        "game_xp": game_stats.xp,
        "streak": {
            "current_days": streak.current_days if streak else 0,
            "best_days": streak.best_days if streak else 0,
        },
        "badges": badges,
    }


def calculate_xp(rows: list[ChapterProgress], user_id: int, db: Session) -> int:
    # Weighted XP as agreed: reading + checklist + quiz attempts.
    read_xp = sum(15 for row in rows if row.visited)
    checklist_xp = sum(row.checklist_done * 3 for row in rows)
    quiz_score_sum = db.scalar(select(func.coalesce(func.sum(QuizAttempt.score), 0)).where(QuizAttempt.user_id == user_id)) or 0
    return int(read_xp + checklist_xp + quiz_score_sum)


def update_streak(db: Session, user_id: int, *, did_activity: bool) -> UserStreak:
    streak = db.scalar(select(UserStreak).where(UserStreak.user_id == user_id))
    if not streak:
        streak = UserStreak(user_id=user_id, current_days=0, best_days=0, last_activity_day="")
        db.add(streak)

    if not did_activity:
        db.commit()
        db.refresh(streak)
        return streak

    today = datetime.now(timezone.utc).date()
    today_s = today.isoformat()

    if streak.last_activity_day == today_s:
        db.commit()
        db.refresh(streak)
        return streak

    if streak.last_activity_day:
        prev = datetime.fromisoformat(streak.last_activity_day).date()
        delta = (today - prev).days
        if delta == 1:
            streak.current_days += 1
        else:
            # soft reset: keep overall progress and badges, only streak bonus chain resets.
            streak.current_days = 1
    else:
        streak.current_days = 1

    streak.best_days = max(streak.best_days, streak.current_days)
    streak.last_activity_day = today_s

    db.commit()
    db.refresh(streak)
    return streak


def award_badges(db: Session, user_id: int, summary: dict) -> list[str]:
    target = []
    pct = summary.get("pct", 0)
    if pct >= 25:
        target.append("Consistent")
    if pct >= 50:
        target.append("Performer")
    if pct >= 75:
        target.append("Fast Climber")
    if pct == 100:
        target.append("Full Coverage")

    existing = set(db.scalars(select(UserBadge.badge_name).where(UserBadge.user_id == user_id)).all())
    for name in target:
        if name not in existing:
            db.add(UserBadge(user_id=user_id, badge_name=name))
    db.commit()
    return target


def export_progress_csv(db: Session, user_id: int) -> str:
    rows = db.scalars(
        select(ChapterProgress)
        .where(ChapterProgress.user_id == user_id)
        .order_by(ChapterProgress.topic_id.asc(), ChapterProgress.chapter_id.asc())
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["topic_id", "chapter_id", "chapter_title", "visited", "checklist_done", "checklist_total", "updated_at"])
    for row in rows:
        writer.writerow(
            [
                row.topic_id,
                row.chapter_id,
                row.chapter_title,
                "yes" if row.visited else "no",
                row.checklist_done,
                row.checklist_total,
                row.updated_at.isoformat() if row.updated_at else "",
            ]
        )
    return output.getvalue()


def list_chapter_progress(db: Session, user_id: int) -> list[dict]:
    rows = db.scalars(
        select(ChapterProgress)
        .where(ChapterProgress.user_id == user_id)
        .order_by(ChapterProgress.topic_id.asc(), ChapterProgress.chapter_id.asc())
    ).all()
    return [
        {
            "topic_id": row.topic_id,
            "chapter_id": row.chapter_id,
            "chapter_title": row.chapter_title,
            "visited": row.visited,
            "checklist_done": row.checklist_done,
            "checklist_total": row.checklist_total,
            "checklist_state": json.loads(row.checklist_state_json or "{}"),
            "updated_at": row.updated_at.isoformat() if row.updated_at else "",
        }
        for row in rows
    ]


def create_quiz_attempt(
    db: Session,
    *,
    user_id: int,
    topic_id: str,
    chapter_id: str,
    score: int,
    max_score: int,
    difficulty: str,
    answers: dict,
) -> QuizAttempt:
    attempt = QuizAttempt(
        user_id=user_id,
        topic_id=topic_id,
        chapter_id=chapter_id,
        score=score,
        max_score=max_score,
        difficulty=difficulty,
        answers_json=json.dumps(answers, ensure_ascii=False),
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def get_or_create_game_stats(db: Session, user_id: int) -> UserGameStats:
    row = db.scalar(select(UserGameStats).where(UserGameStats.user_id == user_id))
    if row:
        return row
    row = UserGameStats(user_id=user_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_game_stats(db: Session, user_id: int) -> dict:
    row = get_or_create_game_stats(db, user_id)
    return {
        "xp": row.xp,
        "flash_played": row.flash_played,
        "flash_perfect": row.flash_perfect,
        "match_played": row.match_played,
        "match_perfect": row.match_perfect,
        "timeline_played": row.timeline_played,
        "timeline_perfect": row.timeline_perfect,
        "correction_played": row.correction_played,
        "correction_perfect": row.correction_perfect,
    }


def upsert_game_stats(db: Session, user_id: int, payload: dict) -> dict:
    row = get_or_create_game_stats(db, user_id)
    row.xp = max(row.xp, int(payload.get("xp", row.xp)))
    row.flash_played = max(row.flash_played, int(payload.get("flash_played", row.flash_played)))
    row.flash_perfect = max(row.flash_perfect, int(payload.get("flash_perfect", row.flash_perfect)))
    row.match_played = max(row.match_played, int(payload.get("match_played", row.match_played)))
    row.match_perfect = max(row.match_perfect, int(payload.get("match_perfect", row.match_perfect)))
    row.timeline_played = max(row.timeline_played, int(payload.get("timeline_played", row.timeline_played)))
    row.timeline_perfect = max(row.timeline_perfect, int(payload.get("timeline_perfect", row.timeline_perfect)))
    row.correction_played = max(row.correction_played, int(payload.get("correction_played", row.correction_played)))
    row.correction_perfect = max(
        row.correction_perfect, int(payload.get("correction_perfect", row.correction_perfect))
    )
    db.commit()
    db.refresh(row)
    return get_game_stats(db, user_id)
