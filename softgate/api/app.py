"""FastAPI 읽기 API. docs/orchestration/DASHBOARD_DESIGN.md의 계약을 구현한다.

Store(SQLite)에서 읽기만 한다. 채점·검수는 하지 않는다.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from softgate.db import Store
from softgate.learning_card.models import LearningCard


def _card_summary(card: LearningCard) -> dict:
    return {
        "id": card.id,
        "principle": card.principle.value,
        "severity": card.severity,
        "violation_reason": card.violation_reason,
        "user_accepted": card.user_accepted,
        "source_file": card.source_file,
        "source_line": card.source_line,
        "generated_at": card.generated_at.isoformat(),
        "reviewed_at": card.reviewed_at.isoformat() if card.reviewed_at else None,
    }


def _card_detail(card: LearningCard) -> dict:
    return {
        "id": card.id,
        "session_id": card.session_id,
        "finding_id": card.finding_id,
        "principle": card.principle.value,
        "severity": card.severity,
        "code_hash": card.code_hash,
        "violation_reason": card.violation_reason,
        "cost_example": card.cost_example,
        "before_code": card.before_code,
        "after_code": card.after_code,
        "learning_points": card.learning_points,
        "revision_prompt": card.revision_prompt,
        "user_accepted": card.user_accepted,
        "user_feedback": card.user_feedback,
        "source_file": card.source_file,
        "source_line": card.source_line,
        "generated_at": card.generated_at.isoformat(),
        "reviewed_at": card.reviewed_at.isoformat() if card.reviewed_at else None,
    }


def _compute_stats(findings: list[dict], cards: list[LearningCard]) -> dict:
    accepted = sum(1 for c in cards if c.user_accepted is True)
    rejected = sum(1 for c in cards if c.user_accepted is False)
    pending = sum(1 for c in cards if c.user_accepted is None)
    decided = accepted + rejected
    acceptance_rate = round(accepted / decided, 4) if decided else None

    principle_counts = Counter(f["principle"] for f in findings)
    severity_counts = Counter(f["severity"] for f in findings)
    date_counts = Counter(c.generated_at.date().isoformat() for c in cards)

    return {
        "total_findings": len(findings),
        "total_cards": len(cards),
        "review": {"accepted": accepted, "rejected": rejected, "pending": pending},
        "acceptance_rate": acceptance_rate,
        "by_principle": [
            {"principle": p, "count": n} for p, n in sorted(principle_counts.items())
        ],
        "by_severity": [
            {"severity": s, "count": n} for s, n in sorted(severity_counts.items())
        ],
        "cards_over_time": [
            {"date": d, "count": n} for d, n in sorted(date_counts.items())
        ],
    }


def create_app(db_path: str | Path | None = None) -> FastAPI:
    app = FastAPI(title="softgate dashboard API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    def store() -> Store:
        return Store(db_path)

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/api/stats")
    def stats() -> dict:
        with store() as s:
            return _compute_stats(s.list_findings(), s.all_cards())

    @app.get("/api/findings")
    def findings() -> list[dict]:
        with store() as s:
            return s.list_findings()

    @app.get("/api/cards")
    def cards(status: str = "all") -> list[dict]:
        if status not in {"all", "pending", "accepted", "rejected"}:
            raise HTTPException(
                status_code=400,
                detail="status는 all|pending|accepted|rejected 중 하나",
            )
        with store() as s:
            items = s.all_cards()
        if status == "pending":
            items = [c for c in items if c.user_accepted is None]
        elif status == "accepted":
            items = [c for c in items if c.user_accepted is True]
        elif status == "rejected":
            items = [c for c in items if c.user_accepted is False]
        return [_card_summary(c) for c in items]

    @app.get("/api/cards/{card_id}")
    def card(card_id: str) -> dict:
        with store() as s:
            found = s.get_card(card_id)
        if found is None:
            raise HTTPException(status_code=404, detail=f"{card_id} 없음")
        return _card_detail(found)

    return app
