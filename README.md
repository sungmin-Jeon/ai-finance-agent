# AI Finance Agent

DART 사업보고서 기반 AI 투자 리서치 도우미입니다.  
기업명과 투자 질문을 입력하면, 사업보고서 기반 RAG 검색 결과를 바탕으로 투자 찬성 Agent, 투자 반대 Agent, 리스크 판단 Agent, 최종 리포트 Agent가 순차적으로 분석을 수행하고 투자 판단 리포트를 생성합니다.

Streamlit UI와 FastAPI API로 구성되어 있으며, LangGraph + LangChain, FAISS 기반 RAG를 사용합니다.

## 왜 만들었나요?

- 개인 투자자가 방대한 사업보고서를 직접 읽고 핵심 내용을 파악하기 어렵다는 문제를 줄이고 싶었습니다.
- 단순 요약이 아니라 투자 찬성/반대/리스크 관점을 나누어 균형 잡힌 분석을 제공하고자 했습니다.
- RAG를 통해 DART 사업보고서 문맥을 활용하여 근거 기반 투자 리포트를 생성하고자 했습니다.

## 주요 기능

- DART 사업보고서 기반 RAG 검색
- 투자 찬성 Agent: 성장 요인과 투자 매력 분석
- 투자 반대 Agent: 위험 요인과 부정적 시나리오 분석
- 리스크 판단 Agent: 찬반 의견을 종합해 핵심 리스크 평가
- 최종 리포트 Agent: 투자 판단 보고서 생성
- Structured Output: Agent별 결과를 JSON 형태로 구조화
- Streamlit UI: 기업명/질문 입력 및 분석 결과 확인
- FastAPI API: 투자 분석 Workflow 실행

## 코드 구조

```text
app/
  main.py                 # Streamlit 엔트리포인트(UI)
  components/
    sidebar.py            # 사이드바 설정
    results.py            # 분석 결과 출력
  utils/
    state_manager.py      # Streamlit 세션 상태 초기화

server/
  main.py                 # FastAPI 엔트리포인트(API 라우터 등록)
  api/
    v1/
      workflow.py         # 투자 분석 API
  agents/
    bull_agent.py         # 투자 찬성 Agent
    bear_agent.py         # 투자 반대 Agent
    risk_agent.py         # 리스크 판단 Agent
    report_agent.py       # 최종 리포트 Agent
  config/
    settings.py           # 환경변수 및 LLM 설정
  retrieval/
    retriever.py          # FAISS 검색 및 문서 포맷팅
  schemas/
    agent_schema.py       # Agent Structured Output 스키마
  tools/
    dart_tool.py          # DART 문서 검색 Tool
  workflow/
    graph.py              # LangGraph Workflow 구성
    state.py              # InvestmentState 타입

requirements.txt          # 의존성 목록
.env                      # 환경변수 예시
README.md                 # 프로젝트 설명