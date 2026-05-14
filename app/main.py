import sys
from pathlib import Path

import requests
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from server.config.settings import settings

from app.components.sidebar import render_sidebar
from app.components.results import display_results
from app.utils.state_manager import init_session_state


API_URL = "http://localhost:8000/api/v1/workflow/investment"


def start_analysis():
    company_name = st.session_state.company_name
    question = st.session_state.question

    payload = {
        "company_name": company_name,
        "question": question,
        "enable_rag": st.session_state.get("enable_rag", True),
    }

    try:
        with st.spinner("투자 판단 에이전트 실행 중..."):
            response = requests.post(
                API_URL,
                json=payload,
                timeout=180,
            )

        response.raise_for_status()

        data = response.json()
        result = data.get("result", data)

        st.session_state.result = result
        st.session_state.messages = result.get("messages", [])
        st.session_state.docs = result.get("docs", {})
        st.session_state.contexts = result.get("contexts", {})
        st.session_state.app_mode = "results"

        st.rerun()

    except requests.exceptions.ConnectionError:
        st.error(
            "FastAPI 서버에 연결할 수 없습니다. "
            "`uvicorn server.main:app --reload --host 0.0.0.0 --port 8000`을 먼저 실행하세요."
        )
        st.session_state.app_mode = "input"

    except requests.exceptions.Timeout:
        st.error("분석 시간이 너무 오래 걸려 요청이 종료되었습니다. timeout 값을 늘려보세요.")
        st.session_state.app_mode = "input"

    except requests.exceptions.HTTPError as e:
        st.error(f"API 요청 실패: {e}")
        try:
            st.json(response.json())
        except Exception:
            st.write(response.text)
        st.session_state.app_mode = "input"

    except Exception as e:
        st.error(f"분석 중 오류가 발생했습니다: {e}")
        st.session_state.app_mode = "input"


def render_input():
    st.markdown(
        """
        ### 프로젝트 소개

        이 애플리케이션은 SK하이닉스 DART 사업보고서 기반으로  
        투자 찬성, 투자 반대, 리스크 판단, 최종 리포트 에이전트가  
        순차적으로 투자 판단을 수행합니다.
        """
    )

    st.text_area(
        "투자 질문",
        key="question",
        height=120,
    )

    if st.button("분석 시작", type="primary"):
        st.session_state.app_mode = "analysis"
        st.rerun()


def render_ui():
    st.set_page_config(page_title="AI Finance Agent", page_icon="📈")

    st.title("📈 AI Finance Agent")

    if settings.OPENAI_API_KEY:
        st.success("API Key loaded successfully")
    else:
        st.error("API Key not found")
        return

    render_sidebar()

    current_mode = st.session_state.app_mode

    if current_mode == "input":
        render_input()

    elif current_mode == "analysis":
        start_analysis()

    elif current_mode == "results":
        display_results()


if __name__ == "__main__":
    init_session_state()
    render_ui()