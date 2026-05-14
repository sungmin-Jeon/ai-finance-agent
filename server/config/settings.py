# server/config/settings.py

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# .env 로드
load_dotenv()


class Settings(BaseSettings):
    """프로젝트 전역 설정"""

    # =========================
    # OpenAI
    # =========================
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"

    # =========================
    # Langfuse (선택)
    # =========================
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_HOST: str | None = None

    # =========================
    # App Settings
    # =========================
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Finance Agent"

    # =========================
    # CORS
    # =========================
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # =========================
    # Directories
    # =========================
    DATA_DIR: str = "data"
    RAW_DIR: str = "data/raw"
    VECTORSTORE_DIR: str = "data/vectorstore"

    # =========================
    # Pydantic Settings
    # =========================
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    # =========================
    # LLM
    # =========================
    def get_llm(
        self,
        model_name: str | None = None,
        temperature: float = 0.7,
        streaming: bool = False,
    ):
        return ChatOpenAI(
            model=model_name or self.OPENAI_MODEL,
            api_key=self.OPENAI_API_KEY,
            temperature=temperature,
            streaming=streaming,
        )

    # =========================
    # Embeddings
    # =========================
    def get_embeddings(self):
        return OpenAIEmbeddings(
            model=self.OPENAI_EMBEDDING_MODEL,
            api_key=self.OPENAI_API_KEY,
        )


# 전역 설정 객체
settings = Settings()


# 편의 함수
def get_llm(
    model_name: str | None = None,
    temperature: float = 0.7,
    streaming: bool = False,
):
    return settings.get_llm(
        model_name=model_name,
        temperature=temperature,
        streaming=streaming,
    )


def get_embeddings():
    return settings.get_embeddings()