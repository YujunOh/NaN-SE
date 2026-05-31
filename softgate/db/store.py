"""학습 카드와 finding을 SQLite에 저장/조회.

INTERFACES.md의 LearningCard <-> learning_cards 테이블 매핑을 구현한다.
WAL 모드로 동시 읽기/쓰기 안정성을 확보한다.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from softgate.learning_card.models import LearningCard
from softgate.metrics.findings import MetricFinding
from softgate.principles import Principle

_SCHEMA = """
CREATE TABLE IF NOT EXISTS findings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    class_name  TEXT NOT NULL,
    metric      TEXT NOT NULL,
    value       REAL NOT NULL,
    threshold   REAL NOT NULL,
    principle   TEXT NOT NULL,
    severity    INTEGER NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS learning_cards (
    id              TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL,
    finding_id      INTEGER NOT NULL,
    principle       TEXT NOT NULL,
    severity        INTEGER NOT NULL,
    code_hash       TEXT NOT NULL,
    violation_reason TEXT NOT NULL,
    cost_example    TEXT NOT NULL,
    before_code     TEXT NOT NULL,
    after_code      TEXT NOT NULL,
    learning_points TEXT NOT NULL,
    revision_prompt TEXT NOT NULL,
    user_accepted   INTEGER,
    user_feedback   TEXT,
    generated_at    TEXT NOT NULL,
    reviewed_at     TEXT
);
"""


def default_db_path() -> Path:
    return Path.home() / ".softgate" / "softgate.db"


class Store:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else default_db_path()
        if self.path != Path(":memory:") and str(self.path) != ":memory:":
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> Store:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # --- findings ---

    def save_finding(self, finding: MetricFinding, session_id: str) -> int:
        cur = self.conn.execute(
            """INSERT INTO findings
               (session_id, class_name, metric, value, threshold, principle, severity, created_at)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                session_id,
                finding.class_name,
                finding.metric,
                finding.value,
                finding.threshold,
                finding.principle.value,
                finding.severity,
                datetime.now().isoformat(),
            ),
        )
        self.conn.commit()
        return int(cur.lastrowid)

    # --- learning cards ---

    def save_card(self, card: LearningCard) -> None:
        self.conn.execute(
            """INSERT OR REPLACE INTO learning_cards
               (id, session_id, finding_id, principle, severity, code_hash,
                violation_reason, cost_example, before_code, after_code,
                learning_points, revision_prompt, user_accepted, user_feedback,
                generated_at, reviewed_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                card.id,
                card.session_id,
                card.finding_id,
                card.principle.value,
                card.severity,
                card.code_hash,
                card.violation_reason,
                card.cost_example,
                card.before_code,
                card.after_code,
                json.dumps(card.learning_points, ensure_ascii=False),
                card.revision_prompt,
                None if card.user_accepted is None else int(card.user_accepted),
                card.user_feedback,
                card.generated_at.isoformat(),
                card.reviewed_at.isoformat() if card.reviewed_at else None,
            ),
        )
        self.conn.commit()

    def _row_to_card(self, row: sqlite3.Row) -> LearningCard:
        return LearningCard(
            id=row["id"],
            session_id=row["session_id"],
            finding_id=row["finding_id"],
            principle=Principle(row["principle"]),
            severity=row["severity"],
            code_hash=row["code_hash"],
            violation_reason=row["violation_reason"],
            cost_example=row["cost_example"],
            before_code=row["before_code"],
            after_code=row["after_code"],
            learning_points=json.loads(row["learning_points"]),
            revision_prompt=row["revision_prompt"],
            user_accepted=None if row["user_accepted"] is None else bool(row["user_accepted"]),
            user_feedback=row["user_feedback"],
            generated_at=datetime.fromisoformat(row["generated_at"]),
            reviewed_at=datetime.fromisoformat(row["reviewed_at"]) if row["reviewed_at"] else None,
        )

    def get_card(self, card_id: str) -> LearningCard | None:
        row = self.conn.execute(
            "SELECT * FROM learning_cards WHERE id = ?", (card_id,)
        ).fetchone()
        return self._row_to_card(row) if row else None

    def get_unreviewed(self) -> list[LearningCard]:
        rows = self.conn.execute(
            "SELECT * FROM learning_cards WHERE user_accepted IS NULL ORDER BY id"
        ).fetchall()
        return [self._row_to_card(r) for r in rows]

    def review_card(
        self, card_id: str, accepted: bool, feedback: str | None = None
    ) -> bool:
        cur = self.conn.execute(
            """UPDATE learning_cards
               SET user_accepted = ?, user_feedback = ?, reviewed_at = ?
               WHERE id = ?""",
            (int(accepted), feedback, datetime.now().isoformat(), card_id),
        )
        self.conn.commit()
        return cur.rowcount > 0

    def next_card_id(self) -> str:
        n = self.conn.execute("SELECT COUNT(*) FROM learning_cards").fetchone()[0]
        return f"CARD-{n + 1:03d}"
