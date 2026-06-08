# 폴리글랏 대시보드 확장 — 설계·핸드오프

작성 2026-06-01. 이 문서는 CLI 전용이던 NaN-SE에 읽기 API(Python/FastAPI)와 웹 대시보드(TypeScript/React)를 더하는 확장의 설계와 진행 기록이다. 멀티에이전트로 빌드·리뷰를 나눠 진행하므로, 각 에이전트가 같은 계약을 보도록 API 스키마를 여기 고정한다. 동시에 형상관리 증빙으로 의사결정을 남긴다.

## 1. 왜 언어를 나누나

검출(결정론적)과 설명(LLM)을 분리한 게 NaN-SE의 핵심 논지다. 이 분리를 언어 레이어까지 끌고 간다. 각 관심사를 그 관심사에 가장 맞는 도구로 구현하면 분리의 효용이 코드로 드러난다.

| 레이어 | 언어/스택 | 이유 |
|---|---|---|
| 검출 | Python (ast, radon) | 정적 분석 생태계가 가장 두껍다. 결정론적 코어 |
| 설명 | LLM (provider 교체 가능: Anthropic·Gemini, Python) | 자연어 설명만 담당. 점수 매기기 안 함 |
| 읽기 API | Python (FastAPI) | 검출·설명 결과가 이미 Python/SQLite에 있으므로 같은 런타임에서 노출 |
| 표현 | TypeScript (Vite + React) | 인터랙티브 시각화는 브라우저 생태계가 최적 |
| 저장 | SQLite | 로컬 단일 사용자 도구엔 zero-config가 정답. source of truth |

경계는 HTTP다. Python이 SQLite에 쓰고 FastAPI로 읽기만 노출하면, TypeScript 프론트는 그 계약만 알면 된다. 언어가 달라도 결합은 약하다(낮은 결합도). 이게 분리의 효용이다.

## 2. 검수는 여전히 사람, 그리고 CLI

대시보드는 읽기 전용이다. 카드 채택/거절은 기존 `nanse review <ID>` CLI에 그대로 둔다. 검수가 의도적 행위로 남아야 "검수는 사람" 원칙이 흐려지지 않는다. 대시보드는 무엇이 검출됐고 무엇이 검수를 기다리는지 보여주기만 한다.

## 3. API 계약 (고정)

base path `/api`. 전부 읽기(GET). FastAPI + uvicorn. `nanse serve`로 기동. CORS는 로컬 dev origin 허용.

### GET /api/health
```json
{ "status": "ok" }
```

### GET /api/stats
```json
{
  "total_findings": 12,
  "total_cards": 9,
  "review": { "accepted": 5, "rejected": 1, "pending": 3 },
  "acceptance_rate": 0.83,
  "by_principle": [
    { "principle": "Single Responsibility", "count": 3 },
    { "principle": "Open-Closed", "count": 2 }
  ],
  "by_severity": [ { "severity": 6, "count": 4 } ],
  "cards_over_time": [ { "date": "2026-05-31", "count": 4 } ]
}
```
`acceptance_rate`는 검수 완료분 중 채택 비율(accepted / (accepted+rejected)), 분모 0이면 null.

### GET /api/findings
findings 테이블 전체. 최신순.
```json
[ {
  "id": 1, "session_id": "20260531-101500", "class_name": "AuthService",
  "metric": "lcom4", "value": 3.0, "threshold": 1.0,
  "principle": "Single Responsibility", "severity": 6,
  "source_file": "src/auth/service.py", "source_line": 12,
  "created_at": "2026-05-31T10:15:00"
} ]
```
지표별 원칙 매핑은 검출층이 고정한다. lcom4는 Single Responsibility, cyclomatic은 Open-Closed로 단다. `source_file`/`source_line`은 검출 시점에 ast·radon에서 잡은 위치로, 없으면 둘 다 null이다.

### GET /api/cards
카드 요약 목록. 쿼리 `status=pending|accepted|rejected|all`(기본 all).
```json
[ {
  "id": "CARD-001", "principle": "Single Responsibility", "severity": 6,
  "violation_reason": "AuthService가 ...",
  "source_file": "src/auth/service.py", "source_line": 12,
  "user_accepted": null, "generated_at": "2026-05-31T10:16:00",
  "reviewed_at": null
} ]
```

### GET /api/cards/{id}
카드 전체. 404 가능.
```json
{
  "id": "CARD-001", "session_id": "...", "finding_id": 1,
  "principle": "Single Responsibility", "severity": 6, "code_hash": "...",
  "violation_reason": "...", "cost_example": "...",
  "before_code": "...", "after_code": "...",
  "source_file": "src/auth/service.py", "source_line": 12,
  "learning_points": ["...", "..."], "revision_prompt": "...",
  "user_accepted": null, "user_feedback": null,
  "generated_at": "...", "reviewed_at": null
}
```

`principle`은 `Principle` enum의 값 문자열(예: "Single Responsibility"). 프론트는 이 문자열을 그대로 키로 쓴다.

## 4. 화면 구성 (대시보드)

1. 개요: total findings/cards 카드, 채택률, 원칙별 막대, 심각도 분포, 카드 생성 시계열. 원칙별 막대를 클릭하면 그 원칙으로 거른 Findings 탭으로 이동한다.
2. Findings 테이블: 대상·위치·지표·값/임계·원칙·심각도. 위치 칩을 누르면 `파일:줄` 문자열이 클립보드에 복사돼 에디터에서 바로 점프할 수 있다.
3. 학습 카드 갤러리: 카드 클릭 시 before/after 코드, 학습 포인트, 재요청 prompt, 검수 상태 배지(대기/채택/거절), 위치 칩
4. 지표 설명: LCOM4와 순환복잡도가 무엇을 세는지, 임계치(1, 10)를 어디서 가져왔는지 설명하는 정적 페이지. 검출이 결정론적이라는 논지를 사용자에게 직접 보인다.

## 5. orchestration 방식과 그 이유

목적은 속도가 아니라 무결성이다. 그래서 병렬 빌더로 쪼개 짜기보다, 통합 지점(API 계약)을 한곳에서 고정하고 빌드 후 독립 코드리뷰를 여러 번 거치는 쪽을 택했다. 병렬 빌더는 일관성이 깨지기 쉽고, 그게 바로 NaN-SE가 비판하는 "조율 없는 에이전트 스파게티"라 자기모순이다.

- 통합/계약: 단일 스레드(이 문서)가 API 스키마를 고정하고 백엔드를 직접 구현
- 빌드: 계약에 맞춰 백엔드(FastAPI), 프론트(React) 구현
- 리뷰: code-reviewer 에이전트가 백엔드·프론트를 독립으로 검토(QA 독립성). 결과는 `REVIEW_LOG.md`에 남김
- 수정·재검증: 리뷰 지적 반영 후 필요하면 2차 리뷰

리뷰 기록을 남기는 것 자체가 강의의 "QA 독립성·자기 의심" 실천 증빙이다.
