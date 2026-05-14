from typing import Any, Dict, List, TypedDict


class AgentType:
    BULL = "BULL_AGENT"
    BEAR = "BEAR_AGENT"
    RISK = "RISK_AGENT"
    REPORT = "REPORT_AGENT"

    @classmethod
    def to_korean(cls, role: str) -> str:
        if role == cls.BULL:
            return "투자 찬성"
        elif role == cls.BEAR:
            return "투자 반대"
        elif role == cls.RISK:
            return "리스크 판단"
        elif role == cls.REPORT:
            return "최종 리포트"
        return role


class InvestmentState(TypedDict):
    company_name: str
    question: str

    messages: List[Dict[str, Any]]
    docs: Dict[str, List]
    contexts: Dict[str, str]

    bull_opinion: Any
    bear_opinion: Any
    risk_opinion: Any
    final_report: Any