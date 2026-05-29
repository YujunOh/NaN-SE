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

softgate는 이 빈자리에 들어가는 미들웨어다. AI coding agent를 대체하는 도구가 아니라, agent 위에 hook으로 올라가서 단계별 진입 조건(요구·설계·테스트 기준)을 강제하고, 산출물의 SOLID·응집도·결합도·요구 충족도를 LLM judge로 자동 검증한다.

## 핵심 아이디어

긴 트랜잭션을 잘게 잘라 독립적으로 수행한다는 SAGA 패턴을 SDLC에 적용한다. 5단계(요구 → 설계 → 구현 → 테스트 → 배포)를 각각 트랜잭션으로 보고, 단계별 invariant(진입 조건)를 만족해야 다음으로 진행한다. 실패 시 이전 단계로 보상 트랜잭션(rollback) 수행.

분산 시스템 영역에서는 SAGA(1987), choreography vs orchestration, constraint-driven design, idempotency 같은 정합성 보장 기법이 오래 전부터 정립되어 있다. 최근의 AI agent 협업에서 드러나는 문제(상태 일관성·산출물 충돌·중복 작업·잘못된 의사결정 전파)는 새로운 카테고리의 문제가 아니라, 그 옛 패턴들이 다시 등장하는 형태에 가깝다. softgate는 새로운 개념을 발명하기보다, 이미 검증된 분산 시스템 패턴을 AI coding agent 도메인에 가져온 응용 레이어로 위치한다.

## 4 핵심 모듈 + 옵션

### 핵심

| 모듈 | 역할 |
|---|---|
| **SOLID Judge + Learning Card** | AI 생성 diff를 SOLID 5원칙 + 응집도 7단계 + 결합도 6단계로 자동 채점. 위반 시 학습 카드 자동 생성 (위반 이유·운영 단계 비용 예시·Before/After 코드·재요청 prompt). 사용자 검수 후 AI에 다시 전달하는 폐쇄 루프 |
| **Stage** | SDLC 5단계(Requirement→Design→Dev→Test→Deploy) 누락 검출 + 자동 제안. **차단하지 않는다** (사용자 짜증 회피, 강제 게이트 도구들과 정반대 메시지) |
| **Traceability** | REQ-001 ↔ UC-001 ↔ `src/code.py` ↔ `tests/test_code.py` 자동 매트릭스. 한국어 commit message 태그(`[REQ-001]`) + 한국 대학생 과제 양식·교수님 제출 포맷 first-class |
| **Progress Dashboard** | 학습 카드 풀이 기록, SOLID 통과율 트렌드, 연속 사용 일수, 모듈별 진척. 단순 차단·채점이 아닌 **성취감 유발** UX |

### 옵션 (학교 과제 키워드 충족용)

| 모듈 | 역할 |
|---|---|
| EV Tracker | PV/EV/SPI/CPI 자동 계산 (PMI PMBOK 기준) |
| FP Counter | IFPUG 표준 FP 자동 산정 |
| Process Log | ISO 25010 품질 9축 매핑 시각화 |

## 기존 도구와의 위치

| 도구 | 무대 | softgate와의 관계 |
|---|---|---|
| Claude Code, GPT (OpenAI), Cursor, Gemini, 자체 LLM | AI coding agent 실행 | softgate가 hook으로 위에 올라가는 구조 |
| LangChain, LangGraph, 자체 에이전트 프레임워크 | 에이전트 실행 인프라 | softgate는 그 위의 정책 레이어 |
| SonarQube, ESLint | 코드 작성 후 정적 분석 | softgate는 작성 전 단계 진입 조건도 검증 |
| LangSmith, Helicone | LLM 비용·레이턴시 observability | 측정 대상이 다름. softgate는 SW공학 절차 준수 |

softgate는 하나의 벤더(Claude, GPT, Gemini, 자체 LLM)에 종속되지 않는다. hook 인터페이스만 표준화되면 다른 벤더로도 어댑터를 통해 확장 가능한 구조다.

자세한 비교는 [docs/COMPETITIVE.md](./docs/COMPETITIVE.md)

## 핵심 정책 — 검수는 사람이 한다

검증(Verification)과 확인(Validation)은 결국 사람이 한다는 점이 핵심. softgate의 모든 LLM judge 출력은 hint이고, 최종 결정은 사용자가 한다.

- SOLID Judge가 통과시켜도 사용자가 reject 가능
- 학습 카드도 자동 생성된 콘텐츠를 사용자가 검수·채택. 거절 사유는 다음 카드 생성 시 prompt 개선에 반영
- Stage는 차단하지 않고 검출·제안만. 우회 명령 불필요
- Traceability 매트릭스 자동 매핑 결과를 사용자가 한 번 확인 후 채택

자세한 정책은 [docs/AI_TOOLING.md](./docs/AI_TOOLING.md), [docs/REQUIREMENTS.md](./docs/REQUIREMENTS.md)

## 기술 스택

- Python 3.11+
- Claude Agent SDK (LLM judge subagent)
- Claude Code Hooks: `PreToolUse`, `Stop`, `UserPromptSubmit`
- SQLite (세션 메타, EV 히스토리, 이벤트 버스)
- CLI: Typer
- 다이어그램: Mermaid

확장 가능성 (현재 범위 밖): [docs/FUTURE_WORK.md](./docs/FUTURE_WORK.md)

## 작성자

오유준 (홍익대학교 컴퓨터공학과)
