import { useState } from "react";
import Overview from "./components/Overview";
import Findings from "./components/Findings";
import Cards from "./components/Cards";
import Metrics from "./components/Metrics";

const TABS = [
  { key: "overview", label: "개요" },
  { key: "findings", label: "Findings" },
  { key: "cards", label: "학습 카드" },
  { key: "metrics", label: "지표 설명" },
] as const;

type TabKey = (typeof TABS)[number]["key"];

export default function App() {
  const [tab, setTab] = useState<TabKey>("overview");
  const [principleFilter, setPrincipleFilter] = useState<string | null>(null);

  const openFindings = (principle: string | null) => {
    setPrincipleFilter(principle);
    setTab("findings");
  };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          softgate <span className="brand-sub">dashboard</span>
        </div>
        <nav className="tabs">
          {TABS.map((t) => (
            <button
              key={t.key}
              className={`tab ${tab === t.key ? "active" : ""}`}
              onClick={() => setTab(t.key)}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>

      <main className="content">
        {tab === "overview" && <Overview onPrincipleSelect={openFindings} />}
        {tab === "findings" && (
          <Findings
            principleFilter={principleFilter}
            onClearFilter={() => setPrincipleFilter(null)}
            onExplain={() => setTab("metrics")}
          />
        )}
        {tab === "cards" && <Cards />}
        {tab === "metrics" && <Metrics />}
      </main>

      <footer className="foot muted small">
        검출은 결정론적 메트릭, 설명은 LLM. 검수(채택/거절)는 CLI(softgate review)에서.
      </footer>
    </div>
  );
}
