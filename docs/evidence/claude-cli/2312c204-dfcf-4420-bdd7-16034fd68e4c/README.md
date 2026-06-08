# Claude CLI 원문 세션 sync

- 세션 ID: `2312c204-dfcf-4420-bdd7-16034fd68e4c`
- 원본 위치: `C:\Users\dbwns\.claude\projects\C--Users-dbwns\...`
- sync 방식: 원본 JSONL의 줄 구조를 유지하되, 실제 API key처럼 보이는 값만 `[REDACTED_SECRET]`로 치환했습니다.
- 원본 무결성 확인용 SHA256, 라인 수, redaction 횟수는 `manifest.json`에 남겼습니다.
- Claude JSONL 안에서는 `HANDOFF_VERIFICATION.md`/`cap-handoff.png` exact 문자열은 확인되지 않았고, NaN-SE 개발·보고서 검수 세션(`docs/REPORT.md`, `README.md`, CI/캡처 검수)이 이 세션 묶음에 남아 있습니다.

## 파일 수

- 부모 세션 JSONL: 1개
- subagent JSONL: 17개
- 총 JSONL: 18개

## 주의

원본 파일은 사용자 홈의 `.claude` 아래에 그대로 두고 수정하지 않았습니다. 저장소에는 보안 마스킹된 sync본만 둡니다.
