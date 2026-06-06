import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api";
import { useFetch } from "../useFetch";

const SEV_COLOR = (s: number) =>
  s >= 7 ? "#e5484d" : s >= 4 ? "#f5a623" : "#30a46c";

const SHORT_PRINCIPLE: Record<string, string> = {
  "Single Responsibility": "SRP",
  "Open-Closed": "OCP",
  "Liskov Substitution": "LSP",
  "Interface Segregation": "ISP",
  "Dependency Inversion": "DIP",
};

const shorten = (p: string) => SHORT_PRINCIPLE[p] ?? p;

const GRID = "#e2e6ee";
const AXIS = "#66707e";
const tickStyle = { fontSize: 11, fill: AXIS };

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="stat-card">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

export default function Overview({
  onPrincipleSelect,
}: {
  onPrincipleSelect?: (principle: string | null) => void;
}) {
  const { data, error, loading } = useFetch(() => api.stats());

  if (loading) return <p className="muted">불러오는 중입니다...</p>;
  if (error) return <p className="error">API 연결에 실패했습니다: {error}</p>;
  if (!data) return null;

  const principles = data.by_principle.map((d) => shorten(d.principle));
  const principleLabel = principles.length ? principles.join(" · ") : "—";

  const topPrinciple = [...data.by_principle].sort(
    (a, b) => b.count - a.count,
  )[0];
  const topPrincipleLabel = topPrinciple
    ? `${shorten(topPrinciple.principle)} (${topPrinciple.count})`
    : "—";

  const sevTotal = data.by_severity.reduce((s, d) => s + d.count, 0);
  const sevWeighted = data.by_severity.reduce(
    (s, d) => s + d.severity * d.count,
    0,
  );
  const avgSeverity =
    sevTotal > 0 ? `${(sevWeighted / sevTotal).toFixed(1)} / 10` : "—";

  return (
    <div>
      <p className="muted small" style={{ marginBottom: 12 }}>
        아래 수치는 <code>nanse seed-demo</code>로 채운 예시 데이터다. 실제
        분석은 <code>nanse analyze</code>로 채운다.
      </p>
      <div className="stat-row">
        <StatCard label="검출 finding (임계 초과)" value={String(data.total_findings)} />
        <StatCard label="검출된 원칙" value={principleLabel} />
        <StatCard label="가장 잦은 위반" value={topPrincipleLabel} />
        <StatCard label="평균 심각도" value={avgSeverity} />
      </div>

      <div className="chart-grid">
        <section className="panel">
          <div className="panel-head">
            <h3>원칙별 finding</h3>
            <span className="muted small">막대를 누르면 해당 원칙의 Findings로 이동합니다</span>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.by_principle}>
              <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
              <XAxis dataKey="principle" tick={tickStyle} stroke={GRID} />
              <YAxis allowDecimals={false} tick={tickStyle} stroke={GRID} />
              <Tooltip cursor={{ fill: "rgba(53,103,224,0.07)" }} />
              <Bar
                dataKey="count"
                fill="#3567e0"
                radius={[4, 4, 0, 0]}
                cursor="pointer"
                onClick={(d: { principle?: string }) =>
                  onPrincipleSelect?.(d?.principle ?? null)
                }
              />
            </BarChart>
          </ResponsiveContainer>
        </section>

        <section className="panel">
          <h3>심각도 분포</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.by_severity}>
              <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
              <XAxis dataKey="severity" tick={tickStyle} stroke={GRID} />
              <YAxis allowDecimals={false} tick={tickStyle} stroke={GRID} />
              <Tooltip />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {data.by_severity.map((d) => (
                  <Cell key={d.severity} fill={SEV_COLOR(d.severity)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </section>

        <section className="panel wide">
          <h3>카드 생성 추이</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={data.cards_over_time}>
              <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
              <XAxis dataKey="date" tick={tickStyle} stroke={GRID} />
              <YAxis allowDecimals={false} tick={tickStyle} stroke={GRID} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#3567e0"
                strokeWidth={2}
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </section>
      </div>
    </div>
  );
}
