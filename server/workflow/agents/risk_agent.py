from typing import List, Literal

from pydantic import BaseModel, Field

from server.config.settings import get_llm
from server.tools.dart_tool import DartTool
from server.workflow.state import InvestmentState, AgentType


class RiskOutput(BaseModel):
    agent: Literal["RISK_AGENT"] = "RISK_AGENT"
    summary: str = Field(
        description="전체 리스크 판단 요약"
    )
    key_risks: List[str] = Field(
        description="가장 중요한 핵심 리스크"
    )
    short_term_risks: List[str] = Field(
        description="단기적으로 주가에 영향을 줄 수 있는 리스크"
    )
    long_term_risks: List[str] = Field(
        description="중장기 구조적 리스크"
    )
    monitoring_points: List[str] = Field(
        description="향후 반드시 확인해야 할 핵심 지표"
    )
    risk_level: Literal["낮음", "보통", "높음"] = Field(
        description="종합 리스크 수준"
    )
    evidence: List[str] = Field(
        description="DART 근거 기반 핵심 문장 요약"
    )


class RiskAgent:
    def __init__(self, k: int = 5):
        self.llm = get_llm(temperature=0.2)
        self.structured_llm = self.llm.with_structured_output(RiskOutput)
        self.dart_tool = DartTool(k=k)

    def run(self, state: InvestmentState) -> InvestmentState:
        company_name = state["company_name"]
        question = state["question"]

        docs, context = self.dart_tool.search(
            company_name=company_name,
            question=question,
            mode="risk",
        )

        prompt = f"""
당신은 투자 리스크 관리자입니다.

[기업]
{company_name}

[사용자 질문]
{question}

[BULL 의견]
{state["bull_opinion"]}

[BEAR 의견]
{state["bear_opinion"]}

[DART 근거]
{context}

역할:
- 찬성/반대 의견을 모두 검토하세요.
- DART 근거 기준으로 핵심 리스크를 판단하세요.
- 리스크 수준을 반드시 "낮음", "보통", "높음" 중 하나로 제시하세요.
- DART 문서에 있는 내용만 사용하세요.
- 문서에 없는 내용은 추측하지 마세요.
- 모든 응답은 RiskOutput 스키마에 맞춰 작성하세요.

작성 기준:
- summary: 전체 리스크를 2~3문장으로 요약
- key_risks: 2~5개
- short_term_risks: 1~4개
- long_term_risks: 1~4개
- monitoring_points: 3~5개
- risk_level: 반드시 낮음/보통/높음 중 하나
- evidence: DART 근거에서 확인 가능한 내용만 2~5개
"""

        output: RiskOutput = self.structured_llm.invoke(prompt)
        output_dict = output.model_dump()

        state["docs"][AgentType.RISK] = docs
        state["contexts"][AgentType.RISK] = context
        state["risk_opinion"] = output_dict
        state["messages"].append(
            {
                "role": AgentType.RISK,
                "content": output_dict,
            }
        )

        return state