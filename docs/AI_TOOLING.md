# AI 도구 선정 근거

과제 명세: "바이브코딩을 위한 인공지능은 자율적으로 선정 가능."

선정: **Claude Code 단일 사용** (Anthropic, claude-opus-4-7)

## 1. 후보 비교

| 도구 | 강점 | 약점 | softgate 적합도 |
|---|---|---|---|
| **Claude Code (CLI)** | Hook API 공개, Agent SDK, subagent 지원, Max 플랜으로 비용 고정 | 학습 곡선 | ⭕ Hook으로 Stage Gate 구현 직결 |
| ChatGPT Plus + Cursor | 인기 IDE, 빠른 prototyping | Hook API 제한, subagent 미지원 | △ Stage Gate 강제력 약함 |
| GitHub Copilot | 코드 자동완성 강함 | 세션 단위 추적 어려움, process gate 불가 | ✗ 본 도구 컨셉 부적합 |
| LangChain + 자체 LLM | 가장 유연 | 12일에 인프라부터 짜야 함 | ✗ Brooks 법칙 위반 |

## 2. 선정 근거

1. **Hook 통합**: Claude Code의 `PreToolUse`, `Stop`, `UserPromptSubmit` hook이 Stage Gate의 차단 메커니즘과 1:1 매핑. 다른 도구는 이런 hook 미공개.
2. **Subagent**: SOLID Judge의 LLM judge 호출에 Claude Agent SDK의 Task tool 사용. 별도 인프라 불필요.
3. **비용 고정**: Max 5x 플랜으로 quota 충분 (12일간). FP Counter·EV Tracker 등 보조 모듈의 LLM 호출도 부담 없음.
4. **카테고리 정렬**: multi-agent 실행 인프라(LangChain, LangGraph, agent harness 등) 카테고리에 Claude Code가 속함
5. **dogfooding**: 본인이 매일 사용하는 도구. 12일간 softgate를 softgate로 만드는 메타 검증 가능.

## 3. 단일 선택의 risk와 완충

| Risk | 완충 |
|---|---|
| 단일 벤더 의존 → Anthropic API 장애 시 작업 중단 | 로컬 코드 작성·테스트는 Claude 없이도 가능. LLM judge만 일시 disable 후 수동 모드로 fallback. |
| 다른 도구와의 비교 부재 | 본 문서가 그 답변. Hook API 공개도 + 비용 구조로 정량 정당화. |
| 다중 세션 = Brooks 법칙 인력 추가 | Day 4에 모든 세션 동시 출발, Day 7 이후 신규 세션 추가 금지. |

## 4. 사용 정책 — "검수는 사람"

검증(Verification)과 확인(Validation)은 결국 사람이 한다는 것이 핵심. 시스템·문서가 맞는지(검증), 사용자 요구에 타당한지(확인) 둘 다 사람의 판단 영역.

본 과제 진행 정책:

- **commit message**는 본인이 직접 작성. AI 자동 생성 commit 금지. `Co-Authored-By: Claude` 같은 자동 부착도 금지 (과제 산출물은 본인 산출물).
- **AI 출력 채택 기준**: Day 8 통합 후부터는 softgate의 SOLID Judge가 매긴 점수를 *보조 지표*로 사용. 단, 최종 채택 여부는 본인이 결정. Judge가 통과시켜도 본인이 "이거 필요 없는 추상화 같은데"라고 판단하면 reject.
- **Stage Gate 우회**: 본인이 `--force` 우회한 횟수는 EV Log에 마킹. 매일 회고에서 "오늘 왜 우회했나" 1줄로 기록 → 도구 자체의 false positive 패턴 발견용.
- **AI 사용 로그**: `docs/AI_USAGE.md`에 일별 기록 (Day 2부터). 형식: "오늘 AI가 X 잘못 만들어서 내가 Y로 고쳤다. 다음엔 prompt를 Z로 바꿔보자". 정량 지표 아닌 본인 회고.

이 정책은 AI에게 자율성을 너무 주면 추측성 기능·추상화가 누적된다는 작성자의 경험(REQUIREMENTS Section 1 P1)과 V&V 정의가 만나는 지점에 위치.
