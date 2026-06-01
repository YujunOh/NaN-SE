"""순환복잡도 검출 테스트."""

from nanse.metrics.complexity import analyze_complexity, findings_from_complexity
from nanse.principles import Principle

COMPLEX = """
class Router:
    def route(self, x, y, z, w):
        if x:
            if y:
                if z:
                    if w:
                        return 1
                    return 2
                return 3
            return 4
        if y and z:
            return 5
        if w or x:
            return 6
        for i in range(10):
            if i % 2:
                return i
        return 0
"""

SIMPLE = """
class Calc:
    def add(self, a, b):
        return a + b
"""


def test_complex_method_flagged():
    findings = findings_from_complexity(COMPLEX, "src/router.py")
    assert len(findings) == 1
    assert findings[0].metric == "cyclomatic"
    assert findings[0].principle is Principle.OCP
    assert "Router.route" in findings[0].class_name
    assert findings[0].value > 10
    assert findings[0].source_file == "src/router.py"
    assert findings[0].source_line == 3


def test_simple_method_not_flagged():
    assert findings_from_complexity(SIMPLE) == []


def test_analyze_complexity_lists_methods():
    results = analyze_complexity(SIMPLE)
    assert len(results) == 1
    assert results[0].name == "add"
    assert results[0].classname == "Calc"
