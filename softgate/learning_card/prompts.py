"""학습 카드 LLM 프롬프트 템플릿. 본인 자산.

검출은 이미 결정적으로 끝났으므로 프롬프트는 채점을 시키지 않는다.
"왜 위반이고 어떻게 고치는지"를 설명만 시킨다.
"""

from __future__ import annotations

from softgate.metrics.findings import MetricFinding

LEARNING_CARD_PROMPT = """당신은 SW공학 원칙을 가르치는 학습 도우미입니다.
아래는 정적 분석으로 이미 확정된 위반 사실입니다. 채점은 끝났으니 다시 점수를
매기지 말고, 왜 문제인지와 고치는 법만 학습 카드로 설명하세요.

## 확정된 위반 (결정적 메트릭)
- 클래스: {class_name}
- 원칙: {principle}
- 지표: {metric} = {value} (임계값 {threshold})
- 심각도: {severity}/10

## 대상 코드
```python
{code}
```

## 출력 형식 (JSON만, 다른 텍스트 없음)
{{
  "violation_reason": "왜 이게 위반인지 3-5줄 자연어 설명",
  "cost_example": "이 위반이 운영 단계에서 어떤 비용으로 돌아오는지 구체 예시 1개",
  "before_code": "위반 코드 스니펫 (원본에서 발췌)",
  "after_code": "리팩토링 후 코드 스니펫",
  "learning_points": ["bullet 1", "bullet 2", "bullet 3"],
  "revision_prompt": "AI coding agent에 다시 보낼 수정 지시 (구체적 리팩토링 가이드)"
}}

## 톤
- 자연어 한국어
- 짧고 직설적
- 학습자가 이해하기 쉽게
- 추측이 아닌 코드 사실에 기반"""


def build_prompt(finding: MetricFinding, code: str) -> str:
    return LEARNING_CARD_PROMPT.format(
        class_name=finding.class_name,
        principle=finding.principle.value,
        metric=finding.metric,
        value=finding.value,
        threshold=finding.threshold,
        severity=finding.severity,
        code=code,
    )
