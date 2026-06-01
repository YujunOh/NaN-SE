"""FastAPI 읽기 API. docs/orchestration/DASHBOARD_DESIGN.md의 계약을 구현한다.

Store(SQLite)에서 읽기만 한다. 채점·검수는 하지 않는다.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from nanse.db import Store
from nanse.learning_card.models import LearningCard

GITHUB_BASE = "https://github.com/YujunOh/nanse/blob/main/docs"

# 첫 화면에서 바로 보여줄 문서 묶음. (slug, 한 줄 소개)
DOC_GROUPS: list[dict] = [
    {
        "name": "서비스 소개",
        "docs": [
            ("VISION", "NaN-SE가 풀려는 문제와 방향"),
            ("REPORT", "프로세스에 입각한 개발 보고서 본문"),
            ("COMPETITIVE", "기존 도구와의 비교"),
        ],
    },
    {
        "name": "설계",
        "docs": [
            ("ARCHITECTURE", "모듈 구성과 검출·설명 분리 구조"),
            ("REQUIREMENTS", "페르소나·유스케이스·비기능 요구"),
            ("INTERFACES", "모듈 간 인터페이스 계약"),
            ("METRICS", "LCOM4·순환복잡도 검출 지표"),
            ("LEARNING_CARDS", "학습 카드 생성 규칙"),
        ],
    },
    {
        "name": "개발 과정",
        "docs": [
            ("LECTURE_COVERAGE", "강의 주제 대비 반영 점검"),
            ("AI_TOOLING", "AI 도구 사용 방식"),
            ("AI_USAGE", "AI 활용 기록"),
            ("DISCUSSION_LOG", "주요 의사결정 로그"),
            ("WBS", "작업 분해와 일정"),
            ("EV_LOG", "Earned Value 손계산 기록"),
            ("FUTURE_WORK", "12일 범위 밖 확장 방향"),
        ],
    },
]

_DOCS_DIR = Path(__file__).resolve().parents[2] / "docs"
_ALLOWED_SLUGS = {
    slug for group in DOC_GROUPS for slug, _ in group["docs"]
}


def _doc_path(slug: str) -> Path | None:
    if slug not in _ALLOWED_SLUGS:
        return None
    path = _DOCS_DIR / f"{slug}.md"
    if not path.is_file():
        return None
    return path


def _doc_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
        if stripped:
            break
    return fallback


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
    app = FastAPI(title="nanse dashboard API", version="0.1.0")
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

    @app.get("/api/docs")
    def docs() -> dict:
        groups = []
        for group in DOC_GROUPS:
            items = []
            for slug, blurb in group["docs"]:
                path = _doc_path(slug)
                if path is None:
                    continue
                title = _doc_title(path.read_text(encoding="utf-8"), slug)
                items.append(
                    {
                        "slug": slug,
                        "title": title,
                        "blurb": blurb,
                        "github_url": f"{GITHUB_BASE}/{slug}.md",
                    }
                )
            if items:
                groups.append({"name": group["name"], "docs": items})
        return {"groups": groups}

    @app.get("/api/docs/{slug}")
    def doc(slug: str) -> dict:
        path = _doc_path(slug)
        if path is None:
            raise HTTPException(status_code=404, detail=f"{slug} 문서 없음")
        text = path.read_text(encoding="utf-8")
        return {
            "slug": slug,
            "title": _doc_title(text, slug),
            "markdown": text,
            "github_url": f"{GITHUB_BASE}/{slug}.md",
        }

    return app
