"""LLM 응답(JSON 문자열)을 검증된 dict로 파싱. 본인 구현 영역.

LLM이 코드펜스로 감싸거나 앞뒤에 군더더기를 붙이는 경우를 견딘다.
필수 키가 빠지거나 타입이 어긋나면 ValueError를 던진다.
"""

from __future__ import annotations

import json
import re

REQUIRED_KEYS = (
    "violation_reason",
    "cost_example",
    "before_code",
    "after_code",
    "learning_points",
    "revision_prompt",
)

_FENCE = re.compile(r"```(?:json)?\s*(\{.*\})\s*```", re.DOTALL)


def _extract_json(text: str) -> str:
    fenced = _FENCE.search(text)
    if fenced:
        return fenced.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("응답에서 JSON 객체를 찾지 못함")
    return text[start : end + 1]


def parse_llm_response(text: str) -> dict:
    """LLM 텍스트에서 학습 카드 콘텐츠 dict를 뽑아 검증한다."""
    try:
        data = json.loads(_extract_json(text))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON 파싱 실패: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("최상위가 JSON 객체가 아님")

    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise ValueError(f"필수 키 누락: {missing}")

    if not isinstance(data["learning_points"], list):
        raise ValueError("learning_points는 리스트여야 함")

    return data
