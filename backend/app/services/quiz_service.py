from __future__ import annotations

from ..services.content_loader import list_study_topics, get_study_topic


def get_chapter_quiz(chapter_id: str) -> dict:
    # MVP generator: builds a lightweight quiz only from existing structured chapter content.
    for topic in list_study_topics():
        detail = get_study_topic(topic["id"])
        for chapter in detail.get("chapters", []):
            if chapter.get("id") != chapter_id:
                continue

            questions = []
            for idx, item in enumerate(chapter.get("checklist", [])[:8], start=1):
                questions.append(
                    {
                        "id": f"{chapter_id}-q{idx}",
                        "difficulty": "easy" if idx <= 3 else "medium",
                        "question": f"Ai parcurs si poti explica: {item}?",
                        "type": "boolean",
                        "options": ["da", "nu"],
                        "answer": "da",
                    }
                )

            if not questions:
                questions.append(
                    {
                        "id": f"{chapter_id}-q1",
                        "difficulty": "medium",
                        "question": "Poti explica ideea centrala a capitolului in cuvintele tale?",
                        "type": "boolean",
                        "options": ["da", "nu"],
                        "answer": "da",
                    }
                )

            return {
                "chapter_id": chapter_id,
                "topic_id": detail.get("id"),
                "topic_title": detail.get("title"),
                "chapter_title": chapter.get("title"),
                "questions": questions,
                "source": "generated_from_official_chapter_content",
            }

    raise ValueError("Chapter not found")


def grade_quiz(quiz: dict, answers: dict[str, str]) -> dict:
    total = len(quiz.get("questions", []))
    score = 0
    for q in quiz.get("questions", []):
        qid = q.get("id")
        expected = q.get("answer")
        given = answers.get(qid)
        if given == expected:
            score += 1

    return {
        "score": score,
        "max_score": total,
        "pct": round((score / total) * 100) if total else 0,
    }
