"""LCOM4 계산기 단위 테스트.

INTERFACES.md의 4종 케이스 패턴을 따른다.
정상 입력, 잘못된 입력, 빈/없는 항목, 경계 동작.
"""

import ast

import pytest

from softgate.metrics import analyze_source, compute_lcom4
from softgate.metrics.lcom import ClassCohesion


COHESIVE = """
class Counter:
    def __init__(self):
        self.count = 0
    def increment(self):
        self.count += 1
    def reset(self):
        self.count = 0
    def value(self):
        return self.count
"""

GOD = """
class AuthService:
    def __init__(self):
        self.user = None
        self.smtp_host = "localhost"
        self.token_secret = "x"
    def login(self):
        self.user = "u"
    def logout(self):
        self.user = None
    def send_email(self):
        return self.smtp_host
    def issue_token(self):
        return self.token_secret
"""


def test_cohesive_class_has_lcom4_one():
    (result,) = analyze_source(COHESIVE)
    assert result.lcom4 == 1
    assert result.is_cohesive is True
    assert result.method_count == 3  # __init__ 제외


def test_god_class_splits_into_components():
    (result,) = analyze_source(GOD)
    assert result.lcom4 == 3
    assert result.is_cohesive is False
    assert ["login", "logout"] in result.components
    assert ["send_email"] in result.components
    assert ["issue_token"] in result.components


def test_method_call_connects_methods():
    src = """
class Service:
    def handle(self):
        return self.helper()
    def helper(self):
        return 1
"""
    (result,) = analyze_source(src)
    # 필드는 안 쓰지만 handle이 helper를 호출하므로 한 덩어리.
    assert result.lcom4 == 1


def test_staticmethod_is_excluded():
    src = """
class Util:
    @staticmethod
    def add(a, b):
        return a + b
    def use(self):
        return self.x
"""
    (result,) = analyze_source(src)
    assert result.method_count == 1  # add는 제외, use만


def test_class_without_methods():
    src = """
class Empty:
    pass
"""
    (result,) = analyze_source(src)
    assert result.lcom4 == 0
    assert result.method_count == 0


def test_invalid_source_raises():
    with pytest.raises(SyntaxError):
        analyze_source("def broken(:\n  pass")


def test_no_class_returns_empty():
    assert analyze_source("x = 1\n") == []


def test_compute_lcom4_returns_class_cohesion_type():
    tree = ast.parse(COHESIVE)
    class_node = tree.body[0]
    assert isinstance(class_node, ast.ClassDef)
    result = compute_lcom4(class_node)
    assert isinstance(result, ClassCohesion)
