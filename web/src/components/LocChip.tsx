import { useState } from "react";

export default function LocChip({
  file,
  line,
}: {
  file: string | null;
  line: number | null;
}) {
  const [copied, setCopied] = useState(false);

  if (!file) return <span className="muted small">위치 미상</span>;

  const label = line ? `${file}:${line}` : file;

  const copy = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard?.writeText(label).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    });
  };

  return (
    <button
      className="loc-chip mono"
      onClick={copy}
      title="클릭하면 경로:라인 복사"
    >
      {copied ? "복사됨" : label}
    </button>
  );
}
