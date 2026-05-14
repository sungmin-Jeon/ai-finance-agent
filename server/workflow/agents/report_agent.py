from typing import List, Literal

from pydantic import BaseModel, Field

from server.config.settings import get_llm
from server.tools.dart_tool import DartTool
from server.workflow.state import InvestmentState, AgentType


class ReportOutput(BaseModel):
    agent: Literal["REPORT_AGENT"] = "REPORT_AGENT"
    title: str = Field(description="리포트 제목")
    executive_summary: str = Field(description="핵심 요약")
    bull_case: str = Field(description="투자 찬성 근거 요약")
    bear_case: str = Field(description="투자 반대 근거 요약")
    risk_summary: str = Field(description="주요 리스크 요약")
    investment_view: Literal["매수", "관망", "비중축소"] = Field(
        description="최종 투자 관점"
    )
    investment_reason: str = Field(description="최종 투자 관점의 판단 근거")
    key_monitoring_points: List[str] = Field(
        description="향후 확인해야 할 핵심 지표"
    )
    evidence: List[str] = Field(
        description="DART 근거 기반 핵심 문장 요약"
    )


class ReportAgent:
    def __init__(self, k: int = 5):
        self.llm = get_llm(temperature=0.2)
        self.structured_llm = self.llm.with_structured_output(ReportOutput)
        self.dart_tool = DartTool(k=k)

    def run(self, state: InvestmentState) -> InvestmentState:
        company_name = state["company_name"]
        question = state["question"]

        docs, context = self.dart_tool.search(
            company_name=company_name,
            question=question,
            mode="report",
        )

        prompt = f"""
당신은 금융 리서치 리포트 작성자입니다.

[기업]
{company_name}

[사용자 질문]
{question}

[BULL 의견]
{state["bull_opinion"]}

[BEAR 의견]
{state["bear_opinion"]}

[RISK 판단]
{state["risk_opinion"]}

[최종 검토용 DART 근거]
{context}

역할:
- 찬성, 반대, 리스크 판단을 종합하세요.
- 투자 추천은 단정하지 말고 균형 있게 작성하세요.
- DART 문서에 있는 내용만 사용하세요.
- 문서에 없는 내용은 추측하지 마세요.
- 모든 응답은 ReportOutput 스키마에 맞춰 작성하세요.

작성 기준:
- title: 리포트 제목
- executive_summary: 전체 투자 판단을 2~4문장으로 요약
- bull_case: 투자 찬성 근거 요약
- bear_case: 투자 반대 근거 요약
- risk_summary: 핵심 리스크 요약
- investment_view: 반드시 "매수", "관망", "비중축소" 중 하나
- investment_reason: 최종 판단 근거
- key_monitoring_points: 향후 확인할 지표 3~5개
- evidence: DART 근거에서 확인 가능한 내용만 2~5개
"""

        output: ReportOutput = self.structured_llm.invoke(prompt)
        output_dict = output.model_dump()

        state["docs"][AgentType.REPORT] = docs
        state["contexts"][AgentType.REPORT] = context
        state["final_report"] = output_dict
        state["messages"].append(
            {
                "role": AgentType.REPORT,
                "content": output_dict,
            }
        )

        return state