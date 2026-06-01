import { useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api, type DocDetail } from "../api";
import { useFetch } from "../useFetch";

export default function DocModal({
  slug,
  onClose,
}: {
  slug: string;
  onClose: () => void;
}) {
  const { data, error, loading } = useFetch<DocDetail>(
    () => api.doc(slug),
    [slug],
  );

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
        className="modal doc-modal"
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
            <div className="doc-modal-head">
              <h2>{data.title}</h2>
              <a
                className="gh-link"
                href={data.github_url}
                target="_blank"
                rel="noreferrer"
              >
                GitHub에서 보기
              </a>
            </div>
            <article className="markdown">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {data.markdown}
              </ReactMarkdown>
            </article>
          </>
        )}
      </div>
    </div>
  );
}
