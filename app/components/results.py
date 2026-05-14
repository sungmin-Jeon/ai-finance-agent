import streamlit as st


def render_list(items):
    if not items:
        st.write("- 없음")
        return

    for item in items:
        st.markdown(f"- {item}")


def display_bull(bull):
    st.subheader("🐂 투자 찬성 관점")

    st.markdown(f"**요약**  \n{bull.get('summary', '')}")
    st.markdown(f"**핵심 논리**  \n{bull.get('core_thesis', '')}")

    with st.expander("성장 요인"):
        render_list(bull.get("growth_drivers", []))

    with st.expander("경쟁 우위"):
        render_list(bull.get("competitive_advantages", []))

    with st.expander("수익성 개선 요인"):
        render_list(bull.get("profitability_catalysts", []))

    with st.expander("투자 매력"):
        render_list(bull.get("investment_attractions", []))

    st.metric("Bull Score", bull.get("bull_score", "-"))


def display_bear(bear):
    st.subheader("🐻 투자 반대 관점")

    st.markdown(f"**요약**  \n{bear.get('summary', '')}")
    st.markdown(f"**핵심 반론**  \n{bear.get('core_counter_argument', '')}")

    with st.expander("사업 리스크"):
        render_list(bear.get("business_risks", []))

    with st.expander("시장/경쟁 리스크"):
        render_list(bear.get("market_competition_risks", []))

    with st.expander("재무 리스크"):
        render_list(bear.get("financial_risks", []))

    with st.expander("투자 유의사항"):
        render_list(bear.get("investment_cautions", []))

    st.metric("Bear Score", bear.get("bear_score", "-"))


def display_risk(risk):
    st.subheader("⚠️ 리스크 평가")

    st.markdown(f"**요약**  \n{risk.get('summary', '')}")

    st.metric("Risk Level", risk.get("risk_level", "-"))

    with st.expander("핵심 리스크"):
        render_list(risk.get("key_risks", []))

    with st.expander("단기 리스크"):
        render_list(risk.get("short_term_risks", []))

    with st.expander("장기 리스크"):
        render_list(risk.get("long_term_risks", []))

    with st.expander("모니터링 포인트"):
        render_list(risk.get("monitoring_points", []))


def display_report(report):
    st.subheader("📄 최종 투자 리포트")

    st.markdown(f"## {report.get('title', '투자 판단 리포트')}")

    st.info(report.get("executive_summary", ""))

    st.markdown("### 투자 의견")
    st.metric("Investment View", report.get("investment_view", "-"))

    st.markdown(f"**판단 근거**  \n{report.get('investment_reason', '')}")

    st.markdown("### Bull Case")
    st.write(report.get("bull_case", ""))

    st.markdown("### Bear Case")
    st.write(report.get("bear_case", ""))

    st.markdown("### Risk Summary")
    st.write(report.get("risk_summary", ""))

    with st.expander("핵심 모니터링 포인트"):
        render_list(report.get("key_monitoring_points", []))

    with st.expander("DART 근거"):
        render_list(report.get("evidence", []))


def display_results():
    result = st.session_state.result

    st.title("📊 투자 분석 결과")

    report = result.get("final_report", {})
    bull = result.get("bull_opinion", {})
    bear = result.get("bear_opinion", {})
    risk = result.get("risk_opinion", {})

    display_report(report)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        display_bull(bull)

    with col2:
        display_bear(bear)

    st.divider()

    display_risk(risk)

    st.divider()

    if st.button("새 분석하기"):
        st.session_state.app_mode = "input"
        st.rerun()