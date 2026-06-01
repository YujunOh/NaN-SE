"""finding 매핑 + 학습 카드 생성 파이프라인 테스트.

LLM 호출은 가짜 complete 함수로 주입해 네트워크 없이 검증한다.
"""

import json

import pytest

from nanse.learning_card import LearningCard
from nanse.learning_card.generator import generate_card
from nanse.learning_card.parser import parse_llm_response
from nanse.metrics import analyze_source
from nanse.metrics.findings import findings_from_cohesion
from nanse.principles import Principle


GOD = """
class AuthService:
    def __init__(self):
        self.user = None
        self.smtp_host = "localhost"
        self.token_secret = "x"
    def login(self):
        self.user = "u"
    def logout(self):
        self.user = None
    def send_email(self):
        return self.smtp_host
    def issue_token(self):
        return self.token_secret
"""

COHESIVE = """
class Counter:
    def __init__(self):
        self.count = 0
    def increment(self):
        self.count += 1
    def value(self):
        return self.count
"""

VALID_CONTENT = {
    "violation_reason": "책임이 셋으로 갈렸다",
    "cost_example": "이메일 변경 시 인증 회귀 필요",
    "before_code": "class AuthService: ...",
    "after_code": "class AuthService: ...\nclass EmailNotifier: ...",
    "learning_points": ["SRP", "책임 분리", "변경 사유 분리"],
    "revision_prompt": "AuthService를 세 클래스로 분리하라",
}


def _fake_complete(_prompt: str) -> str:
    return json.dumps(VALID_CONTENT, ensure_ascii=False)


# --- finding 매핑 ---

def test_god_class_produces_srp_finding():
    findings = findings_from_cohesion(analyze_source(GOD))
    assert len(findings) == 1
    assert findings[0].principle is Principle.SRP
    assert findings[0].metric == "lcom4"
    assert findings[0].value == 3.0
    assert findings[0].severity > 0


def test_cohesive_class_produces_no_finding():
    assert findings_from_cohesion(analyze_source(COHESIVE)) == []


# --- 파서 ---

def test_parser_handles_code_fence():
    fenced = "```json\n" + json.dumps(VALID_CONTENT) + "\n```"
    data = parse_llm_response(fenced)
    assert data["violation_reason"]


def test_parser_rejects_missing_key():
    incomplete = json.dumps({"violation_reason": "x"})
    with pytest.raises(ValueError):
        parse_llm_response(incomplete)


def test_parser_rejects_non_json():
    with pytest.raises(ValueError):
        parse_llm_response("죄송합니다 JSON이 없습니다")


def test_parser_rejects_non_list_learning_points():
    bad = dict(VALID_CONTENT)
    bad["learning_points"] = "not a list"
    with pytest.raises(ValueError):
        parse_llm_response(json.dumps(bad))


# --- 생성 파이프라인 (end-to-end, 가짜 LLM) ---

def test_generate_card_end_to_end():
    finding = findings_from_cohesion(analyze_source(GOD))[0]
    card = generate_card(
        finding,
        GOD,
        card_id="CARD-001",
        session_id="sess-1",
        finding_id=7,
        complete=_fake_complete,
    )
    assert isinstance(card, LearningCard)
    assert card.principle is Principle.SRP
    assert card.id == "CARD-001"
    assert card.finding_id == 7
    assert card.user_accepted is None
    assert len(card.code_hash) == 16
    assert len(card.learning_points) == 3


def test_generate_card_propagates_parse_error():
    finding = findings_from_cohesion(analyze_source(GOD))[0]

    def broken(_prompt: str) -> str:
        return "no json here"

    with pytest.raises(ValueError):
        generate_card(
            finding, GOD, card_id="CARD-002", session_id="s", complete=broken
        )
