import { useState } from "react";
import { api } from "../api";
import { useFetch } from "../useFetch";
import DocModal from "./DocModal";

function HeroStat({ value, label }: { value: string; label: string }) {
  return (
    <div className="hero-stat">
      <div className="hero-stat-value">{value}</div>
      <div className="hero-stat-label">{label}</div>
    </div>
  );
}

export default function Landing({
  onEnter,
}: {
  onEnter?: (tab: "overview" | "findings" | "cards" | "metrics") => void;
}) {
  const docs = useFetch(() => api.docs());
  const [openSlug, setOpenSlug] = useState<string | null>(null);

  return (
    <div className="landing">
      <section className="hero">
        <div className="hero-main">
          <div className="hero-badge">소프트웨어공학 과제 · prototype</div>
          <h1 className="hero-title">
            바이브코딩에도 <span className="hl">SW공학 원칙</span>을 지킵니다
          </h1>
          <p className="hero-lead">
            NaN-SE는 코드를 짜는 동안 결정론적 메트릭(LCOM4, 순환복잡도)으로 SRP와
            복잡도 위반을 찾아내고, 확정된 위반만 LLM 학습 카드로 설명합니다. 검출과
            설명을 분리해 채점이 흔들릴 여지를 없앴습니다. 채택할지 거절할지 같은
            최종 판단은 사람이 합니다.
          </p>
          <div className="hero-actions">
            <button className="cta" onClick={() => onEnter?.("overview")}>
              대시보드 열기
            </button>
            <button className="cta ghost" onClick={() => onEnter?.("cards")}>
              학습 카드 보기
            </button>
          </div>
          <div className="hero-stats">
            <HeroStat value="2" label="검출 지표 (LCOM4·복잡도)" />
            <HeroStat value="33" label="통과 테스트" />
            <HeroStat value="0" label="검출에 쓰는 LLM" />
          </div>
        </div>
        <aside className="hero-term" aria-hidden="true">
          <div className="term-bar">
            <span />
            <span />
            <span />
            <em>nanse review</em>
          </div>
          <div className="term-body mono">
            <div className="t-line">
              <span className="t-cmd">$ nanse analyze</span>
            </div>
            <div className="t-line">
              <span className="t-path">auth_service.py:12</span>{" "}
              <span className="t-dim">LCOM4=3 &gt; 1</span>{" "}
              <span className="t-warn">SRP</span>
            </div>
            <div className="t-line">
              <span className="t-path">order_router.py:48</span>{" "}
              <span className="t-dim">복잡도=14 &gt; 10</span>{" "}
              <span className="t-warn">OCP</span>
            </div>
            <div className="t-line t-gap">
              <span className="t-cmd">$ nanse learn</span>
            </div>
            <div className="t-line">
              <span className="t-ok">학습 카드 2장 생성</span>
            </div>
            <div className="t-line t-gap">
              <span className="t-cmd">$ nanse review</span>
            </div>
            <div className="t-line">
              <span className="t-dim">[A]ccept [R]eject</span>{" "}
              <span className="t-cursor">▋</span>
            </div>
          </div>
        </aside>
      </section>

      <section className="pillars">
        <div className="pillar">
          <div className="pillar-tag det">검출</div>
          <h3>결정론적이라 흔들리지 않습니다</h3>
          <p className="muted">
            LCOM4의 연결 요소 수로 응집 결손을, radon 순환복잡도로 분기 폭증을
            정적으로 측정합니다. 응집이 갈라지면 SRP 위반, 분기가 폭증하면 OCP
            위반을 의심합니다. 같은 코드에는 같은 결과가 나옵니다.
          </p>
        </div>
        <div className="pillar">
          <div className="pillar-tag exp">설명</div>
          <h3>위반을 학습 기회로</h3>
          <p className="muted">
            확정된 위반만 LLM에 넘겨 위반 이유와 운영 비용, 교정 예시를 카드로
            만듭니다. 채점은 시키지 않습니다.
          </p>
        </div>
        <div className="pillar">
          <div className="pillar-tag rev">검수</div>
          <h3>최종 판단은 사람</h3>
          <p className="muted">
            카드의 교정안을 채택할지 거절할지는 사용자가 CLI(nanse review)에서
            정합니다. 도구는 단서만 만듭니다.
          </p>
        </div>
      </section>

      <section className="docs-section">
        <div className="panel-head">
          <h2>프로젝트 문서</h2>
          <span className="muted small">카드를 누르면 본문이 열리고, GitHub 링크는 따로 있습니다</span>
        </div>
        {docs.loading && <p className="muted">문서를 불러오는 중입니다...</p>}
        {docs.error && <p className="error">문서 API 호출이 실패했습니다: {docs.error}</p>}
        {docs.data?.groups.map((g) => (
          <div key={g.name} className="doc-group">
            <h3 className="doc-group-name">{g.name}</h3>
            <div className="doc-grid">
              {g.docs.map((d) => (
                <div
                  key={d.slug}
                  className="doc-card"
                  role="button"
                  tabIndex={0}
                  onClick={() => setOpenSlug(d.slug)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setOpenSlug(d.slug);
                    }
                  }}
                >
                  <div className="doc-card-slug mono">{d.slug}.md</div>
                  <div className="doc-card-title">{d.title}</div>
                  <p className="doc-card-blurb muted small">{d.blurb}</p>
                  <a
                    className="doc-card-gh small"
                    href={d.github_url}
                    target="_blank"
                    rel="noreferrer"
                    onClick={(e) => e.stopPropagation()}
                  >
                    GitHub
                  </a>
                </div>
              ))}
            </div>
          </div>
        ))}
      </section>

      {openSlug && (
        <DocModal slug={openSlug} onClose={() => setOpenSlug(null)} />
      )}
    </div>
  );
}
