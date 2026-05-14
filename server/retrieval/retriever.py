# server/retrieval/retriever.py

from server.retrieval.vectorstore import load_vector_store
from server.config.settings import get_embeddings


def search_dart_documents(
    query: str,
    k: int = 5,
):
    embeddings = get_embeddings()

    vector_store = load_vector_store(
        embeddings=embeddings,
    )

    docs = vector_store.similarity_search(
        query=query,
        k=k,
    )

    return docs


def format_documents(docs):
    return "\n\n".join(
        f"[문서 {i + 1}]\n"
        f"metadata: {doc.metadata}\n"
        f"{doc.page_content}"
        for i, doc in enumerate(docs)
    )