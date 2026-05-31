"""메트릭 값을 임계값과 비교해 SOLID 위반 finding으로 바꾸는 층.

여기까지가 결정적 영역이다. LLM은 호출하지 않는다. finding이 만들어진 뒤에야
학습 카드 생성(설명, LLM)이 트리거된다.
"""

from __future__ import annotations

from dataclasses import dataclass

from softgate.metrics.lcom import ClassCohesion
from softgate.principles import Principle

# 임계값. 벤치마크 기반 도출이 원칙이나 초기값은 교과서 기준.
# LCOM4는 1이 이상적이고 2 이상이면 클래스가 무관한 책임으로 갈라진 신호.
LCOM4_THRESHOLD = 1


@dataclass
class MetricFinding:
    """임계값을 넘은 메트릭 하나. SOLID 원칙에 매핑된다."""

    class_name: str
    metric: str
    value: float
    threshold: float
    principle: Principle
    severity: int  # 0-10, 클수록 심각


def _lcom4_severity(lcom4: int) -> int:
    """LCOM4 초과 정도를 0-10 심각도로 환산. 컴포넌트가 많을수록 심각."""
    over = lcom4 - LCOM4_THRESHOLD
    return min(10, over * 3)


def findings_from_cohesion(results: list[ClassCohesion]) -> list[MetricFinding]:
    """LCOM4 결과 중 임계값 초과 클래스를 SRP 위반 finding으로 변환."""
    findings: list[MetricFinding] = []
    for r in results:
        if r.lcom4 > LCOM4_THRESHOLD:
            findings.append(
                MetricFinding(
                    class_name=r.class_name,
                    metric="lcom4",
                    value=float(r.lcom4),
                    threshold=float(LCOM4_THRESHOLD),
                    principle=Principle.SRP,
                    severity=_lcom4_severity(r.lcom4),
                )
            )
    return findings
