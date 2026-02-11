from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="candidate")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class SessionToken(Base):
    __tablename__ = "session_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class ChapterProgress(Base):
    __tablename__ = "chapter_progress"
    __table_args__ = (UniqueConstraint("user_id", "topic_id", "chapter_id", name="uq_user_chapter"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[str] = mapped_column(String(128), index=True)
    chapter_id: Mapped[str] = mapped_column(String(128), index=True)
    chapter_title: Mapped[str] = mapped_column(String(255), default="")
    visited: Mapped[bool] = mapped_column(Boolean, default=False)
    checklist_done: Mapped[int] = mapped_column(Integer, default=0)
    checklist_total: Mapped[int] = mapped_column(Integer, default=0)
    checklist_state_json: Mapped[str] = mapped_column(Text, default="{}")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    topic_id: Mapped[str] = mapped_column(String(128), index=True)
    chapter_id: Mapped[str] = mapped_column(String(128), index=True)
    score: Mapped[int] = mapped_column(Integer, default=0)
    max_score: Mapped[int] = mapped_column(Integer, default=0)
    difficulty: Mapped[str] = mapped_column(String(16), default="medium")
    answers_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class UserStreak(Base):
    __tablename__ = "user_streaks"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_streak"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    current_days: Mapped[int] = mapped_column(Integer, default=0)
    best_days: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_day: Mapped[str] = mapped_column(String(16), default="")


class UserBadge(Base):
    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_name", name="uq_user_badge_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    badge_name: Mapped[str] = mapped_column(String(64), index=True)
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)


class UserGameStats(Base):
    __tablename__ = "user_game_stats"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_game_stats"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    xp: Mapped[int] = mapped_column(Integer, default=0)
    flash_played: Mapped[int] = mapped_column(Integer, default=0)
    flash_perfect: Mapped[int] = mapped_column(Integer, default=0)
    match_played: Mapped[int] = mapped_column(Integer, default=0)
    match_perfect: Mapped[int] = mapped_column(Integer, default=0)
    timeline_played: Mapped[int] = mapped_column(Integer, default=0)
    timeline_perfect: Mapped[int] = mapped_column(Integer, default=0)
    correction_played: Mapped[int] = mapped_column(Integer, default=0)
    correction_perfect: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, onupdate=now_utc)
