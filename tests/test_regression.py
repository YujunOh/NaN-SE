"""회귀 테스트.

한 번 잡은 버그가 되살아나지 않게 기대값을 고정한다.
god class가 생성자(__init__) 때문에 LCOM4=1로 위장되던 버그(REPORT 4.3)를
가드한다. dunder를 계산에서 빼므로 AuthService는 책임 3개(=3)로 갈라져야 한다.
값이 1로 돌아오면 그 버그가 재발한 것이다.
"""

from pathlib import Path

from nanse.metrics import analyze_source

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "auth_service.py"


def test_god_class_lcom4_stays_split() -> None:
    results = {r.class_name: r.lcom4 for r in analyze_source(EXAMPLE.read_text(encoding="utf-8"))}
    assert results["AuthService"] == 3  # dunder 제외 → 1로 위장되지 않는다
    assert results["Counter"] == 1  # 응집 클래스는 한 덩어리
