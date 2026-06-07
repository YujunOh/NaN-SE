# Interfaces — NaN-SE

> 구현 단계 진입 전에 작성한 Protocol/dataclass 인터페이스 명세다(통합 risk 완충용).
>
> **구현 범위**: 이 중 실제 코드로 구현한 것은 2절의 Metric Analyzer(검출)와 Learning Card(설명)뿐이고, 실제 시그니처는 `nanse/metrics/`·`nanse/learning_card/`에 있다(아래 명세와 세부가 다를 수 있다. 예: 구현 검출은 lcom4→SRP, cyclomatic→OCP 두 매핑만 쓰고 cbo·wmc·param_max는 계산하지 않는다. `send_revision_to_agent`는 구현하지 않았다). 3~6절(Stage, Traceability, Progress Dashboard, EV/FP/Process Log)과 Event 버스는 피벗 때 접은 설계이고 코드가 없다. 이 문서는 설계 사고 기록으로 읽는다.

## 0. 왜 Protocol인가

`Protocol`은 duck typing + structural subtyping을 활용하므로, 모듈 간 **자료 결합**(data coupling)만 강제 가능. SW공학에서 다루는 결합도 6단계 중 가장 약한 결합 수준. 추상 클래스 상속을 강제하지 않으므로 모듈별 트랙이 독립 진행 가능한 구조.

## 1. 공용 타입

```python
from typing import Protocol, Literal
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel
from enum import Enum

StageName = Literal['Requirement', 'Design', 'Dev', 'Test', 'Deploy']
FPKind = Literal['EI', 'EO', 'EQ', 'ILF', 'EIF']
Complexity = Literal['low', 'avg', 'high']

class Principle(str, Enum):
    SRP = "Single Responsibility"
    OCP = "Open-Closed"
    LSP = "Liskov Substitution"
    ISP = "Interface Segregation"
    DIP = "Dependency Inversion"
    HIGH_COHESION = "High Cohesion"
    LOW_COUPLING = "Low Coupling"


@dataclass
class Event:
    """이벤트 버스 단위 — choreography 모듈이 구독."""
    session_id: str
    event_type: str  # e.g. 'CommitMade', 'CardJudged', 'StageCompleted'
    payload: dict
    published_at: datetime
```

## 2. 핵심 1 — Metric Analyzer (검출) + Learning Card Generator (설명)

> Day 5 결정으로 검출과 설명을 분리했다. 검출은 결정적 정적 분석이라 LLM을
> 호출하지 않고 같은 입력에 같은 출력을 낸다. LLM은 설명(학습 카드)만 채운다.
> 이유는 DISCUSSION_LOG 2026-05-31 참조.

```python
@dataclass
class ClassMetrics:
    """한 클래스의 결정적 메트릭. 같은 소스에 항상 같은 값."""
    class_name: str
    lcom4: int           # 응집도 결손, 연결 요소 수. 1이 이상적
    cbo: int             # 결합도 (Coupling Between Objects)
    wmc: int             # 가중 메서드 수
    cyclomatic_max: int  # 메서드별 순환복잡도 최댓값
    method_count: int
    param_max: int       # 메서드 매개변수 개수 최댓값


@dataclass
class MetricFinding:
    """임계값을 넘은 메트릭 하나. SOLID 원칙에 매핑된다."""
    class_name: str
    metric: str          # 'lcom4', 'cbo', 'cyclomatic', ...
    value: float
    threshold: float
    principle: Principle  # lcom4->SRP, cbo->LOW_COUPLING, ...
    severity: int        # 0-10, 임계값 초과 정도


class MetricAnalyzer(Protocol):
    """결정적 검출층. LLM 호출 없음. Stage가 Edit/commit 시점에 호출.

    LCOM4는 직접 구현(nanse/metrics/lcom.py), 순환복잡도 등은 radon 통합.
    """
    def analyze(self, source: str) -> list[ClassMetrics]: ...
    def findings(self, metrics: list[ClassMetrics]) -> list[MetricFinding]:
        """임계값 초과 항목만 골라 SOLID 원칙에 매핑."""
        ...
```

SOLID별 결정적 검출 가능성은 다르다. SRP·DIP·결합도·응집도는 메트릭 proxy가
탄탄하고, OCP·ISP는 부분, LSP는 본질적으로 기계화 불가다. LSP/OCP의 모호한
부분은 검출하지 않고 사람 판단에 맡긴다. 즉 MetricFinding은 자신 있는 위반만
올린다.

```python
# 학습 카드 시스템 — 자세한 명세는 LEARNING_CARDS.md
class LearningCard(BaseModel):
    id: str  # CARD-001
    session_id: str
    finding_id: int  # MetricFinding 식별자
    principle: Principle
    severity: int    # MetricFinding.severity 복사 (0-10)
    code_hash: str

    # LLM이 채우는 콘텐츠 (자연어 설명만, 점수 매기기 아님)
    violation_reason: str
    cost_example: str
    before_code: str
    after_code: str
    learning_points: list[str]
    revision_prompt: str

    # 본인이 짠 검수 로직
    user_accepted: bool | None
    user_feedback: str | None

    generated_at: datetime
    reviewed_at: datetime | None


class LearningCardGenerator(Protocol):
    """MetricAnalyzer가 finding을 올리면 호출. 학습 카드 자동 생성.

    LLM은 자연어 콘텐츠만 채운다. 메트릭 값과 위반 판정은 이미 결정적으로 끝났다.
    """
    def generate(self, finding: MetricFinding, code: str) -> LearningCard: ...
    def review(self, card_id: str, accepted: bool, feedback: str | None = None) -> None: ...
    def get_unreviewed(self) -> list[LearningCard]: ...
    def send_revision_to_agent(self, card_id: str) -> bool:
        """채택된 카드의 재요청 prompt를 AI agent에 전송."""
        ...
```

## 3. Stage (누락 검출 + 자동 제안) — 설계만, 코드 없음

```python
@dataclass
class StageStatus:
    current_stage: StageName
    missing_artifacts: list[str]  # 예: ["REQ-005", "tests/test_payment.py"]
    suggestions: list[str]        # 자동 제안 메시지


class Stage(Protocol):
    """SDLC 5단계 state machine + PreToolUse hook 진입점. 차단하지 않고 제안만 한다."""
    def current_status(self) -> StageStatus: ...
    def detect_missing(self, action: str, context: dict) -> list[str]:
        """AI agent의 action에 대해 누락된 산출물 목록 반환."""
        ...
    def suggest(self, missing: list[str]) -> list[str]:
        """누락 항목에 대한 자동 제안 메시지 생성."""
        ...
    def transition(self, to_stage: StageName) -> bool: ...
```

## 4. Traceability (요구 추적) — 부분 구현 (존재 검증은 `nanse/traceability.py`, 나머지는 설계만)

```python
@dataclass
class TraceabilityRow:
    req_id: str | None
    uc_id: str | None
    code_path: str | None
    test_path: str | None
    gap_type: Literal['no_uc', 'no_code', 'no_test', 'complete']


@dataclass
class UseCase:
    id: str  # UC-NNN
    req_ids: list[str]
    actor: str
    scenario: str
    mermaid: str | None
    include_uc_ids: list[str]
    extend_uc_id: str | None


class Traceability(Protocol):
    """commit message 태그 매칭으로 자동 갱신."""
    def add_requirement(self, req_id: str, title: str, ac: list[str]) -> None: ...
    def add_usecase(self, markdown: str) -> UseCase: ...
    def parse_commit_tags(self, message: str) -> dict:
        """commit message에서 [REQ-001][UC-001] 태그 추출."""
        ...
    def matrix(self) -> list[TraceabilityRow]: ...
    def gaps(self) -> list[TraceabilityRow]:
        """gap_type != 'complete'인 행만 반환."""
        ...
    def export_matrix(self) -> str:
        """traceability 매트릭스를 markdown으로 export."""
        ...
```

## 5. Progress Dashboard — 설계만 (웹 대시보드가 일부 대체)

```python
@dataclass
class DashboardSnapshot:
    cards_total: int
    cards_accepted: int
    cards_rejected: int
    acceptance_rate: float
    solid_pass_rate_7d: float
    solid_pass_rate_30d: float
    streak_days: int
    principle_distribution: dict[Principle, int]  # 위반 빈도 분포
    measured_at: datetime


class ProgressDashboard(Protocol):
    """CardJudged 이벤트 구독 + 비동기 집계."""
    def snapshot(self) -> DashboardSnapshot: ...
    def streak(self) -> int:
        """연속 사용 일수 (학습 카드 검수 활동 기준)."""
        ...
    def render_cli(self) -> str:
        """rich library로 CLI 패널 렌더링."""
        ...
    def render_html(self) -> str:
        """간단한 HTML 출력 (선택)."""
        ...
```

## 6. 옵션 모듈 — EV / FP / Process Log — 설계만, 코드 없음

```python
# 옵션 1 — FP Counter
@dataclass
class FPItem:
    kind: FPKind
    complexity: Complexity
    weight: float  # IFPUG 표준 가중치 표 참조 (METRICS.md Section 1.2)


class FPCounter(Protocol):
    def add(self, kind: FPKind, complexity: Complexity) -> FPItem: ...
    def total(self) -> float: ...
    def by_kind(self) -> dict[FPKind, float]: ...


# 옵션 2 — EV Tracker
@dataclass
class EVSnapshot:
    pv: float
    ev: float
    ac: float
    spi: float
    cpi: float
    fp_total: float | None


class EVTracker(Protocol):
    def measure(self) -> EVSnapshot: ...
    def update_from_commits(self, repo_path: str) -> None: ...
    def include_fp(self, fp_total: float) -> None: ...


# 옵션 3 — Process Log
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
    def iso25010_dimensions(self) -> dict[str, int]: ...
```

## 7. 이벤트 타입 명세

| 이벤트 | 발행 모듈 | 구독 모듈 | payload |
|---|---|---|---|
| `RequirementCreated` | Traceability / req add CLI | Stage | `{req_id, kind, ...}` |
| `EditAttempted` | Stage (PreToolUse hook) | Process Log (옵션) | `{tool_name, file}` |
| `DiffSubmitted` | (외부) Claude Code | Metric Analyzer | `{diff, file_paths}` |
| `MetricFound` | Metric Analyzer | Progress Dashboard | `{finding_id, metric, value}` |
| `CardGenerated` | LearningCardGenerator | Progress Dashboard | `{card_id, principle}` |
| `CardJudged` | LearningCardGenerator | Progress Dashboard | `{card_id, accepted, feedback}` |
| `CommitMade` | (외부) git | Traceability | `{commit_hash, message, files}` |
| `StageCompleted` | Stage | EV Tracker (옵션), Process Log (옵션) | `{stage_name, completed_at}` |

## 8. 모듈 간 의존성 검증

1차 통합 시 검증할 의존성.

```
Stage           →  MetricAnalyzer.analyze()         (Edit hook 시점)
MetricAnalyzer  →  LearningCardGenerator.generate()  (finding 발생 시)
LearningCard    →  Hook (UserPromptSubmit)     (채택된 재요청 prompt 전송)
Traceability    →  events 구독 (CommitMade)
Progress Dash   →  events 구독 (CardJudged, CardGenerated, MetricFound)
EV Tracker     →  events 구독 (StageCompleted) + FP Counter.total()
Process Log    →  events 구독 (모든)
```

각 트랙은 위 인터페이스만 stub으로 구현해두면 통합 가능. 실제 동작은 모듈 완성 후.

## 9. 설계 메모

`Protocol`을 채택한 이유는 결합도 최소화 원칙 적용 + 병렬 개발 시 인터페이스 합의 문서를 코드 형태로 남겨두기 위함. 4 트랙이 동시 진행되어도 Protocol contract만 지키면 통합 단계에서 깨질 가능성이 작은 구조.

다만 Protocol은 컴파일 타임 검증만 가능. 런타임 동작 보장은 통합 테스트 단계에서 진행. `mypy --strict` 또는 `pyright`로 contract 위반 자동 탐지 예정.

단위 테스트는 `pytest` 사용. 각 모듈은 기본 4종 케이스 커버:
- 정상 입력 시 expected 출력 (`assert ==`)
- 잘못된 입력(음수·범위 외 등) 시 예외 발생 (`pytest.raises`)
- 존재하지 않는 항목 조회·삭제 시 `None` 또는 정의된 예외
- 중복 추가 시 예외 처리

자동 생성된 테스트 코드는 그대로 채택하지 않고 사람이 한 번 검수 후 채택. 테스트 케이스 자체의 타당성도 V&V 영역.

ARCHITECTURE.md의 SQLite 스키마와 본 인터페이스는 명시적 매핑 관계 (예: `LearningCard` ↔ `learning_cards` 테이블, `Event` ↔ `events` 테이블). 이 매핑이 깨지면 1차 통합 PoC 시점에 발견되는 구조.
