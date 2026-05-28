# VISION — vibegate

## TL;DR

vibegate는 바이브코딩 시대의 TCP. unreliable AI coding 위에 SW공학 reliability를 얹는 검증·제약 프로토콜.

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

vibegate는 두 번째 길에 베팅한다.

---

## 3. 컨셉 — 바이브코딩 시대의 TCP

TCP는 unreliable한 IP 위에서 reliability를 보장하는 프로토콜이다. 패킷 손실, 순서 뒤바뀜, 중복, 전달 실패 같은 IP의 한계를 handshake, ACK, retransmission, flow control, congestion control로 보완한다.

vibegate는 같은 발상을 AI coding 도메인에 적용한다.

| 네트워크 개념 | vibegate 대응 |
|---|---|
| **3-way handshake** | Stage 진입 전 invariant 확인 → AI agent 의도 확인 → Stage 승인 |
| **Retransmission** | SOLID Judge 위반 시 자동 재요청. 최대 3회 후 사람이 ruling |
| **Flow control** | hook 응답 ≤ 500ms — 사용자 작업 속도를 막지 않는 throughput 보장 |
| **Congestion control** | LLM judge 환각으로 인한 무한 루프 방지. 혼잡 임계 시 사람에게 escalate |

IP가 본질적으로 unreliable하지만 TCP 덕분에 사용자가 안심하고 웹브라우저를 여는 것처럼, AI coding agent의 본질적 불안정성에도 vibegate를 얹으면 사용자가 결과물을 안심하고 받을 수 있어야 한다는 것이 본 프로젝트의 가설.

---

## 4. 솔루션 — 6 모듈 + SAGA 5 Stage

상세 설계는 [ARCHITECTURE.md](./ARCHITECTURE.md). 요약:

- 5 Stage SAGA (Requirement → Design → Dev → Test → Deploy)
- Stage 사이 invariant 자동 검증, 위반 시 보상 트랜잭션
- 6 모듈 hybrid 통신 (Stage 중심 orchestration + 보조 모듈 choreography)
- LLM judge subagent로 SOLID·응집도·결합도 자동 채점, 사용자가 최종 ruling

---

## 5. 차별점

상세 비교는 [COMPETITIVE.md](./COMPETITIVE.md). 핵심:

- Claude Code, Cursor, Codex, opencode 같은 **agent를 대체하지 않는다**. agent 위에 hook으로 얹히는 control plane
- SonarQube·ESLint 같은 정적 분석과 달리 **코드 작성 전 단계 진입 조건도 검증**
- Harness.io 같은 CI/CD 도구와 다른 단계 — vibegate는 PR 이전 시점에 작동

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

product로서의 vibegate가 갖춰야 할 것:

- **dogfooding 가치**: 작성자가 "이 도구 없으면 불안하다" 수준으로 매일 의존하는 흐름
- **도입 마찰 최소화**: hook 1개 등록만으로 즉시 작동. 기존 워크플로우 변경 최소
- **검수권은 사용자**: 도구는 hint만, ruling은 사람. "AI 맹신 금지"가 코드 레벨에서 강제됨
- **확장 가능한 인터페이스**: Protocol 기반 contract. 4 트랙 병렬 개발 가능

본 prototype에서 출발해 진짜 product로 가는 길은 길지만, 시작점이 명확한 상태.
