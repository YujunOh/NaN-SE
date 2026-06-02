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

  const rate =
    data.acceptance_rate === null
      ? "—"
      : `${Math.round(data.acceptance_rate * 100)}%`;

  return (
    <div>
      <div className="stat-row">
        <StatCard label="검출 finding" value={String(data.total_findings)} />
        <StatCard label="학습 카드" value={String(data.total_cards)} />
        <StatCard label="검수 대기" value={String(data.review.pending)} />
        <StatCard label="채택률" value={rate} />
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
