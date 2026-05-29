# VISION — softgate

## TL;DR

softgate는 바이브코딩 시대의 TCP. unreliable AI coding 위에 SW공학 reliability를 얹는 검증·제약 프로토콜.

---

## 1. 배경 — 바이브코딩이 스탠다드가 되는 동안

2025년 2월 Andrej Karpathy가 "vibe coding"이라는 용어를 만든 지 1년 남짓, AI coding agent를 통한 코드 생성은 트렌드를 넘어 개발의 기본 모드가 되었다.

- 개발자 84%가 AI 도구 사용 (Stack Overflow Survey 2025)
- 개발자 월평균 AI 지출 약 $110, 최대 $430 (QuotaMeter 2025)
- Fortune 100 기업 90%가 GitHub Copilot 도입

그런데 같은 기간 동안 소프트웨어 품질은 향상되기는커녕 다음 두 가지 비유로 표현될 정도로 전락했다.

### "AI 스파게티"

기능은 분명히 동작한다. 단 50명의 개발자가 서로 한 번도 마주친 적 없는 상태로 짠 것 같은 코드베이스. 통합 시점에야 드러나는 구조적 결함. 매 커밋마다 기술부채가 쌓이는 라인. 한 CTO의 표현으로는 "perfectly works until it catastrophically fails."

### "공장 컨베이어벨트"

손길이 거의 닿지 않은 채 라인 끝에서 쏟아져나오는 양산형 제품. 빠르고 많이 나오지만, 출하 전 검수가 빠지면 결국 reject·환불·재작업 비용으로 돌아온다. 바이브코딩의 산출물도 비슷한 흐름. 빠르게 생산되고, 빠르게 main에 들어가고, 며칠 뒤 디버깅 비용으로 회수된다.

### 정량 근거

- AI 생성 코드는 직접 작성 대비 버그 1.7배, 보안 취약성 2배, 논리 오류 75% (CodeRabbit 2025)
- 2027년까지 AI 생성 코드에서 누적 약 $1.5T 기술부채 예측 (industry analyst)
- 2025년 8월 Final Round AI 설문: 18명 CTO가 AI 생성 코드로 인한 production disaster 경험 보고
- AI code churn 거의 2배 — 테스트는 통과하지만 통합·아키텍처 리뷰 이후 재작성 필요

단순한 도구 사용 미숙의 문제가 아니라, 새로운 형태의 소프트웨어 위기.

---

## 2. 동기 — 시류를 거스를 것이 아니라

바이브코딩은 사라지지 않는다. 개발자가 100% AI 없이 코드 짜는 시대로 되돌아가는 것도 비현실적. Karpathy 본인이 자기가 만든 용어를 "강도 1번" 정도로 평했음에도 시류는 이미 trajectory를 그렸다.

선택지는 두 가지.

1. **거스른다** — 바이브코딩 금지·교육·강제. 비현실적이고 효과도 제한적
2. **현명하게 한다** — SW공학 원칙을 바이브코딩 흐름 안에 끼워넣어 품질을 보장한다

softgate는 두 번째 길에 베팅한다.

---

## 3. 컨셉 — 바이브코딩 시대의 TCP

TCP는 unreliable한 IP 위에서 reliability를 보장하는 프로토콜이다. 패킷 손실, 순서 뒤바뀜, 중복, 전달 실패 같은 IP의 한계를 handshake, ACK, retransmission, flow control, congestion control로 보완한다.

softgate는 같은 발상을 AI coding 도메인에 적용한다.

| 네트워크 개념 | softgate 대응 |
|---|---|
| **3-way handshake** | Stage 진입 전 invariant 확인 → AI agent 의도 확인 → Stage 승인 |
| **Retransmission** | SOLID Judge 위반 시 자동 재요청. 최대 3회 후 사람이 ruling |
| **Flow control** | hook 응답 ≤ 500ms — 사용자 작업 속도를 막지 않는 throughput 보장 |
| **Congestion control** | LLM judge 환각으로 인한 무한 루프 방지. 혼잡 임계 시 사람에게 escalate |

IP가 본질적으로 unreliable하지만 TCP 덕분에 사용자가 안심하고 웹브라우저를 여는 것처럼, AI coding agent의 본질적 불안정성에도 softgate를 얹으면 사용자가 결과물을 안심하고 받을 수 있어야 한다는 것이 본 프로젝트의 가설.

---

## 4. 솔루션 — 4 핵심 모듈 + 옵션

상세 설계는 [ARCHITECTURE.md](./ARCHITECTURE.md), 학습 카드 시스템은 [LEARNING_CARDS.md](./LEARNING_CARDS.md).

### 핵심 1 — SOLID Judge + Learning Card Generator

- 입력: git diff + 변경 파일 컨텍스트
- LLM judge가 SOLID 5원칙 + 응집도 7단계 + 결합도 6단계 + 코드 스멜 자동 평가 (0-10점)
- 위반 시 **학습 카드 자동 생성**:
  - 위반 이유 (자연어 3-5줄)
  - 운영 단계 비용 예시 (실제로 어떤 비용으로 돌아오는지)
  - Before/After 코드 스니펫
  - 재요청 prompt (AI agent에 보낼 수정 지시)
- 사용자가 카드 검수·채택·거절. 거절 사유는 다음 카드 생성 시 prompt 개선에 반영
- 채택 시 재요청 prompt가 AI agent에 자동 전송 → 최대 3회 → 초과 시 사람 ruling
- 결정적 가치: 단순 채점이 아니라 **위반을 학습 기회로 전환**하는 폐쇄 루프

### 핵심 2 — Stage (누락 검출 + 자동 제안)

- SDLC 5단계(Requirement → Design → Dev → Test → Deploy) 누락 검출
- **차단하지 않는다**. 검출·제안만 (사용자 짜증 회피)
- AI 코드 변경 시도 시 누락 산출물 자동 안내 + 자동 생성 제안
- 강제 게이트 도구와 정반대 메시지 — "부드러움"이 정체성
- 결정적 가치: 단계 의식 자연스럽게 환기 + 진행 흐름 시각화

### 핵심 3 — Traceability (한국어·과제 양식 특화)

- REQ-001 ↔ UC-001 ↔ src/code.py ↔ tests/test_code.py 자동 매트릭스
- commit message 태그 `[REQ-001][UC-001]` 매칭으로 자동 갱신
- 누락 자동 알림: REQ 매핑 없음 / UC 코드 없음 / 코드 테스트 없음
- **한국어 commit message + 한국 대학생 과제 양식 first-class** (영어권 traceability 도구와 차별)
- 교수님 제출 포맷 자동 생성 (일별 진척 보고서, 형상관리 증빙)
- 결정적 가치: 요구 변경 시 영향 범위 자동 추적 + 한국 대학 워크플로우 정착

### 핵심 4 — Progress Dashboard

- 학습 카드 풀이 기록 (총 풀이 수, 채택률, 거절 사유 분석)
- SOLID 통과율 트렌드 (7일·30일·전체)
- 연속 사용 일수(streak)
- 모듈별 진척 (어떤 단계에서 자주 멈추는지)
- 차트는 CLI rendering(rich library) 또는 간단한 HTML
- 결정적 가치: "강제·채점·차단"이 아닌 **성취감 유발** UX. 학습이 누적되는 게 보이는 보상 구조

### 옵션 모듈 (선택 사용)

다음 모듈은 정량 지표·학교 과제 키워드 충족용. 핵심 가치는 위 4개에 집중.

- **EV Tracker** — PV/EV/SPI/CPI 자동 계산
- **FP Counter** — IFPUG 표준 FP 자동 산정
- **Process Log** — ISO 25010 품질 9축 매핑 시각화

---

## 5. 차별점 — 기존 도구와의 위치

상세 비교는 [COMPETITIVE.md](./COMPETITIVE.md). 솔직히 정리하면 각 모듈 단독으로는 비슷한 도구가 이미 존재.

- **SOLID 채점 영역**: CodeRabbit, Greptile, Qodo, CodeAnt AI, Kodus 등 LLM 기반 AI 코드 리뷰 도구
- **Traceability 영역**: shtracer, traceability-matrices, reqflow, Claude Plugin Hub의 traceability-check
- **Process gate 영역**: Claude Code Hooks 자체에 27개 이상의 hook events. permission gate, quality gate

softgate의 차별점은 다음에서 온다.

1. **3 모듈 결합** — SOLID + Traceability + Stage를 하나의 control plane으로 통합한 도구는 현재 시점에 보이지 않는다
2. **Hook 통합 지점** — 기존 도구는 대부분 PR 단계 또는 IDE 플러그인. softgate는 Claude Code hook으로 코드 작성 직후 inline 채점·검증
3. **자동 재요청 prompt 생성** — 기존 LLM 리뷰는 코멘트만 남기고 끝. softgate는 AI agent에 다시 보낼 prompt까지 자동 생성하여 루프 폐쇄

학교 과제 컨텍스트에서는 "혁신적 아이디어"보다 "어떻게 만들었는가(process)"가 평가 대상. 본인이 직접 구현하면서 SW공학 절차를 적용한 점이 가치.

---

## 6. 비전 — 사용 + 배포 가능 product로

본 12일 prototype은 비전의 0번째 단계. 본인이 직접 사용하면서 다음 흐름으로 확장.

1. **즉시 (현재)**: 본인 일상 코딩에 dogfooding. 매일 SOLID Judge·Stage가 본인을 어떻게 막거나 통과시키는지 관찰
2. **단기 (1-3개월)**: choreography 이벤트 버스 정식 분리 (Redis Streams 등). Cursor·opencode 등 multi-vendor 어댑터
3. **중기 (3-6개월)**: TEE 기반 로컬 실행. 기업·민감 도메인 진입 가능
4. **장기 (6-12개월)**: SaaS 단계. 팀 안에서 한 사람이 뭘 하는지 다른 사람이 자동으로 알 수 있는 협업 트래킹

배포 가능 product 형태가 되려면 위 모든 단계가 production-ready 영역(CI/CD, security, payments, 본인 인증, SLA)을 갖춰야 한다. 자세한 범위는 [FUTURE_WORK.md](./FUTURE_WORK.md).

---

## 7. PO·기획자 관점

본 프로젝트는 단순 학교 과제가 아니다. AI 코딩 도구 헤비유저로서 작성자가 매일 마주치는 실제 페인(추측성 추상화, 검증 없는 commit, 디버깅 비용 누적)을 도구화한 시도. 개인 CLAUDE.md에 박아둔 Karpathy 4원칙을 자동화로 옮기는 메타 인지에서 출발했다.

product로서의 softgate가 갖춰야 할 것:

- **dogfooding 가치**: 작성자가 "이 도구 없으면 불안하다" 수준으로 매일 의존하는 흐름
- **도입 마찰 최소화**: hook 1개 등록만으로 즉시 작동. 기존 워크플로우 변경 최소
- **검수권은 사용자**: 도구는 hint만, ruling은 사람. "AI 맹신 금지"가 코드 레벨에서 강제됨
- **확장 가능한 인터페이스**: Protocol 기반 contract. 4 트랙 병렬 개발 가능

본 prototype에서 출발해 진짜 product로 가는 길은 길지만, 시작점이 명확한 상태.
