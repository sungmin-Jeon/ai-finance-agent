import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.header("⚙️ 설정")

        st.session_state.company_name = st.text_input(
            "분석 기업",
            value=st.session_state.company_name,
        )

        st.session_state.enable_rag = st.checkbox(
            "DART RAG 사용",
            value=True,
        )

        st.caption("현재 MVP는 SK하이닉스 DART vector store 기준입니다.")

        if st.button("초기화"):
            from app.utils.state_manager import reset_session_state

            reset_session_state()
            st.rerun()