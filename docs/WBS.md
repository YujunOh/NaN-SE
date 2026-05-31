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

> Day 3 피벗 결과 트랙 재조정. 4 핵심 모듈 기준.

### Track 1 — Stage + SOLID Judge + Learning Card (핵심 핫 패스, Day 4-7)

이유: PreToolUse hook 진입 → Stage 상태 확인 → SOLID Judge 채점 → Learning Card 생성이 한 흐름. 분리 시 통합 비용 큼 → 동일 트랙.

- Day 4: Stage state machine + `PreToolUse` hook 등록. 누락 검출 로직(차단 X, 제안 O)
- Day 5: SOLID Judge — diff 파싱 + LLM judge prompt + 5원칙·응집도·결합도 채점
- Day 6: Learning Card Generator — 카드 데이터 모델, 생성 파이프라인, prompt 템플릿, DB 저장
- Day 7: 카드 검수 CLI(rich) + 채택 시 재요청 prompt를 hook으로 AI에 자동 전송

### Track 2 — Traceability (한국어/과제 양식, Day 4-7)

- Day 4: Markdown 파서 (REQ, UC, acceptance criteria). 한국어 양식 우선
- Day 5: Mermaid 다이어그램 자동 생성 + 한국어 commit message 태그 파서
- Day 6: SQLite traceability 테이블 + CRUD + gap 검출
- Day 7: 한국 대학 과제 양식 export (일별 진척 보고서, 형상관리 증빙)

### Track 3 — Progress Dashboard (Day 4-7)

- Day 4: SQLite dashboard_metrics 테이블 + 이벤트 구독 골격
- Day 5: 학습 카드 통계 (총 풀이 수, 채택률, 거절 사유 분포)
- Day 6: SOLID 통과율 트렌드(7일·30일) + streak 계산
- Day 7: CLI rendering(rich) + HTML 출력(선택)

### Track 4 — 옵션 모듈 (EV / FP / Process Log, Day 4-7)

학교 과제 키워드 충족용. 핵심 4 모듈 완성 후 시간 남으면 진행. scope 폭발 시 일부 생략 가능.

- Day 4-5: FP Counter — IFPUG 가중치 표 코드화, CLI 입력
- Day 5-6: EV Tracker — WBS 파서, commit 진척 측정, SPI/CPI 산출
- Day 6-7: Process Log — Stop hook + transcript 분류 + ISO 25010 매핑

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
