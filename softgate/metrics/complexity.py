"""순환복잡도 검출. radon을 통합한다(McCabe를 재발명하지 않는다).

복잡도가 높은 메서드는 한 곳에서 너무 많은 일을 한다는 신호이고,
메서드 수준의 SRP 위반으로 본다. 임계값은 McCabe 권고를 따라 10.
"""

from __future__ import annotations

from dataclasses import dataclass

from radon.complexity import cc_visit

from softgate.metrics.findings import MetricFinding
from softgate.principles import Principle

CYCLOMATIC_THRESHOLD = 10


@dataclass
class FunctionComplexity:
    name: str
    classname: str | None
    complexity: int


def analyze_complexity(source: str) -> list[FunctionComplexity]:
    """소스 안 모든 함수/메서드의 순환복잡도를 낸다. 같은 입력에 같은 값."""
    results: list[FunctionComplexity] = []
    for block in cc_visit(source):
        # radon letter: 'F'=함수, 'M'=메서드, 'C'=클래스 집계. 집계는 제외.
        if getattr(block, "letter", "F") in ("F", "M"):
            results.append(
                FunctionComplexity(
                    name=block.name,
                    classname=getattr(block, "classname", None),
                    complexity=block.complexity,
                )
            )
    return results


def _severity(complexity: int) -> int:
    over = complexity - CYCLOMATIC_THRESHOLD
    return min(10, max(1, over))


def findings_from_complexity(source: str) -> list[MetricFinding]:
    """임계값을 넘은 함수/메서드를 SRP finding으로 변환."""
    findings: list[MetricFinding] = []
    for fc in analyze_complexity(source):
        if fc.complexity > CYCLOMATIC_THRESHOLD:
            label = f"{fc.classname}.{fc.name}" if fc.classname else fc.name
            findings.append(
                MetricFinding(
                    class_name=label,
                    metric="cyclomatic",
                    value=float(fc.complexity),
                    threshold=float(CYCLOMATIC_THRESHOLD),
                    principle=Principle.SRP,
                    severity=_severity(fc.complexity),
                )
            )
    return findings
