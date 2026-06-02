export default function Metrics() {
  return (
    <div className="metrics-page">
      <p className="metrics-intro">
        NaN-SE의 검출층은 LLM 없이 두 가지 결정론적 지표만 봅니다. 같은 코드를 넣으면
        늘 같은 값이 나옵니다. 점수를 매기지 않고, 값이 임계치를 넘은 곳을 finding으로
        표시한 다음 설명(학습 카드)은 LLM에 맡깁니다.
      </p>

      <section className="metric-doc">
        <div className="metric-doc-head">
          <span className="metric-tag">lcom4</span>
          <h3>클래스 응집도 (LCOM4)</h3>
          <span className="badge pending">SRP</span>
        </div>
        <p>
          한 클래스 안의 메서드들이 같은 일을 향하는지 봅니다. 메서드를 점으로 두고,
          같은 필드를 쓰거나 서로 호출하면 선으로 잇는 그래프를 그린 뒤, 끊겨 있는
          덩어리(연결 요소)의 개수를 셉니다.
        </p>
        <ul className="metric-points">
          <li>
            <b>LCOM4 = 1</b> 이면 모든 메서드가 한 덩어리로 묶인 응집된 클래스입니다.
          </li>
          <li>
            <b>LCOM4 ≥ 2</b> 이면 서로 안 엮인 책임 덩어리가 둘 이상이고, 클래스가
            여러 일을 동시에 하고 있다는 신호입니다.
          </li>
        </ul>
        <div className="threshold-box">
          <div className="threshold-num">임계치 1</div>
          <p>
            LCOM4는 1이 이상적이라는 것이 원 정의(Hitz &amp; Montazeri)입니다. 2부터는
            한 클래스가 분리 가능한 책임으로 갈라졌다는 뜻이라, 1을 초과하면 SRP(단일
            책임) 위반 의심으로 봅니다. 생성자 같은 dunder 메서드는 모든 필드를 건드려
            응집을 인위적으로 높이므로 계산에서 뺍니다.
          </p>
        </div>
      </section>

      <section className="metric-doc">
        <div className="metric-doc-head">
          <span className="metric-tag">cyclomatic</span>
          <h3>순환복잡도 (Cyclomatic Complexity)</h3>
          <span className="badge pending">OCP</span>
        </div>
        <p>
          한 함수나 메서드 안에 독립적인 실행 경로가 몇 개인지 셉니다. if, elif, for,
          while, and, or 같은 분기마다 경로가 하나씩 늘어납니다. 경로가 많을수록
          테스트로 덮어야 할 경우의 수가 늘고, 한 곳을 고칠 때 영향 범위를 가늠하기
          어렵습니다.
        </p>
        <ul className="metric-points">
          <li>분기 없는 직선 함수는 복잡도가 1입니다.</li>
          <li>
            결제수단이나 상태마다 if, elif가 쌓이면 복잡도가 빠르게 오릅니다. 새 경우를
            더할 때마다 그 메서드를 다시 열어야 하므로 OCP(확장에 열고 변경에 닫는다)
            위반 신호로 봅니다.
          </li>
        </ul>
        <div className="threshold-box">
          <div className="threshold-num">임계치 10</div>
          <p>
            McCabe가 1976년 원 논문에서 모듈당 10을 권고했고, 이후 NIST 등 다수 가이드가
            이 값을 그대로 씁니다. 10을 넘으면 테스트와 유지보수 난도가 급격히
            올라간다는 경험적 기준입니다. NaN-SE는 McCabe 구현을 재발명하지 않고 radon
            라이브러리 값을 그대로 씁니다.
          </p>
        </div>
      </section>

      <p className="metrics-foot muted small">
        임계치는 교과서와 표준 권고를 초기값으로 둔 값이라, 프로젝트 벤치마크가 쌓이면
        조정합니다. 지표가 무엇을 못 보는지(예: 동적 디스패치, 런타임 결합)는 설명
        카드에서 따로 다룹니다.
      </p>
    </div>
  );
}
