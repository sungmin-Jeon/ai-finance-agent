# server/workflow/graph.py

from pathlib import Path

from langgraph.graph import StateGraph, END

from server.workflow.state import InvestmentState, AgentType
from server.workflow.agents.bull_agent import BullAgent
from server.workflow.agents.bear_agent import BearAgent
from server.workflow.agents.risk_agent import RiskAgent
from server.workflow.agents.report_agent import ReportAgent


def create_investment_graph(enable_rag: bool = True):
    workflow = StateGraph(InvestmentState)

    k_value = 5 if enable_rag else 0

    bull_agent = BullAgent(k=k_value)
    bear_agent = BearAgent(k=k_value)
    risk_agent = RiskAgent(k=k_value)
    report_agent = ReportAgent(k=k_value)

    # 노드 등록
    workflow.add_node(AgentType.BULL, bull_agent.run)
    workflow.add_node(AgentType.BEAR, bear_agent.run)
    workflow.add_node(AgentType.RISK, risk_agent.run)
    workflow.add_node(AgentType.REPORT, report_agent.run)

    # 시작 노드
    workflow.set_entry_point(AgentType.BULL)

    # 엣지 연결
    workflow.add_edge(AgentType.BULL, AgentType.BEAR)
    workflow.add_edge(AgentType.BEAR, AgentType.RISK)
    workflow.add_edge(AgentType.RISK, AgentType.REPORT)
    workflow.add_edge(AgentType.REPORT, END)

    return workflow.compile()


def save_graph_image(
    output_path: str = "artifacts/investment_graph.png",
    enable_rag: bool = True,
):
    print("[1/4] Creating graph...")
    graph = create_investment_graph(enable_rag=enable_rag)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Mermaid 텍스트 저장
    print("[2/4] Saving Mermaid source...")
    mermaid_text = graph.get_graph().draw_mermaid()

    mermaid_file = output_file.with_suffix(".md")
    with open(mermaid_file, "w", encoding="utf-8") as f:
        f.write(mermaid_text)

    print(f"Mermaid source saved to: {mermaid_file}")

    # PNG 생성
    print("[3/4] Rendering PNG...")
    try:
        png_bytes = graph.get_graph().draw_mermaid_png()

        with open(output_file, "wb") as f:
            f.write(png_bytes)

        print(f"Graph image saved to: {output_file}")

    except Exception as e:
        print(f"PNG rendering failed: {e}")
        print("Mermaid source file was saved successfully.")

    print("[4/4] Done.")


if __name__ == "__main__":
    save_graph_image()