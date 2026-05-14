from typing import Dict, List, Literal
from pydantic import BaseModel, Field

from server.config.settings import get_llm
from server.tools.dart_tool import DartTool
from server.workflow.state import InvestmentState, AgentType


class BearOutput(BaseModel):
    agent: Literal["BEAR_AGENT"] = "BEAR_AGENT"
    summary: str = Field(description="투자 반대 관점의 핵심 요약")
    core_counter_argument: str = Field(description="BULL 의견에 대한 핵심 반론")
    business_risks: List[str] = Field(description="사업 구조 또는 제품 관련 리스크")
    market_competition_risks: List[str] = Field(description="시장 및 경쟁 환경 리스크")
    financial_risks: List[str] = Field(description="실적 변동성, CAPEX, 재무 부담 등 재무 리스크")
    investment_cautions: List[str] = Field(description="투자자가 유의해야 할 사항")
    evidence: List[str] = Field(description="DART 근거 기반 핵심 문장 요약")
    bear_score: int = Field(
        description="투자 반대 강도. 1은 약함, 5는 매우 강함",
        ge=1,
        le=5,
    )


class BearAgent:
    def __init__(self, k: int = 5):
        self.llm = get_llm(temperature=0.2)
        self.structured_llm = self.llm.with_structured_output(BearOutput)
        self.dart_tool = DartTool(k=k)

    def run(self, state: InvestmentState) -> InvestmentState:
        company_name = state["company_name"]
        question = state["question"]

        docs, context = self.dart_tool.search(
            company_name=company_name,
            question=question,
            mode="bear",
        )

        prompt = f"""
당신은 투자 반대 관점의 금융 애널리스트입니다.

[기업]
{company_name}

[사용자 질문]
{question}

[BULL 의견]
{state["bull_opinion"]}

[DART 근거]
{context}

역할:
- BULL 의견을 검토하고 반대 논리를 작성하세요.
- 사업 리스크, 경쟁 심화, 실적 변동성, 재무 부담을 중심으로 분석하세요.
- DART 근거에 있는 내용만 사용하세요.
- 문서에 없는 내용은 추측하지 마세요.
- 모든 응답은 BearOutput 스키마에 맞춰 작성하세요.

작성 기준:
- summary: 투자 반대 관점의 핵심을 2문장 이내로 요약
- core_counter_argument: BULL 의견의 가장 약한 부분을 지적
- business_risks: 2~4개
- market_competition_risks: 2~4개
- financial_risks: 1~3개
- investment_cautions: 2~4개
- evidence: DART 근거에서 확인 가능한 내용만 2~4개
- bear_score: 투자 반대 강도를 1~5점으로 평가
"""

        output: BearOutput = self.structured_llm.invoke(prompt)
        output_dict = output.model_dump()

        state["docs"][AgentType.BEAR] = docs
        state["contexts"][AgentType.BEAR] = context
        state["bear_opinion"] = output_dict
        state["messages"].append(
            {
                "role": AgentType.BEAR,
                "content": output_dict,
            }
        )

        return state