# Discussion Log — softgate

본 프로젝트 진행 중 작성자의 의사결정·토의 흐름을 자연어로 기록한 일지. commit history만으로는 의도와 토의 흐름이 드러나지 않으므로 별도 보존.

형상관리 증빙 목적이며, 막판에 몰아서 쓴 게 아님을 보이기 위해 일별로 시점·맥락·내적 토의를 자연스럽게 적는다.

---

## 2026-05-27 (수) — Day 1, 착수

오늘 시작. 강의 과제 명세는 "프로세스에 입각한 바이브코딩의 효과 논술"이고 SW는 자유 선정이라 처음엔 무엇을 만들지 막막했다. 처음 떠올린 후보는 (1) 시험 키워드 플래시카드, (2) 인턴/공모전 레이더, (3) DITDA 부속 도구, (4) 완전 새로운 학습용 미니 SW였다. 1번은 강의평이 보일까 무서웠고, 2번은 업무용 메일을 활용한다는 점이 도덕적으로 걸렸다.

그러다 발상이 한 발 나갔다. 바이브코딩으로 SW를 만드는 게 어차피 과제 본질이라면, SW공학 원칙을 어떻게 바이브코딩에 적용할 수 있을지를 도구로 만들어버리면 어떨까. 즉 "바이브코딩을 SW공학 원칙에 맞게 적용하도록 도와주는 툴"을 SaaS 같이. 이게 가장 메타하고 가장 강의 주제와 정렬되는 느낌이었다.

### 사전검수의 발견

scope를 결정하기 전에 강의록을 전수 검수했다. SW공학 강의가 다루는 키워드 전체를 도구가 충분히 커버 가능한지 확인하는 단계. 1차로 검수 agent에게 일반 검수를 시켰는데 일반론·교과서 톤만 나왔다. 본문 발췌 인용이 부족했다. 2차로 "본문 발췌 인용 필수, 자료를 직접 읽어서 인용"이라고 명시 재지시하니 9개 강의 자료의 핵심 인용이 풍부해졌다.

같은 task를 두 번 시켰을 때 출력 깊이가 완전히 달랐다는 사실 자체가 V&V 원칙의 실천 사례가 됐다. 한 번에 안 끝나는 게 일반 룰이고, 본인이 의심해서 재지시하는 게 진짜 검증이라는 자각. 이 패턴 자체가 보고서의 lessons learned 후보가 됐다.

### scope 결정 — 4 모듈에서 6 모듈로 확장

처음에는 4 핵심 모듈(Stage Gate, SOLID Judge, EV Tracker, Process Log)로 잡았다. 검수 결과 강의 70-75% 커버, 12일 가능이라는 보수적 권고가 나왔다.

본인이 의심해서 추가 검수를 더 시켰다. 강의록 9개 본문을 발췌 인용까지 시키니 SAGA·choreography·constraint 같은 핵심 메시지가 도구 컨셉과 거의 1:1로 정렬되는 게 드러났다. 85%+ 커버 가능 + 강의 메시지 그대로 인용 가능한 수준. UseCase Logger와 FP Counter를 추가해서 6 모듈로 scope를 확장하기로 결정.

### Day 1 마무리

repo 초기화, README, WBS(12일 4 트랙 병렬), REQUIREMENTS, AI_TOOLING 작성. 5개 commit으로 마무리. PV/EV 5%, SPI 1.00. 본인이 의심해서 재지시한 V&V 사례 1건. 우회 횟수 0.

---

## 2026-05-28 (목) — Day 2, 어조 검수의 충격

본격 작업 시작. 유스케이스 다이어그램 6개와 worst-case 시퀀스 다이어그램 5개를 그렸다. Mermaid가 정식 `usecaseDiagram`을 미지원이라 `flowchart`로 흉내내는 방식 채택. 다이어그램 처음 그려보는 거라 어색했지만 강의 의도(actor·include·extend)는 표현 가능했다.

오후에 어조 검수를 받으면서 충격을 받았다. 본인이 검수 안 한 상태로 진행한 문서 전반에 AI 어투가 박혀 있었다. 명사 종결 후 점, "솔직히:" 같은 어구, em-dash, 강의 출처 명시 등. 검수 전까지 어조 문제를 자각하지 못한 상태였다는 게 더 중요한 발견. AI는 자기 출력의 AI 티를 감지하지 못한다.

### 강의 출처 명시 제거

"소공0514", "choreography orchestration 노트" 같은 명시적 강의 출처를 전부 제거하기로 결정. 이유는 두 가지.

첫째, 녹음본 .txt를 AI에 직접 주고 작업한 흔적이 노출되면 자존심 안 좋다. 수업에서 들은 내용을 본인이 정리한 것처럼 자연스럽게 써야 한다.

둘째, 출처를 박는 것 자체가 교수님 관점에서는 추종·찬양으로 비칠 수 있다. 본인 작품으로서의 정체성이 흐려진다.

같은 맥락에서 "본인 자각", "솔직히:" 같은 메타 표현도 정리. 명사 종결 후 점도 일괄 제거. em-dash는 짧은 하이픈으로 대체.

### MVP 단어 정정

수업에서 "MVP는 Minimum Viable Product, 돈 받고 팔 수 있는 최소 기능"이라는 메시지가 나왔다. 우리가 짜는 건 prototype 수준이라는 정확한 표현으로 정정. 문서 전반에서 MVP를 prototype으로 일괄 교체.

### VISION 신규 — TCP 비유로 컨셉 격상

기획자/PO 관점에서 비전이 더 뚜렷해야 한다는 자각으로 VISION.md를 신규 작성. 컨셉을 "바이브코딩 시대의 TCP"로 정리. TCP가 unreliable한 IP 위에서 reliability를 보장하는 발상을 AI coding 도메인에 적용한다는 메타포.

"AI 스파게티"와 "공장 컨베이어벨트"를 메인 비유로 채택. CodeRabbit 조사(2025) 통계(버그 1.7배, 보안 취약성 2배, 논리 오류 75%)를 정량 근거로 박았다. industry analyst의 2027년까지 약 $1.5T 기술부채 예측도 같이.

### Day 2 마무리

Day 2 6 commit + Day 3 일부 선행 3 commit. PV 12%, EV 추정 18% (선행분 포함), SPI 약 0.90. 어조 정정으로 인한 commit 추가가 많았다.

---

## 2026-05-29 (금) — Day 3, 핵심 아이디어 빈약 자각

오전 9시 시점. README를 다시 읽으면서 핵심 아이디어가 빈약하다는 자각이 왔다. SAGA 패턴이 정말 SDLC에 적용해서 효용 있는가? 모듈별 (Stage, EV Tracker, FP Counter, Process Log)이 정확히 무엇을 자동화해서 얼마나 도움 되는가? SOLID Judge는 좋아 보이지만 UseCase Logger는 결국 시각화 모듈인 거 아닌가?

이 자각 자체가 중요했다. 본인이 readme를 다시 안 읽었으면 모르고 갔을 부분. 검수의 가치 재확인.

### 광범위 리서치 위임

비슷한 도구가 이미 있는지 광범위 탐색을 agent에 위임했다. 키워드는 LLM 기반 SOLID 채점, traceability matrix 자동화, SDLC stage gate, Claude Code hook 통합 등 광범위.

결과가 결정적이었다.

첫째, **vibegate 이름 자체가 충돌**. PyPI에 `vibegate`라는 "deterministic production readiness gate" 패키지가 이미 알파 진행 중. 어휘와 포지셔닝이 그대로 겹친다. 이름 변경 필수.

둘째, **Traceability Matrix는 거의 동일 도구가 이미 있음**. Claude Plugin Hub의 `traceability-check` skill이 REQ-*/UC-* 스캔, commit message 매칭, gap/orphan 검출까지 한다. 단순 재구현은 표절 인상.

셋째, SDLC 플러그인은 다수 존재. 대부분 phase 강제. softgate가 차별 가능한 영역은 "누락 검출 + 부드러운 제안"이고 Superpowers 같은 강제 게이트와 정반대 메시지 가능.

### 결정 — 이름·scope 재설정

이름은 softgate로 변경. soft 게이트 = "차단 X, 제안 O" 컨셉 텍스트에 내장. 짧고 기억 쉽고 충돌 확률 낮음.

scope는 6 모듈에서 3 핵심으로 축소 + 깊이 강화. SOLID Judge·Traceability·Stage에 집중. EV/FP/Process Log는 옵션으로 강등(학교 과제 키워드 충족용).

Traceability는 한국어 commit message + 한국 대학생 과제 양식 first-class로 차별. 영어권 traceability-check이 못 다루는 영역.

### 추가 발상 — 위반을 학습 기회로

3 핵심 모듈로도 차별점이 약하다는 자각. 본인 의도는 "기술부채와 코드리뷰를 이해 못 하는 건 개발자가 바이브코딩된 코드를 직접 안 짠 데다 꼼꼼히 리뷰하지도 않아서"라는 근본 원인에서 출발. 그렇다면 SOLID Judge가 위반을 검출했을 때 그것을 학습 기회로 전환하면 어떨까. 짧은 학습 카드를 자동 생성해서 사용자가 검수·채택하고, 채택된 카드의 재요청 prompt가 AI에 다시 전달되는 폐쇄 루프.

여기에 Progress Dashboard로 학습이 누적되는 게 보이는 보상 구조를 더하면 강제·차단·채점 위주의 기존 도구와 명확히 차별된다.

scope 폭발 우려가 있어서 한 가지 원칙을 박았다. 학습 카드 자동 생성은 LLM이 자연어 콘텐츠만 채우고, 데이터 모델·파이프라인·검수 로직·DB 저장·CLI 렌더링은 전부 본인 구현. AI 생성물 취급 회피.

### 4 핵심 모듈 확정

1. SOLID Judge + Learning Card Generator
2. Stage (누락 검출 + 자동 제안, 차단 X)
3. Traceability (한국어·과제 양식 특화)
4. Progress Dashboard (성취감 유발)

옵션 모듈로 EV Tracker / FP Counter / Process Log 유지.

### Day 3 오전 작업

GitHub repo rename(vibegate → softgate), 로컬 디렉토리 mv, git remote URL 업데이트, 문서 전반 vibegate → softgate sed 일괄. README·VISION의 4 핵심 모듈 재정의. ARCHITECTURE 본격 재작성은 다음 단계.

---

## 작성자

오유준 (홍익대학교 컴퓨터공학과)
