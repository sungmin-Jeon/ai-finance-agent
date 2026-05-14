import streamlit as st


def init_session_state():
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "input"

    if "company_name" not in st.session_state:
        st.session_state.company_name = "SK하이닉스"

    if "question" not in st.session_state:
        st.session_state.question = "SK하이닉스 투자해도 될까? 투자 판단 리포트 작성해줘."

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "docs" not in st.session_state:
        st.session_state.docs = {}

    if "contexts" not in st.session_state:
        st.session_state.contexts = {}

    if "result" not in st.session_state:
        st.session_state.result = None


def reset_session_state():
    st.session_state.app_mode = "input"
    st.session_state.messages = []
    st.session_state.docs = {}
    st.session_state.contexts = {}
    st.session_state.result = None