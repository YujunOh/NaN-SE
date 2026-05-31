"""SQLite Store 단위 테스트. tmp_path로 격리."""

from datetime import datetime

import pytest

from softgate.db import Store
from softgate.learning_card.models import LearningCard
from softgate.metrics.findings import MetricFinding
from softgate.principles import Principle


def _card(card_id: str) -> LearningCard:
    return LearningCard(
        id=card_id,
        session_id="s",
        finding_id=1,
        principle=Principle.SRP,
        severity=6,
        code_hash="abc",
        violation_reason="r",
        cost_example="c",
        before_code="b",
        after_code="a",
        learning_points=["p1", "p2"],
        revision_prompt="fix it",
        generated_at=datetime.now(),
    )


@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path / "t.db")
    yield s
    s.close()


def test_save_and_get_card(store):
    store.save_card(_card("CARD-001"))
    got = store.get_card("CARD-001")
    assert got is not None
    assert got.principle is Principle.SRP
    assert got.learning_points == ["p1", "p2"]
    assert got.user_accepted is None


def test_get_missing_card_returns_none(store):
    assert store.get_card("CARD-999") is None


def test_unreviewed_then_review(store):
    store.save_card(_card("CARD-001"))
    assert len(store.get_unreviewed()) == 1
    assert store.review_card("CARD-001", True) is True
    assert store.get_unreviewed() == []
    assert store.get_card("CARD-001").user_accepted is True


def test_review_missing_card_returns_false(store):
    assert store.review_card("CARD-404", True) is False


def test_next_card_id_increments(store):
    assert store.next_card_id() == "CARD-001"
    store.save_card(_card("CARD-001"))
    assert store.next_card_id() == "CARD-002"


def test_save_finding_returns_rowid(store):
    finding = MetricFinding(
        class_name="X", metric="lcom4", value=3.0, threshold=1.0,
        principle=Principle.SRP, severity=6,
    )
    rowid = store.save_finding(finding, "sess")
    assert rowid >= 1
