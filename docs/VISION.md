# VISION: softgate

> **피벗 반영(Day 5)**: 위반 검출은 결정론적 메트릭(Metric Analyzer: LCOM4, 순환복잡도)이 하고 LLM은 채점하지 않는다. 아래 옛 "SOLID Judge" 표현은 검출층(Metric Analyzer)으로 정정한다. 경위는 DISCUSSION_LOG.md Day 5.

## 요약

softgate는 바이브코딩 시대의 TCP. 불안정한 AI 코딩 위에 SW공학 신뢰성을 얹는 검증·제약 프로토콜. AI가 만든 SW공학 위반을 단순 차단하는 게 아니라 학습 카드로 전환해 사용자가 원칙을 자연스럽게 익히게 만든다.

---

## 1. 배경 — 바이브코딩이 스탠다드가 되는 동안

2025년 2월 Andrej Karpathy가 "vibe coding"이라는 용어를 만든 지 1년 남짓, AI coding agent를 통한 코드 생성은 트렌드를 넘어 개발의 기본 모드가 되었다.

- 개발자 84%가 AI 도구 사용 (Stack Overflow Survey 2025)
- 개발자 월평균 AI 지출 약 $110, 최대 $430 (QuotaMeter 2025)
- Fortune 100 기업 90%가 GitHub Copilot 도입

그런데 같은 기간 동안 소프트웨어 품질은 향상되기는커녕 다음 두 가지 비유로 표현될 정도로 전락했다.

### "AI 스파게티"

기능은 분명히 동작한다. 다만 수십 명의 개발자가 서로 한 번도 협의한 적 없이 각자 짠 듯한 코드베이스가 만들어진다. 통합 시점에야 드러나는 구조적 결함. 매 커밋마다 기술부채가 쌓이는 라인. 한 CTO의 표현을 빌리면 "평소엔 완벽히 동작하다가 어느 순간 통째로 무너지는" 코드.

### "공장 컨베이어벨트"

손길이 거의 닿지 않은 채 라인 끝에서 쏟아져나오는 양산형 제품. 빠르고 많이 나오지만, 출하 전 검수가 빠지면 결국 reject·환불·재작업 비용으로 돌아온다. 바이브코딩의 산출물도 비슷한 흐름. 빠르게 생산되고, 빠르게 main에 들어가고, 며칠 뒤 디버깅 비용으로 회수된다.

### 정량 근거

- AI 생성 코드는 직접 작성 대비 버그 1.7배, 보안 취약성 2배, 논리 오류 75% (CodeRabbit 2025)
- 2027년까지 AI 생성 코드에서 누적 약 $1.5T 기술부채 예측 (industry analyst)
- 2025년 8월 Final Round AI 설문: 18명 CTO가 AI 생성 코드로 인한 production disaster 경험 보고
- AI code churn 거의 2배 — 테스트는 통과하지만 통합·아키텍처 리뷰 이후 재작성 필요

단순한 도구 사용 미숙의 문제가 아니라, 새로운 형태의 소프트웨어 위기.

---

## 2. 동기 — 흐름을 막을 게 아니라 흐름 안에 원칙을 끼워넣는다

바이브코딩은 사라지지 않는다. 개발자가 AI를 안 쓰던 시대로 되돌아가는 것도 비현실적. Karpathy가 처음 "vibe coding"이라는 용어를 만들었을 때는 "대충 결과만 보고 굴리는 느낌"이라는 가벼운 뉘앙스였지만, 1년 만에 산업 전반의 기본 모드가 됐다.

그렇다면 선택지는 두 가지.

1. **흐름을 막는다** — 바이브코딩 금지·교육·강제. 비현실적이고 효과도 제한적
2. **흐름 안에 원칙을 끼워넣는다** — SW공학 원칙을 바이브코딩 흐름 그대로에 자연스럽게 끼워서 품질을 보장한다

softgate는 두 번째 길에 베팅한다.

---

## 3. 컨셉 — 바이브코딩 시대의 TCP

TCP는 unreliable한 IP 위에서 reliability를 보장하는 프로토콜이다. 패킷 손실, 순서 뒤바뀜, 중복, 전달 실패 같은 IP의 한계를 handshake, ACK, retransmission, flow control, congestion control로 보완한다.

softgate는 같은 발상을 AI coding 도메인에 적용한다.

| 네트워크 개념 | softgate 대응 |
|---|---|
| **3-way handshake** | Stage 진입 전 invariant 확인 → AI agent 의도 확인 → Stage 승인 |
| **Retransmission** | Metric Analyzer 위반 검출 시 학습 카드 재요청. 최대 3회 후 사람이 ruling |
| **Flow control** | hook 응답 ≤ 500ms. 사용자 작업 속도를 막지 않는 throughput 보장 |
| **Congestion control** | LLM 설명층 환각으로 인한 무한 루프 방지. 혼잡 임계 시 사람에게 escalate |

IP가 본질적으로 unreliable하지만 TCP 덕분에 사용자가 안심하고 웹브라우저를 여는 것처럼, AI coding agent의 본질적 불안정성에도 softgate를 얹으면 사용자가 결과물을 안심하고 받을 수 있어야 한다는 것이 본 프로젝트의 가설.

---

## 4. 솔루션 — 4 핵심 모듈 + 옵션

상세 설계는 [ARCHITECTURE.md](./ARCHITECTURE.md), 학습 카드 시스템은 [LEARNING_CARDS.md](./LEARNING_CARDS.md).

### 핵심 1: Metric Analyzer(검출) + Learning Card Generator(설명)

- 입력: 변경 파일 소스
- Metric Analyzer가 LCOM4(SRP·모듈성)·순환복잡도를 결정론적으로 계산해 임계 초과를 finding으로 검출 (LLM 없음). SOLID 전체·응집도 7단계·결합도 6단계 명칭 분류는 범위 밖
- 위반 검출 시 **LLM 설명층이 학습 카드 생성**:
  - 위반 이유 (자연어 3-5줄)
  - 운영 단계 비용 예시 (실제로 어떤 비용으로 돌아오는지)
  - Before/After 코드 스니펫
  - 재요청 prompt (AI agent에 보낼 수정 지시)
- 사용자가 카드 검수·채택·거절. 거절 사유는 다음 카드 생성 시 prompt 개선에 반영
- 채택 시 재요청 prompt가 AI agent에 자동 전송 → 최대 3회 → 초과 시 사람 ruling
- 결정적 가치: 단순 검출이 아니라 **위반을 학습 기회로 전환**하는 폐쇄 루프

### 핵심 2: Stage (누락 검출 + 자동 제안)

- SDLC 5단계(Requirement → Design → Dev → Test → Deploy) 누락 검출
- **차단하지 않는다**. 검출하고 제안만 한다 (작업 흐름이 끊겨서 사용자가 도구를 끄게 되는 상황 회피)
- AI 코드 변경 시도 시 누락 산출물 자동 안내 + 자동 생성 제안
- 강제 게이트 도구와 정반대 메시지 — "부드러움"이 정체성
- 결정적 가치: 단계 의식 자연스럽게 환기 + 진행 흐름 시각화

### 핵심 3 — Traceability (요구 추적 데모)

- REQ-001 ↔ UC-001 ↔ src/code.py ↔ tests/test_code.py 자동 매트릭스
- commit message 태그 `[REQ-001][UC-001]` 매칭으로 자동 갱신
- 누락 자동 알림: REQ 매핑 없음 / UC 코드 없음 / 코드 테스트 없음
- 결정적 가치: 요구 변경 시 영향 범위 자동 추적

### 핵심 4 — Progress Dashboard

- 학습 카드 풀이 기록 (총 풀이 수, 채택률, 거절 사유 분석)
- SOLID 통과율 트렌드 (7일·30일·전체)
- 연속 사용 일수(streak)
- 모듈별 진척 (어떤 단계에서 자주 멈추는지)
- 차트는 CLI rendering(rich library) 또는 간단한 HTML
- 결정적 가치: "강제·채점·차단"이 아닌 **성취감 유발** UX. 학습이 누적되는 게 보이는 보상 구조

### 옵션 모듈 (선택 사용)

다음 모듈은 정량 지표용. 핵심 가치는 위 4개에 집중.

- **EV Tracker** — PV/EV/SPI/CPI 자동 계산
- **FP Counter** — IFPUG 표준 FP 자동 산정
- **Process Log** — ISO 25010 품질 9축 매핑 시각화

---

## 5. 실제 작동 예시 — 하루의 시연

글 설명만으로는 "그래서 뭐가 돌아간다는 건지" 잡히지 않을 수 있다. 실제 CLI 출력 형식으로 하루 흐름을 그려본다.

### 5.1 요구사항 누락 검출

사용자가 Claude Code에 자연어 지시.

```
> 결제 모듈 만들어줘
```

softgate Stage가 감지.

```
[softgate Stage]
관련 REQ ID 없이 코드 변경을 시도합니다.

→ [A] 자동 생성 / [M] 직접 입력 / [S] 건너뛰기
```

`[A]` 선택 시 softgate가 자동으로 골격을 만든다.

```
REQ-005 결제 처리 기능
  AC-001 카드 정보 입력
  AC-002 결제 실패 시 재시도 (최대 3회)
  AC-003 영수증 자동 발송

UC-005 사용자가 결제 시도
  Actor: 사용자, PaymentGateway
  Scenario: 카드 입력 → 인증 → 결제 → 영수증
```

이 골격은 사용자가 수정 가능. 채택 시 그대로 DB에 저장되고 Claude Code가 이어서 PaymentService 코드 작성.

### 5.2 SOLID 위반 → 학습 카드

Claude Code가 생성한 코드.

```python
class PaymentService:
    def process_payment(self): ...
    def send_email(self): ...
    def log_audit(self): ...
    def update_inventory(self): ...
```

softgate Metric Analyzer가 결정론적으로 검출.

```
LCOM4:     4   (연결 요소 4개 = 책임 분리 신호)
임계:      1   초과
순환복잡도: 임계 10 이내
```

LCOM4가 임계를 넘으므로 LLM 설명층이 학습 카드 자동 생성.

```
╭─ CARD-007 | SRP Violation LCOM4=4 ───────────────────╮
│                                                       │
│ 위반 이유:                                            │
│   PaymentService가 결제, 이메일, 감사 로그, 재고      │
│   업데이트를 모두 담당. 책임이 4개로 늘어남.          │
│                                                       │
│ 운영 단계 비용:                                       │
│   재고 로직 변경 시 결제 모듈 회귀 테스트 전체가      │
│   필요해져 배포 지연.                                 │
│                                                       │
│ Before:                                               │
│   class PaymentService:                               │
│       def process_payment(self): ...                  │
│       def send_email(self): ...                       │
│       def log_audit(self): ...                        │
│       def update_inventory(self): ...                 │
│                                                       │
│ After:                                                │
│   class PaymentService: ...        # 결제만           │
│   class EmailNotifier: ...         # 영수증           │
│   class AuditLogger: ...           # 감사             │
│   class InventoryUpdater: ...      # 재고             │
│                                                       │
│ 학습 포인트:                                          │
│   • SRP는 클래스가 변경되는 이유가 하나여야 한다는 원칙
│   • 책임 분리는 테스트 격리에도 도움                  │
│   • 변경 사유가 다르면 클래스도 다르게                │
│                                                       │
│ [A]ccept  [R]eject  [S]kip                            │
╰───────────────────────────────────────────────────────╯
```

사용자가 `[A]` 누르면 카드 안의 재요청 prompt가 Claude Code에 자동 전송된다.

```
[softgate → Claude Code]
PaymentService를 다음 4개로 분리하세요:
- PaymentService (process_payment만)
- EmailNotifier (send_email)
- AuditLogger (log_audit)
- InventoryUpdater (update_inventory)
```

Claude Code가 재작성 → softgate가 재채점 → SRP 8/10 통과.

### 5.3 Commit 시점에 Traceability 자동 갱신

```
> git commit -m "결제 모듈 1차 구현 [REQ-005][UC-005]"
```

softgate Traceability가 commit 감지하고 매트릭스 갱신.

```
$ softgate trace

REQ-005 → UC-005 → src/payment.py → tests/test_payment.py   complete
REQ-004 → UC-004 → src/auth.py    → (없음)                   no_test
REQ-003 → (없음)  →  -            →  -                       no_uc
```

테스트가 없는 REQ-004, UC가 없는 REQ-003을 한눈에 발견.

### 5.4 하루를 마치며 — Progress Dashboard

```
$ softgate dashboard

╭─ softgate Progress — 2026-05-29 ───────────────────╮
│                                                     │
│ 학습 카드                                           │
│   생성: 12장                                        │
│   채택: 9장 (75%)                                   │
│   거절: 3장                                         │
│                                                     │
│ SOLID 통과율                                        │
│   오늘: 67%  (전일 60% → +7%p)                      │
│   7일 평균: 63%                                     │
│                                                     │
│ 연속 사용: 3일                                      │
│                                                     │
│ 자주 걸린 원칙                                      │
│   SRP: 4회                                          │
│   DIP: 3회                                          │
│   Cohesion: 2회                                     │
│                                                     │
╰─────────────────────────────────────────────────────╯
```

차단당해서 짜증나는 게 아니라, 오늘 얼마나 학습했는지 + 통과율이 어떻게 올랐는지 시각화되는 보상 구조.

---

## 6. 차별점 — 기존 도구와의 위치

상세 비교는 [COMPETITIVE.md](./COMPETITIVE.md). 솔직히 정리하면 각 모듈 단독으로는 비슷한 도구가 이미 존재.

- **메트릭 검출 영역**: SonarQube, radon 등 정적 분석 도구. LLM 코드 리뷰(CodeRabbit, Greptile, Qodo 등)도 코멘트를 남김. softgate 차별점은 검출 자체가 아니라 검출→설명→검수 폐루프
- **Traceability 영역**: shtracer, traceability-matrices, reqflow, Claude Plugin Hub의 traceability-check
- **Process gate 영역**: Claude Code Hooks 자체에 27개 이상의 hook events. permission gate, quality gate

softgate의 차별점은 다음에서 온다.

1. **3 모듈 결합** — SOLID + Traceability + Stage를 하나의 control plane으로 통합한 도구는 현재 시점에 보이지 않는다
2. **Hook 통합 지점** — 기존 도구는 대부분 PR 단계 또는 IDE 플러그인. softgate는 Claude Code hook으로 코드 작성 직후 inline 검출·검증
3. **자동 재요청 prompt 생성** — 기존 LLM 리뷰는 코멘트만 남기고 끝. softgate는 AI agent에 다시 보낼 prompt까지 자동 생성하여 루프 폐쇄

---

## 7. 비전 — 사용 + 배포 가능 product로

본 12일 prototype은 비전의 0번째 단계. 본인이 직접 사용하면서 다음 흐름으로 확장.

1. **즉시 (현재)**: 본인 일상 코딩에 dogfooding. 매일 Metric Analyzer·Stage가 본인을 어떻게 막거나 통과시키는지 관찰
2. **단기 (1-3개월)**: choreography 이벤트 버스 정식 분리 (Redis Streams 등). Cursor·opencode 등 multi-vendor 어댑터
3. **중기 (3-6개월)**: TEE 기반 로컬 실행. 기업·민감 도메인 진입 가능
4. **장기 (6-12개월)**: SaaS 단계. 팀 안에서 한 사람이 뭘 하는지 다른 사람이 자동으로 알 수 있는 협업 트래킹

배포 가능 product 형태가 되려면 위 모든 단계가 production-ready 영역(CI/CD, security, payments, 본인 인증, SLA)을 갖춰야 한다. 자세한 범위는 [FUTURE_WORK.md](./FUTURE_WORK.md).

---

## 8. PO·기획자 관점

본 프로젝트는 단순 학교 과제가 아니다. AI 코딩 도구 헤비유저로서 작성자가 매일 마주치는 실제 페인(추측성 추상화, 검증 없는 commit, 디버깅 비용 누적)을 도구화한 시도. 개인 CLAUDE.md에 박아둔 Karpathy 4원칙을 자동화로 옮기는 메타 인지에서 출발했다.

product로서의 softgate가 갖춰야 할 것:

- **dogfooding 가치**: 작성자가 "이 도구 없으면 불안하다" 수준으로 매일 의존하는 흐름
- **도입 마찰 최소화**: hook 1개 등록만으로 즉시 작동. 기존 워크플로우 변경 최소
- **검수권은 사용자**: 도구는 hint만, ruling은 사람. "AI 맹신 금지"가 코드 레벨에서 강제됨
- **확장 가능한 인터페이스**: Protocol 기반 contract. 4 트랙 병렬 개발 가능

본 prototype에서 출발해 진짜 product로 가는 길은 길지만, 시작점이 명확한 상태.
