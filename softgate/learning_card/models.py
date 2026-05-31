"""학습 카드 데이터 모델 (Pydantic). 본인 구현 영역."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from softgate.principles import Principle


class LearningCard(BaseModel):
    # 식별
    id: str  # CARD-001
    session_id: str
    finding_id: int  # MetricFinding 식별자
    principle: Principle
    severity: int = Field(ge=0, le=10)
    code_hash: str

    # LLM이 채우는 자연어 콘텐츠 (채점 아님, 설명만)
    violation_reason: str
    cost_example: str
    before_code: str
    after_code: str
    learning_points: list[str]
    revision_prompt: str

    # 본인이 짠 검수 로직
    user_accepted: bool | None = None
    user_feedback: str | None = None

    # 메타
    generated_at: datetime
    reviewed_at: datetime | None = None
