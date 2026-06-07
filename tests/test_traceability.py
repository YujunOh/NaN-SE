"""요구 추적(Traceability) 최소 구현 테스트.

존재 검증과 gap 분류가 결정적으로 동작하는지 본다.
"""

from pathlib import Path

from nanse.traceability import build_matrix, gaps_only, load_spec


def _touch(root: Path, rel: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("x", encoding="utf-8")


def test_complete_when_code_and_test_exist(tmp_path: Path) -> None:
    _touch(tmp_path, "src/a.py")
    _touch(tmp_path, "tests/test_a.py")
    spec = {"UC-1": {"title": "기능", "code": ["src/a.py"], "test": ["tests/test_a.py"]}}
    rows = build_matrix(spec, tmp_path)
    assert rows[0].gap == "complete"
    assert rows[0].code_present == ["src/a.py"]
    assert rows[0].test_missing == []


def test_no_test_when_test_missing(tmp_path: Path) -> None:
    _touch(tmp_path, "src/a.py")
    spec = {"UC-1": {"title": "기능", "code": ["src/a.py"], "test": ["tests/test_a.py"]}}
    rows = build_matrix(spec, tmp_path)
    assert rows[0].gap == "no_test"
    assert rows[0].test_present == []


def test_no_code_when_code_missing(tmp_path: Path) -> None:
    _touch(tmp_path, "tests/test_a.py")
    spec = {"UC-1": {"title": "기능", "code": ["src/a.py"], "test": ["tests/test_a.py"]}}
    rows = build_matrix(spec, tmp_path)
    assert rows[0].gap == "no_code"
    assert rows[0].code_present == []


def test_gaps_only_filters_complete(tmp_path: Path) -> None:
    _touch(tmp_path, "src/a.py")
    _touch(tmp_path, "tests/test_a.py")
    _touch(tmp_path, "src/b.py")
    spec = {
        "UC-1": {"title": "ok", "code": ["src/a.py"], "test": ["tests/test_a.py"]},
        "UC-2": {"title": "gap", "code": ["src/b.py"], "test": ["tests/test_b.py"]},
    }
    rows = build_matrix(spec, tmp_path)
    only = gaps_only(rows)
    assert [r.req_id for r in only] == ["UC-2"]


def test_load_spec_from_toml(tmp_path: Path) -> None:
    spec_file = tmp_path / "trace.toml"
    spec_file.write_text(
        '[UC-9]\ntitle = "t"\ncode = ["x.py"]\ntest = ["test_x.py"]\n',
        encoding="utf-8",
    )
    spec = load_spec(spec_file)
    assert "UC-9" in spec
    assert spec["UC-9"]["code"] == ["x.py"]


def test_load_spec_default_when_missing(tmp_path: Path) -> None:
    spec = load_spec(tmp_path / "nope.toml")
    assert "UC-03" in spec  # 기본 매핑
