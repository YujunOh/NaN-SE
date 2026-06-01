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
  const stats = useFetch(() => api.stats());
  const docs = useFetch(() => api.docs());
  const [openSlug, setOpenSlug] = useState<string | null>(null);

  const findingCount = stats.data ? String(stats.data.total_findings) : "—";
  const cardCount = stats.data ? String(stats.data.total_cards) : "—";
  const rate =
    stats.data && stats.data.acceptance_rate !== null
      ? `${Math.round(stats.data.acceptance_rate * 100)}%`
      : "—";

  return (
    <div className="landing">
      <section className="hero">
        <div className="hero-badge">소프트웨어공학 과제 · prototype</div>
        <h1 className="hero-title">
          바이브코딩에 <span className="hl">공학 절차</span>를 끼워넣는다
        </h1>
        <p className="hero-lead">
          NaN-SE는 코드를 작성하는 시점에 결정론적 메트릭(LCOM4·순환복잡도)으로
          SRP·복잡도 위반을 검출하고, 확정된 위반만 LLM 학습 카드로 설명한다.
          검출과 설명을 분리해 채점의 흔들림을 없앴고, 채택·거절 같은 최종 판단은
          사람이 한다.
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
          <HeroStat value={findingCount} label="검출 finding" />
          <HeroStat value={cardCount} label="학습 카드" />
          <HeroStat value={rate} label="채택률" />
        </div>
      </section>

      <section className="pillars">
        <div className="pillar">
          <div className="pillar-tag det">검출</div>
          <h3>결정론적이라 흔들리지 않는다</h3>
          <p className="muted">
            LCOM4 연결 요소 수로 응집 결손(SRP)을, radon 순환복잡도로 분기 폭증을
            정적으로 측정한다. 같은 코드에 같은 결과.
          </p>
        </div>
        <div className="pillar">
          <div className="pillar-tag exp">설명</div>
          <h3>위반을 학습 기회로</h3>
          <p className="muted">
            확정된 위반만 LLM에 넘겨 위반 이유·운영 비용·교정 예시를 카드로 만든다.
            채점은 시키지 않는다.
          </p>
        </div>
        <div className="pillar">
          <div className="pillar-tag rev">검수</div>
          <h3>최종 판단은 사람</h3>
          <p className="muted">
            카드의 교정안을 채택할지 거절할지는 사용자가 CLI(nanse review)에서
            정한다. 도구는 단서만 만든다.
          </p>
        </div>
      </section>

      <section className="docs-section">
        <div className="panel-head">
          <h2>프로젝트 문서</h2>
          <span className="muted small">카드를 누르면 본문, GitHub 링크 별도</span>
        </div>
        {docs.loading && <p className="muted">문서 불러오는 중...</p>}
        {docs.error && <p className="error">문서 API 실패: {docs.error}</p>}
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
