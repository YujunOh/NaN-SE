"""학습 카드 생성 파이프라인. 본인 구현 영역.

LLM 호출은 주입 가능한 함수(complete)로 분리했다. 덕분에 테스트에서
네트워크 없이 가짜 응답을 넣을 수 있고, 벤더 교체도 이 한 점만 바꾸면 된다.
(DIP 적용. nanse가 검출하려는 바로 그 원칙을 스스로 지킨다.)
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Callable
from datetime import datetime

from nanse.learning_card.models import LearningCard
from nanse.learning_card.parser import parse_llm_response
from nanse.learning_card.prompts import build_prompt
from nanse.metrics.findings import MetricFinding

Completion = Callable[[str], str]

_ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
_GEMINI_MODEL = os.environ.get("NANSE_GEMINI_MODEL", "gemini-2.5-flash")


def _anthropic_complete(prompt: str) -> str:
    from anthropic import Anthropic

    client = Anthropic()
    response = client.messages.create(
        model=_ANTHROPIC_MODEL,
        max_tokens=1500,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def _gemini_complete(prompt: str) -> str:
    from google import genai  # pip install google-genai

    client = genai.Client()  # GEMINI_API_KEY 환경변수를 자동으로 읽는다
    response = client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
    return response.text


def default_complete(prompt: str) -> str:
    """provider를 환경변수로 고른다. 검출은 LLM과 무관하고 이 설명층만 갈린다.

    NANSE_LLM이 있으면 그 값(anthropic·gemini)을 따르고, 없으면 키 존재로 추론한다.
    GEMINI_API_KEY만 있으면 Gemini, 아니면 Anthropic이 기본이다.
    """
    provider = os.environ.get("NANSE_LLM", "").lower()
    if not provider:
        has_gemini = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
        has_anthropic = bool(os.environ.get("ANTHROPIC_API_KEY"))
        provider = "gemini" if has_gemini and not has_anthropic else "anthropic"
    return _gemini_complete(prompt) if provider == "gemini" else _anthropic_complete(prompt)


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

    complete를 주지 않으면 default_complete가 provider(Anthropic·Gemini)를 고른다.
    """
    complete = complete or default_complete
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
