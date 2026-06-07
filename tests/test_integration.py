"""통합 테스트: 검출 → 카드 생성 → 저장 → 검수 end-to-end.

단위 테스트가 각 부품을 따로 본다면, 여기서는 부품을 실제 흐름대로 이어 붙여
한 번에 돌린다. LLM은 주입 가능한 가짜 함수로 끊어 네트워크 없이 검증한다.
"""

import json
from pathlib import Path

from nanse.db import Store
from nanse.learning_card.generator import generate_card
from nanse.metrics import analyze_source
from nanse.metrics.findings import findings_from_cohesion

GOD_CLASS = '''
class AuthService:
    def __init__(self):
        self.user = None
        self.smtp = "h"
        self.secret = "s"
    def login(self, u, p):
        self.user = u
        return True
    def send_email(self, addr):
        return self.smtp + addr
    def issue_token(self):
        return self.secret
'''


def _fake_llm(_prompt: str) -> str:
    return json.dumps(
        {
            "violation_reason": "AuthService가 인증·이메일·토큰을 모두 담당한다.",
            "cost_example": "이메일 로직 변경 시 인증 회귀가 필요하다.",
            "before_code": "class AuthService: ...",
            "after_code": "class AuthService: ...\nclass EmailNotifier: ...",
            "learning_points": ["SRP", "책임 분리", "테스트 격리"],
            "revision_prompt": "AuthService를 책임 단위로 분리하라.",
        }
    )


def test_detect_to_review_end_to_end(tmp_path: Path) -> None:
    db = tmp_path / "nanse.db"

    # 1. 검출 (결정론적, LLM 없음)
    findings = findings_from_cohesion(analyze_source(GOD_CLASS), "auth.py")
    assert findings, "god class에서 SRP finding이 나와야 한다"
    srp = findings[0]
    assert srp.principle.name == "SRP"
    assert srp.value > srp.threshold

    with Store(db) as store:
        # 2. finding 저장
        finding_id = store.save_finding(srp, session_id="s1")

        # 3. 카드 생성 (가짜 LLM 주입, 네트워크 없음)
        card = generate_card(
            srp,
            GOD_CLASS,
            card_id=store.next_card_id(),
            session_id="s1",
            finding_id=finding_id,
            complete=_fake_llm,
        )
        assert card.principle.name == "SRP"
        assert "SRP" in card.learning_points

        # 4. 저장 후 조회
        store.save_card(card)
        assert store.get_card(card.id) is not None
        assert card.id in [c.id for c in store.all_cards()]
        assert len(store.get_unreviewed()) == 1

        # 5. 검수 (사람) — 채택하면 미검수 목록에서 빠진다
        assert store.review_card(card.id, accepted=True, feedback=None) is True
        assert store.get_unreviewed() == []
        reviewed = store.get_card(card.id)
        assert reviewed is not None and reviewed.user_accepted is True


def test_cohesive_class_produces_no_finding() -> None:
    cohesive = """
class Counter:
    def __init__(self):
        self.n = 0
    def inc(self):
        self.n += 1
    def value(self):
        return self.n
"""
    findings = findings_from_cohesion(analyze_source(cohesive))
    assert findings == []
