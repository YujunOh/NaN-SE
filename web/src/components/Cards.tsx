import { useEffect, useState } from "react";
import { api, type CardDetail, type CardSummary } from "../api";
import { useFetch } from "../useFetch";
import LocChip from "./LocChip";

const STATUSES = [
  { key: "all", label: "전체" },
  { key: "pending", label: "검수 대기" },
  { key: "accepted", label: "채택" },
  { key: "rejected", label: "거절" },
];

function reviewBadge(accepted: boolean | null) {
  if (accepted === null) return <span className="badge pending">검수 대기</span>;
  if (accepted) return <span className="badge accepted">채택</span>;
  return <span className="badge rejected">거절</span>;
}

function CardModal({ id, onClose }: { id: string; onClose: () => void }) {
  const { data, error, loading } = useFetch<CardDetail>(() => api.card(id), [id]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
      >
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>
        {loading && <p className="muted">불러오는 중...</p>}
        {error && <p className="error">{error}</p>}
        {data && (
          <>
            <h2>
              {data.id} · {data.principle} · 심각도 {data.severity}/10{" "}
              {reviewBadge(data.user_accepted)}
            </h2>
            <div className="modal-loc">
              <span className="muted small">위치</span>
              <LocChip file={data.source_file} line={data.source_line} />
            </div>
            <h4>위반 이유</h4>
            <p>{data.violation_reason}</p>
            <h4>운영 단계 비용</h4>
            <p>{data.cost_example}</p>
            <div className="code-cols">
              <div>
                <h4>Before</h4>
                <pre>{data.before_code}</pre>
              </div>
              <div>
                <h4>After</h4>
                <pre>{data.after_code}</pre>
              </div>
            </div>
            <h4>학습 포인트</h4>
            <ul>
              {data.learning_points.map((p, i) => (
                <li key={i}>{p}</li>
              ))}
            </ul>
            <h4>재요청 prompt</h4>
            <pre className="prompt">{data.revision_prompt}</pre>
            {data.user_feedback && (
              <>
                <h4>거절 사유</h4>
                <p className="muted">{data.user_feedback}</p>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default function Cards() {
  const [status, setStatus] = useState("all");
  const [openId, setOpenId] = useState<string | null>(null);
  const { data, error, loading } = useFetch<CardSummary[]>(
    () => api.cards(status),
    [status],
  );

  return (
    <div>
      <div className="filter-row">
        {STATUSES.map((s) => (
          <button
            key={s.key}
            className={`filter ${status === s.key ? "active" : ""}`}
            onClick={() => setStatus(s.key)}
          >
            {s.label}
          </button>
        ))}
      </div>

      {loading && <p className="muted">불러오는 중...</p>}
      {error && <p className="error">API 연결 실패: {error}</p>}
      {data && data.length === 0 && <p className="muted">해당 카드가 없다.</p>}

      <div className="card-grid">
        {data?.map((c) => (
          <div
            key={c.id}
            className="learning-card"
            role="button"
            tabIndex={0}
            onClick={() => setOpenId(c.id)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                setOpenId(c.id);
              }
            }}
          >
            <div className="learning-card-head">
              <span className="mono">{c.id}</span>
              {reviewBadge(c.user_accepted)}
            </div>
            <div className="learning-card-principle">{c.principle}</div>
            <p className="learning-card-reason">{c.violation_reason}</p>
            <div className="learning-card-foot">
              <span className="muted small">심각도 {c.severity}/10</span>
              <LocChip file={c.source_file} line={c.source_line} />
            </div>
          </div>
        ))}
      </div>

      {openId && <CardModal id={openId} onClose={() => setOpenId(null)} />}
    </div>
  );
}
