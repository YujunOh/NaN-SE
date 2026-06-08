"""nanse CLI. Typer + rich. 본인 구현 영역(사용자 검수 인터페이스)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from nanse.db import Store
from nanse.learning_card.generator import generate_card
from nanse.learning_card.models import LearningCard
from nanse.metrics import analyze_source
from nanse.metrics.complexity import findings_from_complexity
from nanse.metrics.findings import MetricFinding, findings_from_cohesion
from nanse.principles import Principle

app = typer.Typer(help="AI 생성 코드의 응집도·복잡도 위반을 결정론적으로 검출하고 학습 카드로 설명한다")
console = Console()


def _collect_findings(source: str, source_file: str | None = None) -> list[MetricFinding]:
    return findings_from_cohesion(
        analyze_source(source), source_file
    ) + findings_from_complexity(source, source_file)


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

    findings = _collect_findings(source, str(path))
    if not findings:
        console.print("[green]위반 finding 없음.[/green]")
        return

    ftable = Table(title="위반 finding")
    ftable.add_column("대상")
    ftable.add_column("위치")
    ftable.add_column("지표")
    ftable.add_column("값/임계", justify="center")
    ftable.add_column("원칙")
    ftable.add_column("심각도", justify="right")
    for f in findings:
        loc = f"{path.name}:{f.source_line}" if f.source_line else path.name
        ftable.add_row(
            f.class_name,
            loc,
            f.metric,
            f"{f.value:g} / {f.threshold:g}",
            f.principle.name,
            str(f.severity),
        )
    console.print(ftable)


@app.command()
def trace(
    spec: Path | None = None,
    gaps: bool = False,
    root: Path | None = None,
) -> None:
    """요구(UC) ↔ 코드 ↔ 테스트 추적 매트릭스를 출력하고 gap을 표시한다. (LLM 없음)

    spec 미지정 시 현재 폴더의 traceability.toml을, 그것도 없으면 기본 매핑을 쓴다.
    --gaps 는 미완(코드·테스트 누락) 항목만 보여준다.
    """
    from nanse.traceability import build_matrix, gaps_only, load_spec

    work_root = root or Path.cwd()
    spec_path = spec or (work_root / "traceability.toml")
    rows = build_matrix(load_spec(spec_path), work_root)
    if gaps:
        rows = gaps_only(rows)

    status = {
        "complete": "[green]complete[/green]",
        "no_test": "[yellow]no_test[/yellow]",
        "no_code": "[red]no_code[/red]",
    }
    table = Table(title="요구 추적 매트릭스 (REQ ↔ UC ↔ 코드 ↔ 테스트)")
    table.add_column("REQ")
    table.add_column("UC")
    table.add_column("요구")
    table.add_column("코드", justify="center")
    table.add_column("테스트", justify="center")
    table.add_column("상태")
    for r in rows:
        table.add_row(
            r.req,
            r.req_id,
            r.title,
            f"{len(r.code_present)}/{r.code_total}",
            f"{len(r.test_present)}/{r.test_total}",
            status.get(r.gap, r.gap),
        )
    console.print(table)

    if not rows:
        console.print("[green]gap 없음. 모든 요구가 코드와 테스트로 추적됨.[/green]")


@app.command()
def learn(path: Path, db: Path | None = None) -> None:
    """검출된 위반 finding을 LLM 설명층에 넘겨 학습 카드를 생성·저장한다.

    검출은 결정적, 설명만 LLM. ANTHROPIC_API_KEY 또는 GEMINI_API_KEY 필요
    (NANSE_LLM=anthropic|gemini로 명시 가능, 기본 Anthropic).
    """
    source = path.read_text(encoding="utf-8")
    findings = _collect_findings(source, str(path))
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
    console.print(f"[green]{len(created)}장 저장됨: {', '.join(created)}.[/green] 'nanse review <ID>'로 검수.")


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
    """API 키 없이 대시보드/검수 흐름을 보도록 예시 finding·카드를 채운다.

    원칙(SRP·OCP)과 파일·라인, 채택/거절/대기 상태가 섞인 데이터다.
    """
    from datetime import timedelta

    day0 = datetime.now() - timedelta(days=1)
    day1 = datetime.now()

    # (class_name, metric, value, threshold, principle, severity, file, line)
    specs = [
        ("AuthService", "lcom4", 3.0, 1.0, Principle.SRP, 6,
         "src/auth/service.py", 12,
         "AuthService가 인증·이메일·토큰 발급을 한 클래스에 모아 응집이 갈라졌다. LCOM4=3.",
         "이메일 로직 한 줄 바꿔도 인증 모듈 전체 회귀가 필요해 배포가 지연된다.",
         "class AuthService:\n    def login(self): ...\n    def send_email(self): ...\n    def issue_token(self): ...",
         "class AuthService:\n    def login(self): ...\nclass EmailNotifier: ...\nclass TokenService: ...",
         ["변경 사유가 다르면 클래스도 다르게", "응집이 낮으면 테스트 격리가 어렵다"],
         "AuthService를 AuthService/EmailNotifier/TokenService로 분리하라.",
         True, None, day0),
        ("OrderRouter.route", "cyclomatic", 14.0, 10.0, Principle.OCP, 4,
         "src/order/router.py", 47,
         "route가 결제수단마다 if/elif로 분기해 새 수단을 더할 때마다 이 메서드를 다시 연다.",
         "수단 추가 한 번이 핵심 분기 메서드 수정을 강제해 회귀 위험이 매 배포 누적된다.",
         "def route(self, kind):\n    if kind == 'card': ...\n    elif kind == 'bank': ...\n    elif kind == 'point': ...",
         "handlers = {'card': CardHandler(), ...}\n\ndef route(self, kind):\n    return handlers[kind].handle()",
         ["분기 폭증은 OCP 위반 신호", "전략 매핑으로 확장은 열고 변경은 닫는다"],
         "route의 if/elif 분기를 핸들러 매핑(전략 패턴)으로 바꿔라.",
         None, None, day1),
        ("ReportBuilder", "lcom4", 4.0, 1.0, Principle.SRP, 9,
         "src/report/builder.py", 8,
         "ReportBuilder가 집계·서식·파일쓰기·메일발송 네 책임을 모아 LCOM4=4.",
         "서식 한 가지 바꾸려다 메일 발송 경로까지 깨져 장애로 이어진다.",
         "class ReportBuilder:\n    def aggregate(self): ...\n    def format(self): ...\n    def write_file(self): ...\n    def send_mail(self): ...",
         "class ReportAggregator: ...\nclass ReportFormatter: ...\nclass ReportWriter: ...\nclass ReportMailer: ...",
         ["책임이 넷이면 변경 이유도 넷", "큰 클래스일수록 분리 이득이 크다"],
         "ReportBuilder를 집계/서식/쓰기/발송 네 클래스로 분리하라.",
         False, "교정 예시의 분리 단위가 우리 도메인과 안 맞아 거절.", day0),
        ("PaymentGateway", "lcom4", 2.0, 1.0, Principle.SRP, 3,
         "src/payment/gateway.py", 20,
         "PaymentGateway가 결제 처리와 로깅 책임을 함께 들고 있어 LCOM4=2.",
         "로깅 포맷 변경이 결제 경로 테스트를 통째로 다시 돌리게 만든다.",
         "class PaymentGateway:\n    def charge(self): ...\n    def write_log(self): ...",
         "class PaymentGateway:\n    def charge(self): ...\nclass PaymentLogger:\n    def write_log(self): ...",
         ["로깅은 횡단 관심사로 분리", "응집 회복이 테스트 범위를 좁힌다"],
         "PaymentGateway에서 로깅 책임을 PaymentLogger로 분리하라.",
         True, None, day1),
        ("DataSync.run", "cyclomatic", 12.0, 10.0, Principle.OCP, 2,
         "src/sync/data_sync.py", 33,
         "run이 소스 종류별 분기를 한 메서드에 쌓아 순환복잡도 12.",
         "동기화 대상이 늘 때마다 run을 수정해 기존 경로 회귀를 떠안는다.",
         "def run(self, src):\n    if src == 'db': ...\n    elif src == 'api': ...\n    elif src == 'file': ...",
         "syncers = {'db': DbSyncer(), ...}\n\ndef run(self, src):\n    syncers[src].sync()",
         ["분기 대신 매핑으로 확장 지점을 외부화", "복잡도는 경로 수에 비례"],
         "run의 소스별 분기를 syncer 매핑으로 교체하라.",
         None, None, day1),
    ]

    with Store(db) as store:
        for i, s in enumerate(specs, start=1):
            (cname, metric, value, thr, principle, sev, sfile, sline,
             reason, cost, before, after, points, prompt, accepted, fb, gen) = s
            session_id = gen.strftime("%Y%m%d-%H%M")
            finding = MetricFinding(
                class_name=cname, metric=metric, value=value, threshold=thr,
                principle=principle, severity=sev,
                source_file=sfile, source_line=sline,
            )
            finding_id = store.save_finding(finding, session_id)
            card = LearningCard(
                id=f"CARD-{i:03d}",
                session_id=session_id,
                finding_id=finding_id,
                principle=principle,
                severity=sev,
                code_hash=f"h{i:013d}",
                violation_reason=reason,
                cost_example=cost,
                before_code=before,
                after_code=after,
                learning_points=points,
                revision_prompt=prompt,
                user_accepted=accepted,
                user_feedback=fb,
                source_file=sfile,
                source_line=sline,
                generated_at=gen,
                reviewed_at=(gen if accepted is not None else None),
            )
            store.save_card(card)
    console.print(
        f"[green]예시 finding·카드 {len(specs)}건 저장됨.[/green] "
        "'nanse serve'로 대시보드 확인."
    )


@app.command()
def serve(
    db: Path | None = None,
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """대시보드용 읽기 API를 띄운다 (FastAPI + uvicorn).

    검출·설명 결과를 읽기만 노출한다. 검수는 'nanse review'에 남는다.
    """
    try:
        import uvicorn
    except ModuleNotFoundError:
        console.print(
            "[red]API 의존성이 없음.[/red] 'pip install -e .[api]'로 설치 후 다시 실행."
        )
        raise typer.Exit(1)

    from nanse.api import create_app

    console.print(f"[green]API 기동:[/green] http://{host}:{port}/api/health")
    uvicorn.run(create_app(db), host=host, port=port)


if __name__ == "__main__":
    app()
