# Metrics — Function Point + Earned Value

vibegate가 측정하는 두 정량 지표(FP, EV)의 정의·계산 방식·자동화 메커니즘.

## 1. Function Point (FP)

소프트웨어 규모를 기능 관점에서 측정하는 표준 지표 (IFPUG 기준).

### 1.1 5가지 component

| 기호 | 영문 | 설명 |
|---|---|---|
| EI | External Input | 시스템에 입력되는 데이터 (사용자 입력, 외부 API 호출 등) |
| EO | External Output | 시스템이 출력하는 데이터 (보고서, 알림, 화면 표시 등) |
| EQ | External Query | 입력 후 즉시 응답하는 조회 (검색, 필터링 등). 데이터 변경 없음 |
| ILF | Internal Logical File | 시스템 내부에서 관리되는 논리적 데이터 집합 (DB 테이블 등) |
| EIF | External Interface File | 외부 시스템과 공유하는 데이터 집합. 본 시스템은 참조만 |

### 1.2 복잡도별 가중치 (IFPUG 표준)

| Component | Low | Average | High |
|---|---|---|---|
| EI | 3 | 4 | 6 |
| EO | 4 | 5 | 7 |
| EQ | 3 | 4 | 6 |
| ILF | 7 | 10 | 15 |
| EIF | 5 | 7 | 10 |

복잡도는 DET (Data Element Type) 개수와 FTR/RET (File Type Referenced / Record Element Type) 개수에 따라 결정.

### 1.3 UFP 계산

```
UFP (Unadjusted Function Points) = Σ (component count × weight)
```

예시: EI 5개(Average) + EO 3개(High) + ILF 2개(Average)
→ 5×4 + 3×7 + 2×10 = 20 + 21 + 20 = **61 UFP**

### 1.4 vibegate 자동 계산

`vibegate fp add <kind> <complexity>` CLI로 사용자가 component를 입력하면, 가중치 표를 기반으로 자동 합산.

```python
WEIGHTS = {
    ('EI',  'low'): 3, ('EI',  'avg'): 4, ('EI',  'high'): 6,
    ('EO',  'low'): 4, ('EO',  'avg'): 5, ('EO',  'high'): 7,
    ('EQ',  'low'): 3, ('EQ',  'avg'): 4, ('EQ',  'high'): 6,
    ('ILF', 'low'): 7, ('ILF', 'avg'): 10, ('ILF', 'high'): 15,
    ('EIF', 'low'): 5, ('EIF', 'avg'): 7, ('EIF', 'high'): 10,
}
```

가중치 표는 `vibegate/fp_counter.py`에 하드코딩 (외부 입력 변경 차단).

## 2. Earned Value (EV)

프로젝트 진척을 정량 측정하는 지표 (PMI PMBOK 기준).

### 2.1 핵심 지표

| 기호 | 영문 | 풀이 | 설명 |
|---|---|---|---|
| PV | Planned Value | BCWS (Budgeted Cost of Work Scheduled) | 특정 시점까지 예정된 작업의 계획 가치 |
| EV | Earned Value | BCWP (Budgeted Cost of Work Performed) | 특정 시점까지 실제 완료된 작업의 계획 가치 |
| AC | Actual Cost | ACWP (Actual Cost of Work Performed) | 특정 시점까지 실제 투입된 비용/시간 |
| BAC | Budget at Completion | - | 전체 프로젝트의 계획 총 가치 |

### 2.2 파생 지표

| 지표 | 공식 | 의미 |
|---|---|---|
| SV | EV - PV | Schedule Variance. + 이면 일정 앞섬, - 이면 지연 |
| CV | EV - AC | Cost Variance. + 이면 예산 내, - 이면 초과 |
| SPI | EV / PV | Schedule Performance Index. 1.0 = on schedule |
| CPI | EV / AC | Cost Performance Index. 1.0 = on budget |
| EAC | BAC / CPI | Estimate At Completion. 예상 최종 비용 |
| ETC | EAC - AC | Estimate To Complete. 남은 예상 비용 |
| VAC | BAC - EAC | Variance At Completion. 예상 최종 차이 |

### 2.3 vibegate 자동 계산

- **PV**: `docs/WBS.md`의 "EV 가중치 누적" 컬럼 기준 일별 누적 % 자동 파싱
- **EV**: 완료된 WBS task의 가중치 합계. commit 기반 자동 추정 (commit message에 task ID 매칭) + 사용자 확인
- **AC**: 실제 투입 시간. 사용자가 입력하거나 git log timestamp 차이로 추정

`vibegate wbs ev` CLI 실행 시 위 공식으로 자동 계산되어 `docs/EV_LOG.md`에 일별 스냅샷 기록.

## 3. FP × EV 통합

FP가 측정한 기능 규모를 EV의 가중치로 변환 가능.

```
WBS task의 PV 가중치 = (task에 속한 component의 FP 합) / (전체 프로젝트 UFP) × 100%
```

예시:
- 전체 프로젝트 UFP = 200
- Track 1 task A의 FP 합 = 40
- → task A의 PV 가중치 = 40 / 200 = **20%**

이 매핑이 vibegate의 EV Tracker가 FP Counter 결과를 수용하는 인터페이스(`include_fp(fp_total)`)의 핵심.

## 4. 한계

- **FP 산정의 주관성**: 복잡도(low/avg/high) 판정이 사람마다 다를 수 있는 상황. IFPUG 가이드라인을 따라도 ±20% 변동 가능. 동일 시스템을 5명이 산정하면 결과가 5개 나오는 게 일반적
- **EV의 binary 완료 가정**: 실제로는 task가 50% 완료 같은 중간 상태로 존재. vibegate는 단순화 위해 binary(완료/미완료)로 처리. 부분 진척률을 따로 입력하는 옵션은 향후 추가 검토
- **AC의 시간 측정**: 자동 추정이 어려움. 사용자가 직접 입력하는 것이 정확. git log timestamp는 보조 지표

## 5. ISO 25010 매핑 (Process Log 연동)

EV 측정 결과는 ISO 25010 품질 9축에 매핑되어 Process Log에서 시각화.

| ISO 25010 축 | vibegate 측정 대응 |
|---|---|
| 기능적합성 | Requirement Coverage (요구사항 만족률) |
| 성능효율성 | hook 응답 시간 (≤ 500ms 충족률) |
| 호환성 | (Future Work - multi-vendor) |
| 사용성 | CLI 명령 사용 빈도 (간접) |
| 신뢰성 | SOLID Judge 통과율 |
| 보안성 | (Future Work - TEE) |
| 유지보수성 | 응집도/결합도 점수 (SOLID Judge) |
| 이식성 | (Future Work - multi-vendor) |
| 안전성 | force_overrides 빈도 (낮을수록 안전) |

(Future Work 표시 항목은 현재 prototype 범위 밖)
