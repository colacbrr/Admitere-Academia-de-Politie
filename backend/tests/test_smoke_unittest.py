from __future__ import annotations

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import TelemetryEventPayload, telemetry_event
from app.db.base import Base
from app.services.user_service import (
    compute_progress_summary,
    get_game_stats,
    login_user,
    register_user,
    reset_user_password,
    upsert_chapter_progress,
    upsert_game_stats,
)


class SmokeServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            future=True,
        )
        cls.SessionLocal = sessionmaker(bind=cls.engine, autoflush=False, autocommit=False, future=True)
        Base.metadata.create_all(bind=cls.engine)

    def setUp(self) -> None:
        self.db = self.SessionLocal()

    def tearDown(self) -> None:
        self.db.close()

    def test_auth_and_progress_smoke(self) -> None:
        user = register_user(self.db, "smoke@example.com", "Parola1234", "candidate")
        _, token, _ = login_user(self.db, "smoke@example.com", "Parola1234")
        self.assertTrue(token)

        row = upsert_chapter_progress(
            self.db,
            user_id=user.id,
            topic_id="03_proba_scrisa",
            chapter_id="limba_romana/gramatica_sintaxa",
            chapter_title="Gramatica si sintaxa",
            visited=True,
            checklist_done=2,
            checklist_total=5,
            checklist_state={"0": True, "1": True},
        )
        self.assertTrue(row.visited)

        summary = compute_progress_summary(self.db, user.id)
        self.assertEqual(summary["visited"], 1)
        self.assertEqual(summary["checklist_done"], 2)

    def test_reset_password_smoke(self) -> None:
        register_user(self.db, "reset@example.com", "Parola1234", "candidate")
        reset_user_password(self.db, "reset@example.com", "ParolaNoua5678")

        with self.assertRaises(ValueError):
            login_user(self.db, "reset@example.com", "Parola1234")

        _, token, _ = login_user(self.db, "reset@example.com", "ParolaNoua5678")
        self.assertTrue(token)

    def test_game_stats_and_telemetry_smoke(self) -> None:
        user = register_user(self.db, "game@example.com", "Parola1234", "candidate")
        stats = upsert_game_stats(
            self.db,
            user.id,
            {
                "xp": 120,
                "flash_played": 3,
                "flash_perfect": 1,
                "match_played": 2,
                "match_perfect": 1,
                "timeline_played": 1,
                "timeline_perfect": 0,
                "correction_played": 1,
                "correction_perfect": 1,
            },
        )
        self.assertEqual(stats["xp"], 120)
        self.assertEqual(get_game_stats(self.db, user.id)["flash_played"], 3)

        payload = TelemetryEventPayload(
            event_name="game_finished",
            page="study",
            topic_id="03_proba_scrisa",
            chapter_id="istorie/statul_si_politica",
            game_type="match",
            score=4,
            meta={"source": "unittest"},
        )
        result = telemetry_event(payload=payload, user=None)
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main()
