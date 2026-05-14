import streamlit as st

from server.workflow.state import AgentType


def render_source_materials():
    docs = st.session_state.get("docs", {})
    contexts = st.session_state.get("contexts", {})

    if not docs and not contexts:
        return

    with st.expander("📚 사용된 DART 참고 자료 보기"):
        for role in [
            AgentType.BULL,
            AgentType.BEAR,
            AgentType.RISK,
            AgentType.REPORT,
        ]:
            st.subheader(AgentType.to_korean(role))

            context = contexts.get(role, "")
            if context:
                st.text(context[:1500] + "..." if len(context) > 1500 else context)
            else:
                st.caption("참고 자료 없음")

            st.divider()