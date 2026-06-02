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
      title="누르면 경로와 라인을 복사합니다"
    >
      {copied ? "복사됨" : label}
    </button>
  );
}
