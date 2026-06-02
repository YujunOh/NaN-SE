import { api } from "../api";
import { useFetch } from "../useFetch";
import LocChip from "./LocChip";

const sevClass = (s: number) =>
  s >= 7 ? "sev-high" : s >= 4 ? "sev-mid" : "sev-low";

export default function Findings({
  principleFilter = null,
  onClearFilter,
  onExplain,
}: {
  principleFilter?: string | null;
  onClearFilter?: () => void;
  onExplain?: () => void;
}) {
  const { data, error, loading } = useFetch(() => api.findings());

  if (loading) return <p className="muted">불러오는 중입니다...</p>;
  if (error) return <p className="error">API 연결에 실패했습니다: {error}</p>;
  if (!data || data.length === 0)
    return <p className="muted">검출된 finding이 없습니다. 'nanse learn'으로 카드를 생성해 보세요.</p>;

  const rows = principleFilter
    ? data.filter((f) => f.principle === principleFilter)
    : data;

  return (
    <div>
      <div className="table-toolbar">
        {principleFilter ? (
          <button className="filter-chip" onClick={onClearFilter}>
            원칙: {principleFilter} ✕
          </button>
        ) : (
          <span className="muted small">{data.length}개 finding</span>
        )}
        {onExplain && (
          <button className="link-btn" onClick={onExplain}>
            지표가 뭔가요?
          </button>
        )}
      </div>

      <table className="grid-table">
        <thead>
          <tr>
            <th>대상</th>
            <th>위치</th>
            <th>지표</th>
            <th>값 / 임계</th>
            <th>원칙</th>
            <th>심각도</th>
            <th>검출 시각</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((f) => (
            <tr key={f.id}>
              <td className="mono">{f.class_name}</td>
              <td>
                <LocChip file={f.source_file} line={f.source_line} />
              </td>
              <td>
                <span className="metric-tag">{f.metric}</span>
              </td>
              <td className="mono">
                {f.value} / {f.threshold}
              </td>
              <td>{f.principle}</td>
              <td>
                <span className={`badge ${sevClass(f.severity)}`}>{f.severity}</span>
              </td>
              <td className="muted">{f.created_at.replace("T", " ").slice(0, 19)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
