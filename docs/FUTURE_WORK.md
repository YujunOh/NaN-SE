# Future Work — 12일 prototype 범위 밖

본 12일 과제 prototype에서는 다루지 않지만, 후속 확장 가능한 방향. 보고서 결론부에서 1단락으로 언급 예정.

## 1. Choreography 이벤트 버스

현재 구현은 검출·설명 모듈이 SQLite 공유 + 직접 호출로 묶여 있다. 확장 시 publish/subscribe 미들웨어로 분리 가능. 아래 이벤트 예시 중 구현된 흐름은 `MetricFound`(검출 후 학습 카드 생성)뿐이고, 나머지(Stage, UseCase Logger 등)는 피벗 때 접은 원설계 모듈이라 가상의 예시다.

예상 이벤트:
- `MetricFound` → Learning Card Generator (설명 카드 생성) 구독. 현재 직접 호출로 구현됨
- `RequirementCreated`, `EditAttempted`, `StageCompleted` → 원설계 모듈(Stage, Process Log 등) 대상. 미구현

이 구조의 이론적 배경은 분산 시스템 영역에서 오래 다뤄진 service choreography 패턴. 모듈 간 결합도를 자료 결합 수준까지 낮추는 효과. 본 과제 prototype에서는 SQLite `events` 테이블 polling으로 흉내내는 수준이지만, 진짜 pub/sub 미들웨어(Redis Streams, NATS, Kafka 등)로 교체하면 확장성과 다중 노드 운용까지 가능한 구조로 갈 수 있음.

## 2. TEE 기반 로컬 실행

진짜 갭이 하나 있다. 검출은 로컬에서 결정론적으로 끝나 코드가 나가지 않지만, 학습 카드 생성 단계에서는 대상 코드를 Anthropic API로 그대로 보낸다. 개인 학습용 repo에서는 괜찮아도 기업 사내 코드라면 도입 차단 요인이다.

해결 방향은 설명층 LLM을 로컬 모델(Llama, Qwen 등)로 돌려 코드가 외부로 나가지 않게 하는 것이다. 격리 실행(TEE 등)이나 attestation 가능한 audit log까지 가면 더 단단해지지만, 강의 범위 밖 하드웨어 주제라 본 보고서에서는 한 줄 방향 제시로만 둔다. 12일 범위 밖.

## 3. Multi-vendor

현재 Claude Code 단일. Cursor, Codex, opencode 등이 hook API를 표준화하면 통합 가능. 어댑터 패턴으로 다음 구조를 검토 가능:

```
[Cursor PreEdit]         → [nanse adapter] → [Stage]
[Claude Code PreToolUse] → [nanse adapter] → [Stage]
[opencode]               → [nanse adapter] → [Stage]
```

hook 인터페이스가 벤더별로 다르기 때문에 표준화되지 않으면 어댑터 수가 폭증할 위험이 있는 구조.

## 4. Production Ready 영역 — 전혀 다른 범위

NaN-SE는 코드 작성 단계의 process gate에 집중. 실제 production-ready 시스템에 필요한 다른 영역은 본 과제 범위 밖이고, 이를 다 다루려면 별도 프로젝트 단위가 필요한 구조.

- **CI/CD 파이프라인**: 빌드 자동화, 테스트 자동 실행, 배포 자동화 (Jenkins, GitHub Actions, GitLab CI 등)
- **보안**: 인증/인가, 권한 관리, 시크릿 관리, 침투 테스트, 의존성 취약점 스캔
- **인프라**: caching, CDN, load balancer, auto-scaling, container orchestration
- **운영**: 로그 수집, 모니터링, instrumentation, alerting, SRE 워크플로우
- **데이터**: 백업, 복구, 마이그레이션, 분산 데이터베이스
- **법적·사업적**: payments, 본인 인증(개인정보), 약관, SLA, 컴플라이언스

이런 영역들이 빙산의 아래 부분이고 NaN-SE는 빙산의 일각만 다루는 도구. 본 과제 산출물은 production-ready 시스템이 아닌 prototype이라는 점을 정직하게 표기한다. MVP(Minimum Viable Product)는 돈 받고 팔 수 있는 최소 기능 단위라는 의미이므로, 현재 NaN-SE를 MVP라고 부르는 것은 부정확한 표현.

## 왜 12일 prototype 밖인가

Brooks 법칙: scope 확장 시 통합 비용이 polynomial로 늘어남. 본 과제는 단일 사용자·단일 머신으로 한정하고, 원설계 6 모듈 중 검출·설명 2개만 구현했다.

각 항목별 추가 작업량 추정:
- Choreography 이벤트 버스: +10-14일 (메시지 브로커 선택·통합)
- TEE 기반 로컬 실행: +20-30일 (학습 곡선 + 환경 셋업)
- Multi-vendor: +14-21일 (각 벤더 hook 인터페이스 학습)

본 prototype의 가치는 위 확장의 기초 골격 제공. 추후 확장 시 같은 SQLite 스키마·hook 인터페이스·학습 카드 prompt를 재사용 가능한 구조.

## 메모

확장 가능성을 적어두는 것은 좋지만, 12일 안에 만들지 못한 부분을 보고서에 너무 강조하면 "prototype 못 만들고 말로만 때운" 인상을 줄 위험이 있는 상황. 보고서에서는 이 문서를 참고용으로만 링크하고, 본문은 실제 구현한 검출·설명 폐루프의 lessons learned를 중심으로 갈 예정.
