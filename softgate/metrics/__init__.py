"""결정적 메트릭 검출 코어.

LLM 채점과 분리된 층. 같은 입력에 항상 같은 출력을 낸다.
"""

from softgate.metrics.lcom import ClassCohesion, compute_lcom4, analyze_source

__all__ = ["ClassCohesion", "compute_lcom4", "analyze_source"]
