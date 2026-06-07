# NaN-SE 검출·설명 도구를 재현 가능한 컨테이너로 실행한다.
# 검출(analyze)·추적(trace)은 LLM 없이 돌고, 읽기 API(serve)는 대시보드에 데이터를 노출한다.
FROM python:3.12-slim

WORKDIR /app

# 의존성 레이어 캐시를 위해 메타데이터·패키지를 먼저 복사한 뒤 설치한다.
COPY pyproject.toml README.md ./
COPY nanse ./nanse
RUN pip install --no-cache-dir ".[api]"

# 컨테이너 안에서 데모(analyze/trace)를 바로 돌릴 수 있도록 예시·추적 명세도 포함.
COPY examples ./examples
COPY traceability.toml ./traceability.toml

# 읽기 API 포트
EXPOSE 8000

# 기본 동작은 읽기 API 서버. 검출은 `docker run --rm nanse nanse analyze <file>` 로.
CMD ["nanse", "serve", "--host", "0.0.0.0", "--port", "8000"]
