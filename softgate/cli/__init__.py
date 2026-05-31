"""softgate CLI. Typer + rich. 본인 구현 영역(사용자 검수 인터페이스)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from softgate.db import Store
from softgate.learning_card.generator import generate_card
from softgate.learning_card.models import LearningCard
from softgate.metrics import analyze_source
from softgate.metrics.complexity import findings_from_complexity
from softgate.metrics.findings import MetricFinding, findings_from_cohesion
from softgate.principles import Principle

app = typer.Typer(help="바이브코딩에 SW공학 프로세스를 끼워넣는 부드러운 게이트")
console = Console()


def _collect_findings(source: str) -> list[MetricFinding]:
    return findings_from_cohesion(analyze_source(source)) + findings_from_complexity(source)


@app.command()
def analyze(path: Path) -> None:
    """파이썬 파일의 결정적 메트릭과 위반 finding을 출력한다. (LLM 없음)"""
    source = path.read_text(encoding="utf-8")

    cohesion = analyze_source(source)
    metrics_table = Table(title=f"메트릭: {path.name}")
    metrics_table.add_column("클래스")
    metrics_table.add_column("LCOM4", justify="right")
    metrics_table.add_column("메서드", justify="right")
    metrics_table.add_column("응집", justify="center")
    for c in cohesion:
        metrics_table.add_row(
            c.class_name,
            str(c.lcom4),
            str(c.method_count),
            "OK" if c.is_cohesive else "분리?",
        )
    console.print(metrics_table)

    findings = _collect_findings(source)
    if not findings:
        console.print("[green]위반 finding 없음.[/green]")
        return

    ftable = Table(title="위반 finding")
    ftable.add_column("대상")
    ftable.add_column("지표")
    ftable.add_column("값/임계", justify="center")
    ftable.add_column("원칙")
    ftable.add_column("심각도", justify="right")
    for f in findings:
        ftable.add_row(
            f.class_name,
            f.metric,
            f"{f.value:g} / {f.threshold:g}",
            f.principle.name,
            str(f.severity),
        )
    console.print(ftable)


@app.command()
def learn(path: Path, db: Path | None = None) -> None:
    """검출된 위반 finding을 LLM 설명층에 넘겨 학습 카드를 생성·저장한다.

    검출은 결정적, 설명만 LLM. ANTHROPIC_API_KEY 필요.
    """
    source = path.read_text(encoding="utf-8")
    findings = _collect_findings(source)
    if not findings:
        console.print("[green]위반 finding 없음. 생성할 카드 없음.[/green]")
        return

    with Store(db) as store:
        session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        created: list[str] = []
        for finding in findings:
            finding_id = store.save_finding(finding, session_id)
            card_id = store.next_card_id()
            console.print(f"{card_id} 생성 중... ({finding.class_name} / {finding.metric})")
            card = generate_card(
                finding,
                source,
                card_id=card_id,
                session_id=session_id,
                finding_id=finding_id,
            )
            store.save_card(card)
            created.append(card_id)
    console.print(f"[green]{len(created)}장 저장됨: {', '.join(created)}.[/green] 'softgate review <ID>'로 검수.")


@app.command()
def cards(db: Path | None = None) -> None:
    """미검수 학습 카드 목록."""
    with Store(db) as store:
        unreviewed = store.get_unreviewed()
    if not unreviewed:
        console.print("미검수 카드 없음.")
        return
    table = Table(title="미검수 학습 카드")
    table.add_column("ID")
    table.add_column("원칙")
    table.add_column("심각도", justify="right")
    for c in unreviewed:
        table.add_row(c.id, c.principle.name, str(c.severity))
    console.print(table)


def _render_card(card: LearningCard) -> Panel:
    points = "\n".join(f"  - {p}" for p in card.learning_points)
    body = (
        f"[bold]위반 이유[/bold]\n{card.violation_reason}\n\n"
        f"[bold]운영 단계 비용[/bold]\n{card.cost_example}\n\n"
        f"[bold]Before[/bold]\n{card.before_code}\n\n"
        f"[bold]After[/bold]\n{card.after_code}\n\n"
        f"[bold]학습 포인트[/bold]\n{points}\n\n"
        f"[bold]재요청 prompt[/bold]\n{card.revision_prompt}"
    )
    title = f"{card.id} | {card.principle.name} | 심각도 {card.severity}/10"
    return Panel(body, title=title, border_style="yellow")


@app.command()
def review(card_id: str, db: Path | None = None) -> None:
    """학습 카드 한 장을 띄우고 채택/거절을 받는다."""
    with Store(db) as store:
        card = store.get_card(card_id)
        if card is None:
            console.print(f"[red]{card_id} 없음.[/red]")
            raise typer.Exit(1)
        console.print(_render_card(card))
        choice = typer.prompt("[A]ccept / [R]eject / [S]kip").strip().lower()
        if choice == "a":
            store.review_card(card_id, True)
            console.print("[green]채택됨. 재요청 prompt를 AI agent에 전송할 수 있음.[/green]")
        elif choice == "r":
            feedback = typer.prompt("거절 사유 (Enter로 건너뛰기)", default="")
            store.review_card(card_id, False, feedback or None)
            console.print("거절 사유 기록됨. 다음 카드 생성 시 prompt 개선에 반영.")
        else:
            console.print("건너뜀.")


@app.command(name="seed-demo")
def seed_demo(db: Path | None = None) -> None:
    """API 키 없이 검수 흐름을 테스트하도록 예시 카드 1장을 넣는다."""
    with Store(db) as store:
        card = LearningCard(
            id=store.next_card_id(),
            session_id="demo",
            finding_id=0,
            principle=Principle.SRP,
            severity=6,
            code_hash="demo000000000000",
            violation_reason=(
                "AuthService가 인증, 이메일 발송, 토큰 발급을 모두 담당해 "
                "책임이 셋으로 갈렸다. LCOM4=3."
            ),
            cost_example="이메일 로직 변경 시 인증 모듈 전체 회귀가 필요해 배포가 지연된다.",
            before_code="class AuthService:\n    def login(self): ...\n    def send_email(self): ...\n    def issue_token(self): ...",
            after_code="class AuthService:\n    def login(self): ...\nclass EmailNotifier:\n    def send_email(self): ...\nclass TokenService:\n    def issue_token(self): ...",
            learning_points=[
                "SRP는 클래스가 변경되는 이유가 하나여야 한다는 원칙",
                "책임 분리는 테스트 격리에도 도움",
                "변경 사유가 다르면 클래스도 다르게",
            ],
            revision_prompt="AuthService를 AuthService/EmailNotifier/TokenService로 분리하라.",
            generated_at=datetime.now(),
        )
        store.save_card(card)
    console.print(f"[green]예시 카드 {card.id} 저장됨.[/green] 'softgate cards'로 확인.")


if __name__ == "__main__":
    app()
