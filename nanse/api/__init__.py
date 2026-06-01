"""읽기 전용 REST API (FastAPI). 검출·설명 결과를 대시보드에 노출한다.

검수(채택/거절)는 CLI에 남긴다. 여기서는 읽기만 한다.
"""

from nanse.api.app import create_app

__all__ = ["create_app"]
