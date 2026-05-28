# Interfaces — 4 Track 인터페이스 명세 (Day 3 초안)

> Day 4 병렬 개발 시작 전 인터페이스 합의 (WBS Risk #1 완충).
> Python `Protocol` + `dataclass` 기반. 구현은 Day 4-7에서.

## 0. 왜 Protocol인가

`Protocol`은 duck typing + structural subtyping을 활용하므로, 모듈 간 **자료 결합**(data coupling)만 강제 가능. SW공학에서 다루는 결합도 6단계 중 가장 약한 결합 수준. 추상 클래스 상속을 강제하지 않으므로 모듈별 트랙이 독립 진행 가능한 구조.

## 1. 공용 타입

```python
from typing import Protocol, Literal
from dataclasses import dataclass
from datetime import datetime

StageName = Literal['Requirement', 'Design', 'Dev', 'Test', 'Deploy']
FPKind = Literal['EI', 'EO', 'EQ', 'ILF', 'EIF']
Complexity = Literal['low', 'avg', 'high']


@dataclass
class Event:
    """이벤트 버스 단위 — choreography 모듈이 구독."""
    session_id: str
    event_type: str  # e.g. 'DiffSubmitted', 'StageCompleted'
    payload: dict
    published_at: datetime
```

## 2. Track 1 — Stage Gate + Process Log

```python
@dataclass
class GateDecision:
    allowed: bool
    reason: str  # 사용자에게 표시될 차단 사유
    suggested_action: str | None  # 다음에 뭘 해야 하는지


class StageGate(Protocol):
    """SAGA 5단계 state machine + PreToolUse hook 진입점."""
    def check(self, current_stage: StageName, tool_name: str) -> GateDecision: ...
    def transition(self, to_stage: StageName) -> bool: ...
    def rollback(self) -> None: ...
    def force(self, reason: str) -> None:
        """사용자 명시 우회. force_overrides 테이블에 기록."""
        ...


@dataclass
class StageBreakdown:
    requirement_pct: float
    design_pct: float
    dev_pct: float
    test_pct: float
    maintenance_pct: float


class ProcessLog(Protocol):
    """Stop hook 진입점. transcript 분류 + ISO 25010 매핑."""
    def capture(self, transcript: str) -> None: ...
    def report(self) -> StageBreakdown: ...
    def iso25010_dimensions(self) -> dict[str, int]:
        """기능성·신뢰성·사용성·효율성·유지보수성·이식성·호환성·보안성·안전성 9축."""
        ...
```

## 3. Track 2 — UseCase Logger

```python
@dataclass
class UseCase:
    id: str  # UC-NNN
    actor: str
    scenario: str
    mermaid: str | None
    include_uc_ids: list[str]
    extend_uc_id: str | None


class UseCaseLogger(Protocol):
    """choreography — 사용자 직접 호출 + Stage Gate가 참조."""
    def add(self, markdown: str) -> UseCase: ...
    def list(self) -> list[UseCase]: ...
    def to_mermaid(self, uc: UseCase) -> str: ...
    def exists(self) -> bool:
        """Stage Gate가 'Design 진입 가능 여부' 판정 시 호출."""
        ...
```

## 4. Track 3 — SOLID Judge

```python
@dataclass
class SolidScore:
    srp: int  # 0-10
    ocp: int
    lsp: int
    isp: int
    dip: int
    cohesion: int  # 응집도 7단계 점수화 (가장 강한 응집 → 약한 응집)
    coupling: int  # 결합도 6단계 점수화
    reasoning: str  # LLM judge의 자연어 근거

    @property
    def total(self) -> float:
        return (self.srp + self.ocp + self.lsp + self.isp + self.dip) / 5


class SolidJudge(Protocol):
    """choreography — DiffSubmitted 이벤트 구독."""
    def judge(self, diff: str, context: dict | None = None) -> SolidScore: ...
    def needs_retry(self, score: SolidScore, threshold: int = 7) -> bool: ...
    def request_revision(self, score: SolidScore) -> str:
        """AI agent에게 다시 보낼 수정 프롬프트 생성."""
        ...
```

## 5. Track 4 — FP Counter → EV Tracker

```python
@dataclass
class FPItem:
    kind: FPKind
    complexity: Complexity
    weight: float  # IFPUG 표준 가중치 표 참조 (docs/METRICS.md Section 1.2)


class FPCounter(Protocol):
    def add(self, kind: FPKind, complexity: Complexity) -> FPItem: ...
    def total(self) -> float: ...
    def by_kind(self) -> dict[FPKind, float]: ...


@dataclass
class EVSnapshot:
    pv: float  # planned value (%)
    ev: float  # earned value (%)
    ac: float  # actual cost (hours)
    spi: float  # EV / PV
    cpi: float  # EV / AC (정규화 후)
    fp_total: float | None  # FP Counter 연동 시


class EVTracker(Protocol):
    """choreography — StageCompleted 이벤트 구독 + FP Counter polling."""
    def measure(self) -> EVSnapshot: ...
    def update_from_commits(self, repo_path: str) -> None: ...
    def include_fp(self, fp_total: float) -> None: ...
```

## 6. 이벤트 타입 명세

| 이벤트 | 발행 모듈 | 구독 모듈 | payload |
|---|---|---|---|
| `RequirementCreated` | UseCase Logger / req add CLI | Stage Gate | `{req_id, kind, ...}` |
| `EditAttempted` | Stage Gate (PreToolUse hook) | Process Log | `{tool_name, file, blocked}` |
| `DiffSubmitted` | (외부) Claude Code | SOLID Judge | `{diff, file_paths}` |
| `StageCompleted` | Stage Gate | EV Tracker, Process Log | `{stage_name, completed_at}` |
| `ForceOverride` | Stage Gate.force() | EV Tracker, Process Log | `{stage, reason, forced_at}` |

## 7. 모듈 간 의존성 검증

병렬 개발 후 Day 6 저녁 1차 통합 시 검증할 의존성:

```
Stage Gate    →  UseCase Logger.exists()   (Design 진입 invariant)
Stage Gate    →  events 발행
SOLID Judge   →  events 구독 (DiffSubmitted)
EV Tracker    →  events 구독 (StageCompleted)
EV Tracker    →  FP Counter.total()
Process Log   →  events 구독 (모든)
```

각 트랙은 위 6 인터페이스만 stub으로 구현해두면 통합 가능. 실제 동작은 본 모듈 완성 후.

## 8. 설계 메모

`Protocol`을 채택한 이유는 결합도 최소화 원칙 적용 + 병렬 개발 시 인터페이스 합의 문서를 코드 형태로 남겨두기 위함. 4 트랙이 동시 진행되어도 Protocol contract만 지키면 통합 단계에서 깨질 가능성이 작은 구조.

다만 Protocol은 컴파일 타임 검증만 가능. 런타임 동작 보장은 통합 테스트 단계에서 진행. `mypy --strict` 또는 `pyright`로 contract 위반 자동 탐지 예정.

단위 테스트는 `pytest` 사용. 각 모듈은 기본 4종 케이스 커버:
- 정상 입력 시 expected 출력 (`assert ==`)
- 잘못된 입력(음수·범위 외 등) 시 예외 발생 (`pytest.raises`)
- 존재하지 않는 항목 조회·삭제 시 `None` 또는 정의된 예외
- 중복 추가 시 예외 처리

자동 생성된 테스트 코드는 그대로 채택하지 않고 사람이 한 번 검수 후 채택. 테스트 케이스 자체의 타당성도 V&V 영역.

ARCHITECTURE.md의 SQLite 스키마와 본 인터페이스는 명시적 매핑 관계 (예: `Event` dataclass ↔ `events` 테이블). 이 매핑이 깨지면 1차 통합 PoC 시점에 발견되는 구조.
