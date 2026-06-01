# softgate

> **바이브코딩 시대의 TCP** — unreliable AI coding 위에 SW공학 reliability를 얹는 부드러운 게이트
>
> 차단하지 않는다. 검출하고, 학습 카드로 전환하고, 다시 AI agent에 보낼 prompt까지 자동 생성한다. Claude Code, Cursor, opencode 같은 agent가 *무엇을 만들지* 결정한다면, softgate는 *그 결정과 결과물이 SW공학 원칙을 따르는지* 검증하고 *왜 그래야 하는지*를 사용자에게 자연스럽게 학습시킨다.

전체 비전·배경·로드맵은 [docs/VISION.md](./docs/VISION.md)

## 한 줄 정의

AI coding agent가 만든 산출물(요구·설계·코드·테스트)의 SW공학 위반을 자동 검출하고, 위반 자체를 학습 카드로 전환해 사용자가 SW공학 원칙을 자연스럽게 익히게 만드는 부드러운 게이트

## 왜 지금 필요한가 — "AI 스파게티"와 "공장 컨베이어벨트"

바이브코딩은 트렌드를 넘어 개발의 기본 모드가 되었지만, 같은 기간 소프트웨어 품질은 다음 두 가지 비유로 표현될 정도로 전락한 상태.

- **"AI 스파게티"** — 기능은 동작하지만 50명 개발자가 서로 한 번도 만나본 적 없이 짠 것 같은 코드베이스. 매 커밋마다 기술부채가 쌓이고, 평소엔 멀쩡하다 어느 순간 catastrophically fails
- **"공장 컨베이어벨트"** — 손길이 거의 닿지 않은 채 라인 끝에서 쏟아져나오는 양산형 제품. 빠르고 많이 나오지만, 출하 전 검수가 빠지면 reject·재작업 비용으로 돌아옴

CodeRabbit 조사(2025)는 AI 생성 코드의 정량적 차이를 보여준다. 버그 1.7배, 보안 취약성 2배, 논리 오류 75%. industry analyst는 2027년까지 AI 생성 코드에서 누적 약 $1.5T 기술부채를 예측. 단순한 도구 사용 미숙이 아닌, 새로운 형태의 소프트웨어 위기.

자세한 배경·통계·비전은 [docs/VISION.md](./docs/VISION.md)

## 문제 정의

AI coding agent를 쓰는 개발 흐름의 흔한 패턴은 이렇다.

```
자연어 지시
  → AI가 요구사항을 자기 마음대로 해석
  → 설계 단계 건너뛰고 곧장 구현
  → 테스트는 형식적으로 같이 생성
  → 문서는 누락
  → 변경 영향 분석 없음
  → 코드가 돌아가면 종료
```

겉으로는 빠르게 끝난 것 같지만, 실제로는 다음이 누적된다.

- **토큰 낭비** — AI가 추측성 기능·미래 대비 추상화를 만들면 사용자가 다시 지우는 데 또 토큰을 쓴다. 같은 작업을 두 번 결제한 셈
- **시간 낭비** — 빨리 끝난 줄 알았던 작업이 며칠 뒤 디버깅 비용으로 돌아온다. "AI 코드 디버깅이 직접 코딩보다 오래 걸렸다"는 응답이 개발자 45%대 (Stack Overflow Survey 2025)
- **자원 낭비** — 어차피 해야 할 작업(요구 정리·설계·테스트·문서)이 뒤로 미뤄지며 기술부채가 누적된다. 사람이 손 안 댄 단계들이 쌓이면 다른 사람이 손 댈 수도 없는 상태로 변한다
- **검증 누락** — 코드가 돌아가는 것과 요구를 만족하는 것은 다른 문제다. V&V를 한 번도 거치지 않은 산출물이 그대로 main에 들어가는 일이 일상화된다
- **버그·보안 결함의 정량 차이** — CodeRabbit 조사(2025) 기준 AI 생성 코드는 직접 작성 대비 버그 1.7배, 보안 취약성 2배로 검출됨. 논리 오류율은 75% 수준. "코드가 돌아간다"와 "안전하게 쓸 수 있다"는 다른 문제이고, 그 차이를 직접 검증하지 않으면 운영 단계에서 비용으로 돌아온다

기존 도구들(SonarQube, Helicone, LangSmith 등)은 코드 작성 이후의 정적 분석이나 LLM 비용 추적에 집중되어 있고, AI가 코드를 만드는 과정 자체에 SW공학 절차를 끼워넣는 도구는 빈자리로 남아있다.

softgate는 이 빈자리에 들어가는 미들웨어다. AI coding agent를 대체하는 도구가 아니라, agent가 만든 산출물의 SRP·응집도 위반을 결정론적 정적 메트릭(LCOM4·순환복잡도)으로 검출하고, 확정된 위반을 LLM이 학습 카드로 설명해 사용자가 검수하게 한다. 검출과 설명을 분리한 게 핵심이다. 채점은 LLM에 맡기지 않는다.

## 핵심 아이디어

긴 트랜잭션을 잘게 잘라 독립적으로 수행한다는 SAGA 패턴을 SDLC에 적용한다. 5단계(요구 → 설계 → 구현 → 테스트 → 배포)를 각각 트랜잭션으로 보고, 단계별 invariant(진입 조건)를 만족해야 다음으로 진행한다. 실패 시 이전 단계로 보상 트랜잭션(rollback) 수행.

분산 시스템 영역에서는 SAGA(1987), choreography vs orchestration, constraint-driven design, idempotency 같은 정합성 보장 기법이 오래 전부터 정립되어 있다. 최근의 AI agent 협업에서 드러나는 문제(상태 일관성·산출물 충돌·중복 작업·잘못된 의사결정 전파)는 새로운 카테고리의 문제가 아니라, 그 옛 패턴들이 다시 등장하는 형태에 가깝다. softgate는 새로운 개념을 발명하기보다, 이미 검증된 분산 시스템 패턴을 AI coding agent 도메인에 가져온 응용 레이어로 위치한다.

## 모듈과 구현 범위

Day 5 피벗으로 실제 구현은 검출과 설명 두 모듈에 집중한다. 나머지는 얇은 데모이거나 보고서 설계 언급이다.

### 구현

| 모듈 | 역할 |
|---|---|
| **Metric Analyzer** (구현) | AI 생성 코드를 결정론적 정적 메트릭으로 검출. LCOM4 직접 구현으로 SRP·응집도 위반을, radon으로 순환복잡도를 검출. LLM을 쓰지 않아 동일 코드는 항상 동일 결과 |
| **Learning Card** (구현) | 확정된 위반을 LLM이 학습 카드로 설명 (위반 이유·운영 단계 비용 예시·Before/After 코드·재요청 prompt). 점수는 매기지 않고 설명만. 사용자 검수 후 AI에 다시 전달하는 폐쇄 루프 |

### 얇은 데모 / 보고서 설계만

| 모듈 | 범위 |
|---|---|
| Stage | 얇은 데모. SDLC 5단계 누락 검출 + 제안, 차단하지 않음 |
| Traceability | 얇은 데모. REQ ↔ UC ↔ code ↔ test 매핑 |
| EV Tracker / FP Counter / Process Log | 보고서 설계만. EV(PMBOK)·FP(IFPUG)·ISO 25010 매핑 |

## 기존 도구와의 위치

| 도구 | 무대 | softgate와의 관계 |
|---|---|---|
| Claude Code, GPT (OpenAI), Cursor, Gemini, 자체 LLM | AI coding agent 실행 | softgate가 hook으로 위에 올라가는 구조 |
| LangChain, LangGraph, 자체 에이전트 프레임워크 | 에이전트 실행 인프라 | softgate는 그 위의 정책 레이어 |
| SonarQube, ESLint, radon | 정적 분석·메트릭 검출 | 검출 자체는 겹친다. softgate의 차별점은 검출 뒤 LLM 학습 카드·검수·AI 재요청까지 잇는 폐루프 |
| LangSmith, Helicone | LLM 비용·레이턴시 observability | 측정 대상이 다름. softgate는 SW공학 절차 준수 |

softgate는 하나의 벤더(Claude, GPT, Gemini, 자체 LLM)에 종속되지 않는다. hook 인터페이스만 표준화되면 다른 벤더로도 어댑터를 통해 확장 가능한 구조다.

자세한 비교는 [docs/COMPETITIVE.md](./docs/COMPETITIVE.md)

## 핵심 정책 — 검수는 사람이 한다

검증(Verification)과 확인(Validation)은 결국 사람이 한다는 점이 핵심. 검출은 결정론적이지만 위반을 고칠지, 학습 카드의 교정 예시를 받아들일지는 사용자가 정한다.

- Metric Analyzer가 위반을 검출해도 고칠지는 사용자 판단
- 학습 카드는 LLM이 생성한 설명이므로 사용자가 검수·채택. 거절 사유는 다음 카드 생성 시 prompt 개선에 반영
- Stage는 차단하지 않고 검출·제안만. 우회 명령 불필요
- Traceability 매트릭스 자동 매핑 결과를 사용자가 한 번 확인 후 채택

자세한 정책은 [docs/AI_TOOLING.md](./docs/AI_TOOLING.md), [docs/REQUIREMENTS.md](./docs/REQUIREMENTS.md)

## 기술 스택

- Python 3.11+
- radon (순환복잡도), 자체 구현 LCOM4 (검출)
- Anthropic SDK (학습 카드 설명 생성, Haiku)
- Claude Code Hooks: `PreToolUse`, `Stop`, `UserPromptSubmit`
- SQLite (finding·학습 카드·검수 상태)
- CLI: Typer + rich
- 다이어그램: Mermaid

확장 가능성 (현재 범위 밖): [docs/FUTURE_WORK.md](./docs/FUTURE_WORK.md)

## 문서 인덱스

| 문서 | 내용 |
|---|---|
| [VISION](./docs/VISION.md) | 비전·배경·TCP 비유·로드맵 |
| [ARCHITECTURE](./docs/ARCHITECTURE.md) | 4 핵심 모듈 + 옵션, SQLite 스키마, CLI 명령 체계 |
| [LEARNING_CARDS](./docs/LEARNING_CARDS.md) | 학습 카드 시스템 — 데이터 모델, 생성 파이프라인, 본인 구현 vs LLM 영역 |
| [INTERFACES](./docs/INTERFACES.md) | Protocol 기반 모듈 contract |
| [REQUIREMENTS](./docs/REQUIREMENTS.md) | 페르소나, 5W1H 페인포인트, 유스케이스, V&V 정책 |
| [WBS](./docs/WBS.md) | 12일 일정 + 트랙 구조 |
| [METRICS](./docs/METRICS.md) | FP / EV / ISO 25010 정의·공식 (옵션 모듈) |
| [COMPETITIVE](./docs/COMPETITIVE.md) | 기존 도구 비교 (CodeRabbit, traceability-check 등) |
| [FUTURE_WORK](./docs/FUTURE_WORK.md) | 확장 가능성 (Pub/Sub, TEE, multi-vendor) |
| [DISCUSSION_LOG](./docs/DISCUSSION_LOG.md) | 일별 자연어 토의·의사결정 일지 |
| [AI_TOOLING](./docs/AI_TOOLING.md) | AI 도구 선정 근거 |
| [AI_USAGE](./docs/AI_USAGE.md) | AI 사용 일지 |
| [EV_LOG](./docs/EV_LOG.md) | 일별 EV 측정 |

## 작성자

오유준 (홍익대학교 컴퓨터공학과)
