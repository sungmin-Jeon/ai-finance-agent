from langchain_core.tools import tool

from server.retrieval.retriever import (
    search_dart_documents,
    format_documents,
)


class DartTool:
    def __init__(self, k: int = 5):
        self.k = k

    def search(
        self,
        company_name: str,
        question: str,
        mode: str = "general",
    ):
        query = self._build_query(
            company_name=company_name,
            question=question,
            mode=mode,
        )

        docs = search_dart_documents(
            query=query,
            k=self.k,
        )

        context = (
            format_documents(docs)
            if docs
            else "DART 사업보고서 관련 문서를 찾지 못했습니다."
        )

        return docs, context

    def _build_query(
        self,
        company_name: str,
        question: str,
        mode: str,
    ) -> str:
        query_map = {
            "bull": (
                f"{company_name} 성장 요인 HBM AI 반도체 경쟁력 "
                f"수익성 투자 확대 사업 기회 {question}"
            ),
            "bear": (
                f"{company_name} 리스크 경쟁 심화 공급 과잉 "
                f"고객 집중도 실적 변동성 재무 부담 {question}"
            ),
            "risk": (
                f"{company_name} 사업 위험 시장 위험 재무 위험 "
                f"지정학 리스크 투자 위험 {question}"
            ),
            "report": (
                f"{company_name} 주요 사업 성장 요인 리스크 "
                f"투자 판단 종합 분석 {question}"
            ),
            "general": (
                f"{company_name} 주요 사업 성장 요인 리스크 "
                f"최근 투자 이슈 {question}"
            ),
        }

        return query_map.get(mode, query_map["general"])


@tool
def search_dart_tool(
    company_name: str,
    question: str,
    mode: str = "general",
) -> str:
    """
    DART 사업보고서 벡터스토어를 검색하여
    기업의 주요 사업, 성장 요인, 리스크 관련 근거를 반환합니다.

    Args:
        company_name: 기업명 (예: SK하이닉스)
        question: 사용자의 질문
        mode: 검색 모드
            - bull: 성장 요인 중심
            - bear: 리스크 중심
            - risk: 투자 위험 중심
            - report: 종합 리포트용
            - general: 일반 검색

    Returns:
        검색된 DART 문서 내용을 문자열로 반환합니다.
    """
    dart_tool = DartTool(k=5)
    _, context = dart_tool.search(
        company_name=company_name,
        question=question,
        mode=mode,
    )
    return context