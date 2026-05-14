# server/routers/workflow.py

from typing import Any, Dict, Optional
import asyncio
import json
import uuid

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from server.workflow.graph import create_investment_graph
from server.workflow.state import InvestmentState


router = APIRouter(
    prefix="/api/v1/workflow",
    tags=["workflow"],
)


class InvestmentWorkflowRequest(BaseModel):
    company_name: str = Field(..., min_length=1, description="분석 대상 기업명")
    question: str = Field(..., min_length=5, description="투자 관련 질문")
    enable_rag: bool = True


class InvestmentWorkflowResponse(BaseModel):
    status: str = "success"
    session_id: str
    result: Any = None


def create_initial_state(
    company_name: str,
    question: str,
    session_id: str,
) -> InvestmentState:
    return {
        "session_id": session_id,
        "company_name": company_name,
        "question": question,
        "bull_opinion": {},
        "bear_opinion": {},
        "risk_opinion": {},
        "final_report": {},
        "docs": {},
        "contexts": {},
        "messages": [],
    }


@router.post("/investment", response_model=InvestmentWorkflowResponse)
def run_investment_workflow(request: InvestmentWorkflowRequest):
    session_id = str(uuid.uuid4())

    graph = create_investment_graph(enable_rag=request.enable_rag)

    initial_state = create_initial_state(
        company_name=request.company_name,
        question=request.question,
        session_id=session_id,
    )

    result = graph.invoke(initial_state)

    return InvestmentWorkflowResponse(
        session_id=session_id,
        result=result,
    )


async def investment_stream_generator(
    graph,
    initial_state: InvestmentState,
):
    for chunk in graph.stream(
        initial_state,
        stream_mode="updates",
    ):
        if not chunk:
            continue

        for node_name, node_state in chunk.items():
            event_data = {
                "type": "update",
                "node": node_name,
                "data": {
                    "company_name": node_state.get("company_name"),
                    "question": node_state.get("question"),
                    "bull_opinion": node_state.get("bull_opinion"),
                    "bear_opinion": node_state.get("bear_opinion"),
                    "risk_opinion": node_state.get("risk_opinion"),
                    "final_report": node_state.get("final_report"),
                    "messages": node_state.get("messages", []),
                },
            }

            yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.01)

    yield f"data: {json.dumps({'type': 'end', 'data': {}}, ensure_ascii=False)}\n\n"


@router.post("/investment/stream")
async def stream_investment_workflow(request: InvestmentWorkflowRequest):
    session_id = str(uuid.uuid4())

    graph = create_investment_graph(enable_rag=request.enable_rag)

    initial_state = create_initial_state(
        company_name=request.company_name,
        question=request.question,
        session_id=session_id,
    )

    return StreamingResponse(
        investment_stream_generator(graph, initial_state),
        media_type="text/event-stream",
    )