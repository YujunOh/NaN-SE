# 코드리뷰 루프 기록 — 폴리글랏 대시보드

2026-06-01. DASHBOARD_DESIGN.md 5절의 방식대로, 빌드 후 독립 리뷰를 거쳤다. 백엔드(Python/FastAPI)와 프론트(TypeScript/React)를 각각 다른 리뷰어가 동시에, 구현자와 분리해 검토했다. QA 독립성을 의도한 구성이다.

## 1차 리뷰

### 백엔드 (nanse/api, store, cli serve)

지적과 처리:

1. **status 쿼리 파라미터 검증 누락 (신뢰도 85, 반영)** — `/api/cards?status=`가 enum인데 범위 밖 값(오타·대소문자)이 와도 조용히 전체 목록을 반환했다. 계약은 `all|pending|accepted|rejected` 넷뿐이라, 범위 밖은 400으로 끊도록 수정. 잘못된 입력이 조용히 통과하면 디버깅이 어렵다는 지적이 타당.
2. **연결 누수 점검 (이슈 없음)** — 요청마다 Store(sqlite)를 컨텍스트 매니저로 열고 닫는다. 반환 객체는 메모리에 올라와 연결에 의존하지 않음을 확인. 실제 누수 없음.
3. **next_card_id 경쟁 조건 (신뢰도 80, 보류)** — COUNT 기반 ID 생성이라 병렬 learn 시 충돌 가능. 단 API 추가와 무관한 기존 CLI 설계이고, 단일 사용자 전제라 이번 범위에서 제외. 한계로 기록만.

계약 준수(health 응답, acceptance_rate의 0 분모 null 처리, findings 필드, 404, CORS 읽기 전용)는 이상 없음으로 확인됐다.

### 프론트 (web/src)

지적과 처리:

1. **모달 키보드·ARIA 누락 (신뢰도 82, 반영)** — 카드 상세 모달이 backdrop 클릭으로만 닫혀 키보드 사용자가 못 닫았다. Escape keydown 리스너 추가 + 모달에 `role="dialog"`, `aria-modal="true"` 부여. 오버레이의 기본 접근성 기대치라는 지적이 타당.
2. **useFetch의 alive 가드, 리스트 key, stopPropagation, 타입 nullability** — 전부 정상으로 확인(채택률·user_accepted·reviewed_at의 null 허용 타입이 계약과 일치). 인덱스 key는 재정렬 없는 정적 리스트라 허용.
3. **탭 전환 시 재요청으로 인한 로딩 깜빡임 (신뢰도 72, 보류)** — 캐시가 없어 매 마운트마다 재요청. 학생 프로젝트 수준에서 수용. 한계로만 기록.

타입 계약 일치, race 가드, key 안정성, 미사용 변수 없음, `tsc -b` 통과는 정상 확인됐다.

## 반영 후 재검증

- 백엔드: 잘못된 status 입력에 400, 정상 status는 기존대로 동작 확인.
- 프론트: `npm run build`(tsc -b + vite build) 통과 확인.

신뢰도 80 미만 지적(next_card_id, 로딩 깜빡임)은 이번 범위 밖으로 두되 한계로 남겼다. 둘 다 단일 사용자 로컬 도구 전제에서 실질 위험이 낮다.
