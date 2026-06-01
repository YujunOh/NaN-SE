"""학습 카드 생성 파이프라인. 본인 구현 영역.

LLM 호출은 주입 가능한 함수(complete)로 분리했다. 덕분에 테스트에서
네트워크 없이 가짜 응답을 넣을 수 있고, 벤더 교체도 이 한 점만 바꾸면 된다.
(DIP 적용. nanse가 검출하려는 바로 그 원칙을 스스로 지킨다.)
"""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import datetime

from nanse.learning_card.models import LearningCard
from nanse.learning_card.parser import parse_llm_response
from nanse.learning_card.prompts import build_prompt
from nanse.metrics.findings import MetricFinding

Completion = Callable[[str], str]

_MODEL = "claude-haiku-4-5-20251001"


def _anthropic_complete(prompt: str) -> str:
    from anthropic import Anthropic

    client = Anthropic()
    response = client.messages.create(
        model=_MODEL,
        max_tokens=1500,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def generate_card(
    finding: MetricFinding,
    code: str,
    *,
    card_id: str,
    session_id: str,
    finding_id: int = 0,
    complete: Completion | None = None,
) -> LearningCard:
    """finding과 코드를 받아 학습 카드를 생성한다.

    complete를 주지 않으면 Anthropic Haiku를 호출한다.
    """
    complete = complete or _anthropic_complete
    prompt = build_prompt(finding, code)
    parsed = parse_llm_response(complete(prompt))

    return LearningCard(
        id=card_id,
        session_id=session_id,
        finding_id=finding_id,
        principle=finding.principle,
        severity=finding.severity,
        code_hash=hashlib.sha256(code.encode("utf-8")).hexdigest()[:16],
        source_file=finding.source_file,
        source_line=finding.source_line,
        violation_reason=parsed["violation_reason"],
        cost_example=parsed["cost_example"],
        before_code=parsed["before_code"],
        after_code=parsed["after_code"],
        learning_points=parsed["learning_points"],
        revision_prompt=parsed["revision_prompt"],
        generated_at=datetime.now(),
    )
