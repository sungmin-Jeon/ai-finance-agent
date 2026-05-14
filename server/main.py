# server/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routers.workflow import router as workflow_router


app = FastAPI(
    title="AI Finance Investment Agent",
    description="DART RAG 기반 Multi-Agent 투자 리서치 시스템",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflow_router)


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "AI Finance Investment Agent API is running",
    }