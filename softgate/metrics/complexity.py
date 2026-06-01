"""순환복잡도 검출. radon을 통합한다(McCabe를 재발명하지 않는다).

복잡도가 높은 메서드는 분기(주로 타입·상태 조건)가 한 곳에 몰린 신호다.
새 경우를 추가할 때마다 그 메서드를 다시 열어 고쳐야 하므로 OCP(확장에는
열리고 변경에는 닫힌다) 렌즈로 본다. 임계값은 McCabe 권고를 따라 10.
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
    line: int = 1


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
                    line=getattr(block, "lineno", 1),
                )
            )
    return results


def _severity(complexity: int) -> int:
    over = complexity - CYCLOMATIC_THRESHOLD
    return min(10, max(1, over))


def findings_from_complexity(
    source: str, source_file: str | None = None
) -> list[MetricFinding]:
    """임계값을 넘은 함수/메서드를 OCP finding으로 변환."""
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
                    principle=Principle.OCP,
                    severity=_severity(fc.complexity),
                    source_file=source_file,
                    source_line=fc.line,
                )
            )
    return findings
