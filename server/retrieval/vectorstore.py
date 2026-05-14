# server/retrieval/vector_store.py

from pathlib import Path
from typing import List, Optional

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter


DART_VECTORSTORE_PATH = "data/vectorstore/dart/sk_hynix"

def split_documents(
    docs: List[Document],
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)


def build_vector_store(
    docs: List[Document],
    embeddings,
    save_path: Optional[str] = None,
    batch_size: int = 50,
) -> FAISS:
    if not docs:
        raise ValueError("docs가 비어 있습니다.")

    vector_store = None

    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        print(f"임베딩 중: {i} ~ {i + len(batch)} / {len(docs)}")

        if vector_store is None:
            vector_store = FAISS.from_documents(
                documents=batch,
                embedding=embeddings,
            )
        else:
            vector_store.add_documents(batch)

    if save_path:
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)
        vector_store.save_local(str(save_dir))

    return vector_store


def load_vector_store(
    embeddings,
    load_path: str = DART_VECTORSTORE_PATH,
) -> FAISS:
    return FAISS.load_local(
        folder_path=load_path,
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )