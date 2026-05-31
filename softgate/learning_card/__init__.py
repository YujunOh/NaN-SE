"""학습 카드 시스템 — 설명층.

메트릭 검출(결정적)이 finding을 올리면, 여기서 LLM이 자연어 설명만 채운다.
채점은 이미 끝났다. LLM은 판정하지 않는다.
"""

from softgate.learning_card.models import LearningCard
from softgate.learning_card.generator import generate_card

__all__ = ["LearningCard", "generate_card"]
