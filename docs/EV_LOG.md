# EV Log — vibegate 12일

매일 작업 마무리 시 측정. 형식 고정:

- PV / EV / SPI 한 줄
- 회고 2-3줄
- 우회 횟수: Stage `--force` 사용 횟수 (구현 단계 이후부터 의미 있음)
- AI 출력 채택률: 코드 작성 시작 후 의미 있음

WBS PV는 `docs/WBS.md` "EV 가중치 누적" 컬럼 기준.

---

## Day 1 — 2026-05-27

- **PV 5% / EV 5% / SPI 1.00**
- 회고: 사전검수 2회 (1차 일반, 2차 본문 인용 강제). agent 1차 출력을 의심해서 2차를 시킨 것 자체가 V&V 실천. scope를 4→6 모듈로 확장하기로 결정. 사전검수에 예상보다 1시간 더 소요
- 우회 횟수: 0회
- AI 출력 채택률: N/A (코드 0줄)

---

## Day 2 — 2026-05-28

- **PV 12% / EV 12% / SPI 1.00**
- 회고: 유스케이스 다이어그램 6개 + worst-case 시퀀스 5개 작성. Mermaid 정식 `usecaseDiagram` 미지원이라 `flowchart`로 흉내내는 방식 채택. 외부 분석 검토 후 포지셔닝 문서 분리(COMPETITIVE.md / FUTURE_WORK.md)
- 외부 분석 제안의 70% 채택, 30% 거절 (engineering governance platform 같은 과도 표현은 12일 prototype에 부적합으로 제외)
- 우회 횟수: 0회
- AI 출력 채택률: 다이어그램 한 번 손봐서 채택. Mermaid 렌더링 실제 확인은 GitHub push 후

---

## Day 3 (일부 선행) — 2026-05-28 저녁

> 본래 Day 3는 5/29 예정. 5/28에 일부 선행 진행. 5/29에 잔여(Hook PoC + 어조 보완) 마무리

- **PV 20% / EV 추정 18% / SPI ≈ 0.90**
  (Hook PoC 미완분 -2%. 정량 측정이 아닌 추정치)
- 회고: ARCHITECTURE.md + INTERFACES.md 완성
  - Hybrid (orchestration: 핵심 4 / choreography: 보조 2) 결정
  - SQLite 스키마 9개 테이블, CLI 명령 체계, application boundary, worst-case 대응 매핑
  - Python `Protocol` 기반 4 트랙 인터페이스 명세
- 작업 도중 socket 끊김 1회 발생. ARCHITECTURE를 한 Write로 통째 만들려다 응답이 너무 커서 끊김. 분할 작성으로 해결. **교훈**: 한 번에 1500+ 단어 Write는 안전 한계
- Hook PoC는 의도적 연기. 시스템 설정 변경이라 다음 날 진행
- 어조 검수 결과 전면 보완 필요한 상황 발견. 같은 5/28에 어조 정리 작업 추가 진행
- 우회 횟수: 0회
- AI 출력 채택률: 다이어그램·코드 인터페이스 한 번씩 검수해서 채택. SQLite 스키마는 구현 단계 실제 SQL 돌려보며 또 수정 예상
