"""스모크 테스트.

새 빌드가 "최소한 켜지고 핵심 기능이 도나"를 빠르게 1차 점검한다.
배포된 예시 파일(examples/auth_service.py)에 검출 파이프라인을 끝까지 돌려,
SRP 위반 finding이 실제로 뜨는지만 본다. 상세 단위 검증은 test_lcom.py가 맡는다.
"""

from pathlib import Path

from nanse.metrics import analyze_source
from nanse.metrics.findings import findings_from_cohesion
from nanse.principles import Principle

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "auth_service.py"


def test_analyze_example_produces_srp_finding() -> None:
    results = analyze_source(EXAMPLE.read_text(encoding="utf-8"))
    findings = findings_from_cohesion(results, source_file=str(EXAMPLE))

    classes = {r.class_name for r in results}
    assert {"AuthService", "Counter"} <= classes  # 파이프라인이 전체 클래스를 본다

    srp = [f for f in findings if f.principle is Principle.SRP]
    flagged = {f.class_name for f in srp}
    assert "AuthService" in flagged  # god class가 검출된다
    assert "Counter" not in flagged  # 응집 클래스는 안 걸린다
