# WBS — softgate 12일 일정

마감: 2026-06-08 23:59
시작: 2026-05-27

## 4 트랙 병렬 구조

```
Day:  1    2    3    4    5    6    7    8    9    10   11   12
      [착수][요구][설계][T1·T2·T3·T4 병렬 개발──────][통합][테스트][보고서]
                       └Track 1: Stage Gate → Process Log──┘
                       └Track 2: UseCase Logger────────┘
                       └Track 3: SOLID Judge───────┘
                       └Track 4: FP Counter → EV Tracker──┘
```

## Day-by-Day Breakdown

| Day | 날짜 | 단계 | 산출물 | 예상 Commit | EV 가중치 누적 |
|---|---|---|---|---|---|
| 1 | 05-27 | 착수 | repo 초기화, README, WBS, REQUIREMENTS, AI_TOOLING | 5 | 5% |
| 2 | 05-28 | 요구분석 | 페르소나, 유스케이스 다이어그램 4-6개 (Mermaid), 5W1H, worst-case | 4 | 12% |
| 3 | 05-29 | 아키텍처 설계 | SAGA 단계 정의, 모듈 인터페이스, SQLite 스키마, hook 동작 검증 | 5 | 20% |
| 4 | 05-30 | T1+T2+T3+T4 병렬 시작 | 4 모듈 골격 + 인터페이스 stub | 8 | 35% |
| 5 | 05-31 | T1 Stage Gate 핵심 / T2 Mermaid 생성 / T3 SOLID 규칙 / T4 FP 계산 | 4 모듈 각 50% | 8 | 50% |
| 6 | 06-01 | T1 Process Log 시작 / T2 DB 통합 / T3 LLM judge 통합 / T4 EV Tracker 시작 | 4 모듈 각 75% | 7 | 65% |
| 7 | 06-02 | T1 Process Log 완료 / T3 재요청 루프 / T4 EV Tracker 핵심 | 모듈 6개 완성 | 6 | 75% |
| 8 | 06-03 | 통합 1 | 모듈 간 인터페이스 검증, choreography 이벤트 버스 | 5 | 82% |
| 9 | 06-04 | 통합 2 | End-to-end 테스트, SAGA rollback 검증 | 5 | 88% |
| 10 | 06-05 | 테스트 | 단위/통합/시스템/회귀 — 커버리지 70%+ | 5 | 92% |
| 11 | 06-06 | dogfooding + 보고서 초안 | softgate를 다른 작업에 적용 + 보고서 초안 | 4 | 97% |
| 12 | 06-07 | 보고서 마감 + 제출 준비 | PDF, repo 정리, 데모 스크린샷 | 3 | 100% |

(06-08은 buffer / 마감일)

총 예상 commit: ~60개. 매일 평균 5개 → 자연스러운 history.

## Track별 상세

### Track 1 — Stage Gate + Process Log (직렬, hook 공유, Day 4-7)

이유: 둘 다 Claude Code hook 기반. trace state 공유 필수 → 결합도 높아 동일 트랙.

- Day 4-5: Stage Gate — `PreToolUse` hook 등록, 단계 state machine, 요구사항 부재 시 block
- Day 5-6: Stage Gate — SAGA rollback 로직, idempotency 보장
- Day 6-7: Process Log — `Stop` hook 등록, transcript 분류기 (요구/설계/구현/테스트/유지보수)
- Day 7: Process Log — ISO 25010 메트릭 매핑, 시각화 (CLI 테이블)

### Track 2 — UseCase Logger (독립, Day 4-7)

- Day 4: Markdown 파서 (actor, scenario, include 관계)
- Day 5: Mermaid 다이어그램 자동 생성
- Day 6: SQLite 스키마, CRUD API
- Day 7: Stage Gate가 참조하는 인터페이스

### Track 3 — SOLID Judge (독립, Day 4-7)

- Day 4: Diff 파싱 (git diff format)
- Day 5: SOLID 5원칙 규칙 엔진 (LLM judge subagent prompt)
- Day 6: 응집도/결합도 채점, 점수 통합
- Day 7: 자동 재요청 루프

### Track 4 — FP Counter → EV Tracker (조건부 순차, Day 4-7)

- Day 4: FP Counter — EI/EO/EQ/ILF/EIF 입력 UI (CLI), 복잡도 가중치 테이블
- Day 5: FP Counter — FP 계산 → EV Tracker 인터페이스 정의
- Day 5-6: EV Tracker — WBS 파서, commit/test 진척 측정
- Day 6-7: EV Tracker — FP 가중치 통합, SPI/CPI 산출

## Risk 항목

1. **통합 단계 지연** - 4 트랙이 Day 7에 모이는데 인터페이스 어긋나면 통합 시간 부족. 완충: Day 3에 인터페이스 명세 확정 + Day 6 저녁에 1차 통합 PoC 시도로 호환성 확인. Day 7 통합 합류가 실제로 가능할지 미지수인 상황 (Brooks 법칙이 1인 + 다중 세션에도 적용된다면 폭발 가능)

2. **LLM judge 비결정성** - SOLID Judge 점수가 매번 다를 가능성. 완충: temperature=0, 동일 prompt 회귀 테스트. 점수 100% 일관 보장은 어려움 → 점수는 hint, 최종 채택은 사용자 판단 (REQUIREMENTS Section 7)

3. **Claude Code hook 권한 충돌** - 사용자 환경 `~/.claude/settings.json`이 `defaultMode: acceptEdits`인 경우 `PreToolUse` 차단 hook이 override 가능한지 미확인 상태. 완충: 구현 초기에 hook 동작 PoC 1개로 사전 검증

4. **Brooks 법칙 자체** - 1인 + 다중 세션 운용이 "인력 추가"인지 "단일 인력의 멀티태스킹"인지 모호한 상황. 후자라면 인지 부하만 늘고 통합 비용 폭증 가능. 완충: 모든 세션이 Day 4에 동시 출발, Day 7 이후 신규 트랙 추가 금지. 이 risk가 실제로 터지는 경우 그 자체가 회고 자료가 되는 구조

## EV 계산 방식

- **PV (Planned Value)** = 일별 누적 % (위 표의 "EV 가중치 누적" 컬럼)
- **EV (Earned Value)** = 실제 완료 모듈/단계의 가중치 합
- **AC (Actual Cost)** = 실제 투입 시간 (시간 단위)
- **SV (Schedule Variance)** = EV - PV
- **SPI** = EV / PV
- **CPI** = EV / AC × 표준 시간 가중치

매일 측정 → `docs/EV_LOG.md`에 기록.

FP·EV·EI·EO·EQ·ILF·EIF 등 측정 지표의 정의·가중치 표·계산 공식·자동화 메커니즘은 [docs/METRICS.md](./METRICS.md)에 분리.
