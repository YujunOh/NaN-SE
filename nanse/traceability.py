"""요구 추적(Traceability) 최소 구현.

UC(유스케이스) ↔ 코드 ↔ 테스트의 매핑 명세를 받아, 각 항목의 코드/테스트
파일이 실제로 존재하는지 확인하고 gap을 분류한다. 결정적이라 같은 저장소에
같은 결과가 나오고, LLM을 쓰지 않는다.

전체 설계(commit 태그 자동 갱신, Mermaid export)는 ARCHITECTURE/INTERFACES에
남긴 구상이고, 여기서는 "존재 검증 매트릭스 + gap 탐지"까지만 구현한다.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

# 명세 파일이 없을 때 쓰는 기본 매핑. 실제 NaN-SE의 구현된 유스케이스만 담는다.
DEFAULT_SPEC: dict[str, dict] = {
    "UC-03": {
        "req": "REQ-01",
        "title": "위반의 결정론적 검출",
        "code": [
            "nanse/metrics/lcom.py",
            "nanse/metrics/complexity.py",
            "nanse/metrics/findings.py",
        ],
        "test": ["tests/test_lcom.py", "tests/test_complexity.py"],
    },
    "UC-04": {
        "req": "REQ-02",
        "title": "학습 카드 생성",
        "code": [
            "nanse/learning_card/generator.py",
            "nanse/learning_card/models.py",
            "nanse/learning_card/parser.py",
            "nanse/learning_card/prompts.py",
        ],
        "test": ["tests/test_learning_card.py"],
    },
    "UC-05": {
        "req": "REQ-03",
        "title": "학습 카드 검수·저장",
        "code": ["nanse/db/store.py", "nanse/cli/__init__.py"],
        "test": ["tests/test_store.py"],
    },
    "UC-trace": {
        "req": "REQ-04",
        "title": "요구↔코드↔테스트 존재 검증",
        "code": ["nanse/traceability.py"],
        "test": ["tests/test_traceability.py"],
    },
}


@dataclass
class TraceRow:
    """한 요구(UC)의 추적 결과."""

    req_id: str
    title: str
    req: str = ""
    code_present: list[str] = field(default_factory=list)
    code_missing: list[str] = field(default_factory=list)
    test_present: list[str] = field(default_factory=list)
    test_missing: list[str] = field(default_factory=list)
    gap: str = "complete"  # 'complete' | 'no_code' | 'no_test'

    @property
    def code_total(self) -> int:
        return len(self.code_present) + len(self.code_missing)

    @property
    def test_total(self) -> int:
        return len(self.test_present) + len(self.test_missing)


def load_spec(path: Path | None) -> dict[str, dict]:
    """TOML 명세를 읽는다. 없으면 기본 매핑을 쓴다.

    TOML 형식 예:
        [UC-03]
        title = "위반의 결정론적 검출"
        code = ["nanse/metrics/lcom.py"]
        test = ["tests/test_lcom.py"]
    """
    if path and path.exists():
        return tomllib.loads(path.read_text(encoding="utf-8"))
    return DEFAULT_SPEC


def build_matrix(spec: dict[str, dict], root: Path) -> list[TraceRow]:
    """명세와 저장소 루트를 받아 추적 매트릭스를 만든다.

    gap 분류: 코드가 하나도 없으면 no_code, 코드는 있는데 테스트가 하나도
    없으면 no_test, 둘 다 있으면 complete.
    """
    rows: list[TraceRow] = []
    for req_id, entry in spec.items():
        code = list(entry.get("code", []))
        test = list(entry.get("test", []))
        code_present = [p for p in code if (root / p).exists()]
        code_missing = [p for p in code if not (root / p).exists()]
        test_present = [p for p in test if (root / p).exists()]
        test_missing = [p for p in test if not (root / p).exists()]

        if not code_present:
            gap = "no_code"
        elif not test_present:
            gap = "no_test"
        else:
            gap = "complete"

        rows.append(
            TraceRow(
                req_id=req_id,
                title=entry.get("title", ""),
                req=entry.get("req", ""),
                code_present=code_present,
                code_missing=code_missing,
                test_present=test_present,
                test_missing=test_missing,
                gap=gap,
            )
        )
    return rows


def gaps_only(rows: list[TraceRow]) -> list[TraceRow]:
    return [r for r in rows if r.gap != "complete"]
