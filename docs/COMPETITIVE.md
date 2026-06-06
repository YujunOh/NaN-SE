# 포지셔닝 — 기존 도구와의 비교

## 한 줄 요약

NaN-SE는 AI coding agent를 **대체하지 않는** 도구. agent가 만든 코드의 응집도·복잡도 위반을 결정론적으로 검출하고 학습 카드로 설명하는 검증 보조 레이어

## 비교표

| 도구 | 역할 | NaN-SE와의 관계 | 핵심 차이 |
|---|---|---|---|
| Claude Code, GPT, Cursor, Gemini, 자체 LLM | AI coding agent (실행) | NaN-SE는 산출물을 검증하는 별도 레이어 (현재 CLI, hook 통합은 설계) | 실행 vs 검증 |
| **opencode planner** | "무엇을 어떻게 할지" 계획 agent (read-only) | NaN-SE는 그 계획이 요구사항·SOLID·테스트 기준에 맞는지 검증 | "할지" vs "타당한지" |
| SonarQube, ESLint, radon | 정적 분석 (메트릭 검출) | NaN-SE의 Metric Analyzer 검출 자체는 이들과 겹침. 차별점은 검출 뒤 LLM 설명 카드를 만들고 사람이 검수하는 흐름 (카드에 AI 재요청 prompt 포함) | 검출만 vs 검출→설명→검수 |
| Harness.io | CI/CD 배포 자동화 | 다른 단계 (NaN-SE는 PR 이전) | 배포 vs 개발 |
| LangSmith, Helicone | LLM observability (비용·레이턴시) | 측정 대상 다름. NaN-SE는 SW공학 절차 준수 | 운영 지표 vs 공학 절차 |
| Devin, Manus | end-to-end autonomous agent | 같이 사용 가능. autonomous agent의 산출물을 NaN-SE가 검수 | 자율 실행 vs 검수 |

## opencode planner와의 차이

opencode docs 기준 planner는 "코드 변경 없이 코드 분석·계획"을 담당하는 read-only subagent. 즉 "어떻게 할지"를 결정한다.

NaN-SE Stage는 다른 역할.

- **opencode planner**: "이 작업을 X 방식으로 하자" (제안)
- **NaN-SE Stage**: "이 작업을 시작하려면 Y가 먼저 있어야 한다" (단계 진입 조건)

둘은 보완 관계. 가상의 워크플로우:

```
사용자 요구
   ↓
[NaN-SE Stage 1: Requirement] - 요구사항 ID·유스케이스 존재 여부 확인
   ↓
[opencode planner] - 어떻게 구현할지 계획
   ↓
[NaN-SE Stage 2: Design] - 계획이 아키텍처 규칙 위반 없는지 확인
   ↓
[opencode build agent] - 실제 구현
   ↓
[NaN-SE Metric Analyzer] - 결정론적 메트릭(LCOM4·순환복잡도)으로 위반 검출
   ↓
[NaN-SE Learning Card] - 확정 위반을 LLM이 설명, 사용자가 검수
   ↓
[NaN-SE Process Log] - 단계별 비율 기록
```

긴 트랜잭션을 짧은 독립 단위로 잘라 단계별 검증을 끼워넣는 발상은 분산 시스템 SAGA 패턴의 SDLC 도메인 응용에 해당.

## "하네스"의 두 가지 의미

"하네스"라는 용어는 두 가지로 해석 가능. 하나는 LangChain, LangGraph 같은 multi-agent 실행 인프라(agent harness engineering). 다른 하나는 동명의 Harness.io (DevOps 플랫폼). 둘은 SDLC상 위치가 다른 영역.

| | Harness.io | Agent harness |
|---|---|---|
| 정의 | 엔터프라이즈 SDLC delivery platform | LangChain, LangGraph 같은 multi-agent 실행 인프라 |
| 무대 | CI/CD, 배포, 보안, 운영 | agent 실행, tool permission, context 관리 |
| 고객 | 엔터프라이즈 DevOps 조직 | AI 코딩 도구 사용자 |
| NaN-SE 관계 | 다른 단계 (PR 이후) | NaN-SE가 그 위에 얹는 정책 레이어 |

NaN-SE는 agent harness 위에 올라가는 SW공학 정책 엔진에 가까운 위치. Harness.io와는 SDLC상의 단계 자체가 다른 구조.

## 메모

비교표를 만들면서 정리된 점: NaN-SE가 "대체"가 아니라 "보완" 도구라는 점을 처음부터 명확히 잡지 않으면 "또 다른 AI 코딩 도구"로 오해받기 쉬운 구조. 보고서 제목·서론에서 이 점을 강조해야 하는 부분.

또 외부 분석을 참고하면서 "engineering governance platform" 같은 과도한 SaaS 표현이 제안되었지만, 12일 1인 prototype를 "platform"이라 부르는 것은 과장에 가까우므로 일부만 채택. 본 과제는 prototype 골격 수준임을 명확히 표기.
