"""LCOM4 (Lack of Cohesion of Methods) 계산.

LCOM4는 클래스 내부를 그래프로 본다. 노드는 메서드. 두 메서드가
같은 인스턴스 필드를 쓰거나 한쪽이 다른 쪽을 호출하면 간선을 잇는다.
연결 요소(connected component)의 개수가 LCOM4 값이다.

LCOM4 == 1 이면 응집된 클래스. >= 2 이면 클래스가 서로 무관한
책임 덩어리로 쪼개져 있다는 신호이고, SRP 위반 의심 근거가 된다.

이 모듈은 LLM을 호출하지 않는다. 같은 소스를 넣으면 항상 같은 값이 나온다.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field


@dataclass
class ClassCohesion:
    """한 클래스의 LCOM4 측정 결과."""

    class_name: str
    method_count: int
    field_count: int
    lcom4: int
    line: int = 1
    components: list[list[str]] = field(default_factory=list)

    @property
    def is_cohesive(self) -> bool:
        return self.lcom4 <= 1


class _MethodScanner(ast.NodeVisitor):
    """한 메서드 본문에서 self 필드 접근과 self 메서드 호출을 수집."""

    def __init__(self, self_name: str) -> None:
        self.self_name = self_name
        self.fields: set[str] = set()
        self.calls: set[str] = set()

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name) and node.value.id == self.self_name:
            parent = getattr(node, "_softgate_parent", None)
            if isinstance(parent, ast.Call) and parent.func is node:
                self.calls.add(node.attr)
            else:
                self.fields.add(node.attr)
        self.generic_visit(node)


class _UnionFind:
    def __init__(self, items: list[str]) -> None:
        self._parent = {item: item for item in items}

    def find(self, x: str) -> str:
        root = x
        while self._parent[root] != root:
            root = self._parent[root]
        while self._parent[x] != root:
            self._parent[x], x = root, self._parent[x]
        return root

    def union(self, a: str, b: str) -> None:
        self._parent[self.find(a)] = self.find(b)

    def groups(self) -> list[list[str]]:
        buckets: dict[str, list[str]] = {}
        for item in self._parent:
            buckets.setdefault(self.find(item), []).append(item)
        return [sorted(members) for members in buckets.values()]


def _self_param_name(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str | None:
    """인스턴스 메서드의 첫 인자 이름. static/class 메서드는 None."""
    for deco in node.decorator_list:
        name = deco.id if isinstance(deco, ast.Name) else None
        if name in ("staticmethod", "classmethod"):
            return None
    args = node.args.posonlyargs + node.args.args
    if not args:
        return None
    return args[0].arg


def _tag_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child._softgate_parent = parent  # type: ignore[attr-defined]


def _is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def compute_lcom4(class_node: ast.ClassDef) -> ClassCohesion:
    """ClassDef 하나에 대해 LCOM4를 계산한다.

    생성자를 비롯한 dunder 메서드(__init__ 등)는 제외한다. 생성자는
    보통 모든 필드를 초기화하므로 포함하면 서로 무관한 메서드들이
    인위적으로 한 덩어리로 묶여 LCOM4가 늘 1로 나온다.
    """
    methods: dict[str, _MethodScanner] = {}
    for item in class_node.body:
        if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if _is_dunder(item.name):
            continue
        self_name = _self_param_name(item)
        if self_name is None:
            continue
        scanner = _MethodScanner(self_name)
        for stmt in item.body:
            scanner.visit(stmt)
        methods[item.name] = scanner

    names = list(methods)
    uf = _UnionFind(names)
    all_fields: set[str] = set()

    for i, a in enumerate(names):
        all_fields |= methods[a].fields
        for b in names[i + 1 :]:
            shares_field = bool(methods[a].fields & methods[b].fields)
            calls_each = b in methods[a].calls or a in methods[b].calls
            if shares_field or calls_each:
                uf.union(a, b)

    components = uf.groups() if names else []
    return ClassCohesion(
        class_name=class_node.name,
        method_count=len(names),
        field_count=len(all_fields),
        lcom4=len(components),
        line=class_node.lineno,
        components=components,
    )


def analyze_source(source: str) -> list[ClassCohesion]:
    """소스 문자열 안의 모든 최상위 클래스에 대해 LCOM4를 계산한다."""
    tree = ast.parse(source)
    _tag_parents(tree)
    results: list[ClassCohesion] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            results.append(compute_lcom4(node))
    return results
