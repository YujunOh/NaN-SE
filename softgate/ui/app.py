"""softgate Streamlit UI.

CLI(`softgate.cli`)와 동일한 검출/설명 모듈을 그대로 재사용한다. UI는 입출력만
담당하고 로직은 metrics/learning_card/db 층에 위임한다(계층 분리). 실행:

    streamlit run softgate/ui/app.py
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import streamlit as st

from softgate.db import Store
from softgate.learning_card.generator import generate_card
from softgate.metrics import analyze_source
from softgate.metrics.complexity import findings_from_complexity
from softgate.metrics.findings import MetricFinding, findings_from_cohesion

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"
UI_DB = Path.home() / ".softgate" / "ui.db"


def _collect_findings(source: str) -> list[MetricFinding]:
    return findings_from_cohesion(analyze_source(source)) + findings_from_complexity(source)


def _load_example_source() -> str:
    sample = EXAMPLES_DIR / "auth_service.py"
    if sample.exists():
        return sample.read_text(encoding="utf-8")
    return ""


st.set_page_config(page_title="softgate", layout="wide")
st.title("softgate")
st.caption("검출은 결정론적 메트릭, 설명만 LLM. 바이브코딩 산출물의 SRP·응집도 위반을 학습 카드로.")

with st.sidebar:
    st.header("입력")
    if st.button("예시 코드 불러오기 (auth_service.py)"):
        st.session_state["source"] = _load_example_source()
    st.session_state.setdefault("source", _load_example_source())
    source = st.text_area("분석할 Python 코드", key="source", height=360)

tab_detect, tab_cards = st.tabs(["검출", "학습 카드 검수"])

with tab_detect:
    if not source.strip():
        st.info("사이드바에 코드를 넣거나 예시를 불러오세요.")
    else:
        cohesion = analyze_source(source)
        st.subheader("메트릭 (LLM 없음, 결정론적)")
        st.dataframe(
            [
                {
                    "클래스": c.class_name,
                    "LCOM4": c.lcom4,
                    "메서드": c.method_count,
                    "응집": "OK" if c.is_cohesive else "분리 검토",
                }
                for c in cohesion
            ],
            use_container_width=True,
            hide_index=True,
        )

        findings = _collect_findings(source)
        st.subheader("위반 finding")
        if not findings:
            st.success("위반 finding 없음.")
        else:
            st.dataframe(
                [
                    {
                        "대상": f.class_name,
                        "지표": f.metric,
                        "값": f.value,
                        "임계": f.threshold,
                        "원칙": f.principle.name,
                        "심각도": f.severity,
                    }
                    for f in findings
                ],
                use_container_width=True,
                hide_index=True,
            )

            st.divider()
            has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
            if not has_key:
                st.warning("학습 카드 생성은 ANTHROPIC_API_KEY가 필요합니다. 검출까지는 키 없이 동작합니다.")
            if st.button("학습 카드 생성", disabled=not has_key):
                with Store(UI_DB) as store:
                    session_id = datetime.now().strftime("%Y%m%d-%H%M%S")
                    created = []
                    for finding in findings:
                        finding_id = store.save_finding(finding, session_id)
                        card_id = store.next_card_id()
                        with st.spinner(f"{card_id} 생성 중 ({finding.class_name})"):
                            card = generate_card(
                                finding,
                                source,
                                card_id=card_id,
                                session_id=session_id,
                                finding_id=finding_id,
                            )
                            store.save_card(card)
                        created.append(card_id)
                st.success(f"{len(created)}장 생성: {', '.join(created)}. '학습 카드 검수' 탭에서 확인하세요.")

with tab_cards:
    st.subheader("미검수 학습 카드")
    with Store(UI_DB) as store:
        unreviewed = store.get_unreviewed()
    if not unreviewed:
        st.info("미검수 카드 없음.")
    for card in unreviewed:
        with st.expander(f"{card.id} | {card.principle.name} | 심각도 {card.severity}/10", expanded=False):
            st.markdown(f"**위반 이유**\n\n{card.violation_reason}")
            st.markdown(f"**운영 단계 비용**\n\n{card.cost_example}")
            col_b, col_a = st.columns(2)
            with col_b:
                st.markdown("**Before**")
                st.code(card.before_code, language="python")
            with col_a:
                st.markdown("**After**")
                st.code(card.after_code, language="python")
            st.markdown("**학습 포인트**")
            for p in card.learning_points:
                st.markdown(f"- {p}")
            st.markdown(f"**재요청 prompt**\n\n{card.revision_prompt}")

            c1, c2 = st.columns(2)
            if c1.button("채택", key=f"accept-{card.id}"):
                with Store(UI_DB) as store:
                    store.review_card(card.id, True)
                st.rerun()
            if c2.button("거절", key=f"reject-{card.id}"):
                with Store(UI_DB) as store:
                    store.review_card(card.id, False)
                st.rerun()
