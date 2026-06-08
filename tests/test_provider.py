"""LLM provider 선택 로직 테스트.

검출은 LLM과 무관하므로 여기서 검증하는 건 설명층 provider 라우팅뿐이다.
실제 네트워크 호출 없이, 두 어댑터를 가짜로 바꿔치기해 default_complete가
환경변수에 따라 올바른 쪽을 부르는지만 본다.
"""

import nanse.learning_card.generator as g


def _patch(monkeypatch):
    monkeypatch.setattr(g, "_anthropic_complete", lambda p: "ANTHROPIC")
    monkeypatch.setattr(g, "_gemini_complete", lambda p: "GEMINI")


def test_explicit_gemini(monkeypatch):
    _patch(monkeypatch)
    monkeypatch.setenv("NANSE_LLM", "gemini")
    assert g.default_complete("x") == "GEMINI"


def test_explicit_anthropic(monkeypatch):
    _patch(monkeypatch)
    monkeypatch.setenv("NANSE_LLM", "anthropic")
    monkeypatch.setenv("GEMINI_API_KEY", "k")  # 명시값이 우선한다
    assert g.default_complete("x") == "ANTHROPIC"


def test_infer_gemini_when_only_gemini_key(monkeypatch):
    _patch(monkeypatch)
    monkeypatch.delenv("NANSE_LLM", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    assert g.default_complete("x") == "GEMINI"


def test_default_anthropic(monkeypatch):
    _patch(monkeypatch)
    monkeypatch.delenv("NANSE_LLM", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    assert g.default_complete("x") == "ANTHROPIC"
