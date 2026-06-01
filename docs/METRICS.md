# Metrics: 검출 지표 (LCOM4 · 순환복잡도)

NaN-SE가 실제로 측정하는 지표는 둘이다. 클래스 응집도(LCOM4)와 함수 순환복잡도. 둘 다 결정론적 정적 분석이라 같은 코드를 넣으면 늘 같은 값이 나오고, LLM은 여기 관여하지 않는다. 값이 임계치를 넘은 곳을 finding으로 표시하고, 그 뒤 설명은 학습 카드(LLM)가 맡는다.

구현 위치: `nanse/metrics/lcom.py`, `nanse/metrics/complexity.py`, `nanse/metrics/findings.py`.

## 1. LCOM4 (클래스 응집도)

한 클래스의 메서드들이 같은 일을 향하는지 본다. 메서드를 점으로 두고, 같은 필드를 쓰거나 서로 호출하면 선으로 잇는다. 이 그래프에서 끊겨 있는 덩어리(연결 요소)의 개수가 LCOM4다.

- LCOM4 = 1: 모든 메서드가 한 덩어리. 응집된 클래스.
- LCOM4 ≥ 2: 서로 안 엮인 책임 덩어리가 둘 이상. 클래스가 여러 일을 동시에 한다는 신호.

임계치 1. LCOM4는 1이 이상적이라는 게 원 정의(Hitz & Montazeri)다. 2부터는 분리 가능한 책임으로 갈라졌다는 뜻이라, 1을 초과하면 SRP(단일 책임) 위반 의심으로 본다. 생성자 같은 dunder 메서드는 모든 필드를 건드려 응집을 인위적으로 높이므로 계산에서 뺀다.

매핑 원칙: Single Responsibility. 검출 시 `ast.ClassDef`의 `lineno`로 위치(source_file·source_line)를 함께 기록한다.

## 2. 순환복잡도 (Cyclomatic Complexity)

한 함수나 메서드 안에 독립적인 실행 경로가 몇 개인지 센다. if·elif·for·while·and·or 같은 분기마다 경로가 하나씩 늘어난다. 경로가 많을수록 테스트로 덮어야 할 경우의 수가 늘고, 한 곳을 고칠 때 영향 범위를 가늠하기 어렵다.

임계치 10. McCabe가 1976년 원 논문에서 모듈당 10을 권고했고, 이후 NIST 등 다수 가이드가 이 값을 그대로 쓴다. 10을 넘으면 테스트·유지보수 난도가 급격히 오른다는 경험적 기준이다. NaN-SE는 McCabe 구현을 재발명하지 않고 radon 라이브러리(`cc_visit`) 값을 그대로 쓴다.

매핑 원칙: Open-Closed. 결제수단·상태마다 if/elif가 쌓이면, 새 경우를 더할 때마다 그 메서드를 다시 열어야 하므로 확장에 닫혀 있다고 본다. radon block의 `lineno`로 위치를 기록한다.

## 3. 지표가 못 보는 것

두 지표는 구조를 본다. 런타임 행동은 못 본다.

- 동적 디스패치·런타임 결합: 정적으로 안 잡힌다.
- 결합도(Ca/Ce, Instability), LSP·ISP·DIP 위반: 검출하지 않는다. 기계적 판정이 어렵거나 확률적 채점이 필요한 영역이라 의도적으로 뺐다.
- LCOM4는 "분리가 필요하다"는 신호는 주지만 "이건 교환적 응집"처럼 응집 7단계 명칭을 붙이지는 않는다.

이 한계는 보고서에 그대로 적는다. 무엇을 못 보는지를 학습 카드가 따로 환기하기도 한다.

## 4. (원설계 기록) Function Point · Earned Value

피벗 전 SOLID Judge 시기 설계에는 IFPUG Function Point 카운터와 PMBOK Earned Value 추적기가 도구 모듈로 들어 있었다. Day 5 피벗에서 검출·설명 폐루프로 범위를 좁히며 둘 다 구현하지 않았다. 현재 `NaN-SE` 패키지에 `fp_counter`·`ev_tracker` 모듈도, `nanse fp`·`nanse wbs ev` 명령도 없다.

EV(SPI/CPI)는 이 과제 자체의 일정 관리 용도로만 `docs/WBS.md`에서 손계산으로 쓴다. 도구가 사용자 코드의 FP나 프로젝트 EV를 자동 계산한다고 보고서에 적지 않는다. FP/EV 표준 정의를 학습한 흔적은 WBS.md 일정 절에 남아 있다.
