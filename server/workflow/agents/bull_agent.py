from typing import List, Literal

from pydantic import BaseModel, Field

from server.config.settings import get_llm
from server.tools.dart_tool import DartTool
from server.workflow.state import InvestmentState, AgentType


class BullOutput(BaseModel):
    agent: Literal["BULL_AGENT"] = "BULL_AGENT"
    summary: str = Field(
        description="투자 찬성 관점의 핵심 요약"
    )
    core_thesis: str = Field(
        description="가장 중요한 투자 찬성 논리"
    )
    growth_drivers: List[str] = Field(
        description="주요 성장 요인 목록"
    )
    competitive_advantages: List[str] = Field(
        description="사업 경쟁력 및 진입장벽"
    )
    profitability_catalysts: List[str] = Field(
        description="수익성 개선 요인"
    )
    investment_attractions: List[str] = Field(
        description="투자 매력 포인트"
    )
    evidence: List[str] = Field(
        description="DART 근거 기반 핵심 문장 요약"
    )
    bull_score: int = Field(
        description="투자 매력도 점수 (1~5)",
        ge=1,
        le=5,
    )


class BullAgent:
    def __init__(self, k: int = 5):
        self.llm = get_llm(temperature=0.2)
        self.structured_llm = self.llm.with_structured_output(BullOutput)
        self.dart_tool = DartTool(k=k)

    def run(self, state: InvestmentState) -> InvestmentState:
        company_name = state["company_name"]
        question = state["question"]

        docs, context = self.dart_tool.search(
            company_name=company_name,
            question=question,
            mode="bull",
        )

        prompt = f"""
당신은 투자 찬성 관점의 금융 애널리스트입니다.

[기업]
{company_name}

[사용자 질문]
{question}

[DART 근거]
{context}

역할:
- DART 근거를 바탕으로 투자 찬성 논리를 작성하세요.
- 성장 요인, 사업 경쟁력, 수익성 개선 가능성을 중심으로 분석하세요.
- DART 문서에 있는 내용만 사용하세요.
- 문서에 없는 내용은 추측하지 마세요.
- 모든 응답은 BullOutput 스키마에 맞춰 작성하세요.

작성 기준:
- summary: 전체 찬성 논리를 2문장 이내로 요약
- core_thesis: 가장 중요한 투자 찬성 논리 1개
- growth_drivers: 2~5개
- competitive_advantages: 2~5개
- profitability_catalysts: 1~4개
- investment_attractions: 2~5개
- evidence: DART 근거에서 확인 가능한 내용만 2~5개
- bull_score: 투자 매력도를 1~5점으로 평가
"""

        output: BullOutput = self.structured_llm.invoke(prompt)
        output_dict = output.model_dump()

        state["docs"][AgentType.BULL] = docs
        state["contexts"][AgentType.BULL] = context
        state["bull_opinion"] = output_dict
        state["messages"].append(
            {
                "role": AgentType.BULL,
                "content": output_dict,
            }
        )

        return state