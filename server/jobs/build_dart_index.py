import logging

from server.config.settings import get_embeddings
from server.retrieval.dart.client import download_business_report
from server.retrieval.dart.file_utils import get_main_xml_file
from server.retrieval.dart.preprocessor import preprocess_dart_xml
from server.retrieval.vectorstore import split_documents, build_vector_store


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    rcept_no = "20260317000635"

    base_metadata = {
        "company": "SK하이닉스",
        "corp_code": "00164779",
        "stock_code": "000660",
        "report_nm": "사업보고서 (2025.12)",
        "rcept_no": rcept_no,
        "rcept_dt": "20260317",
        "source": "OpenDART",
    }

    extract_dir = download_business_report(rcept_no=rcept_no)
    xml_path = get_main_xml_file(extract_dir, rcept_no=rcept_no)

    base_metadata["file_path"] = str(xml_path)

    docs = preprocess_dart_xml(
        xml_path=str(xml_path),
        base_metadata=base_metadata,
    )

    chunks = split_documents(docs)

    logger.info("XML 경로: %s", xml_path)
    logger.info("생성된 Document 개수: %d", len(docs))
    logger.info("생성된 Chunk 개수: %d", len(chunks))

    if docs:
        print("\n[첫 번째 Document metadata]")
        print(docs[0].metadata)

        print("\n[첫 번째 Document 내용 일부]")
        print(docs[0].page_content[:1000])

    embeddings = get_embeddings()

    build_vector_store(
        chunks=chunks,
        embeddings=embeddings,
        save_path="data/vectorstore/dart/sk_hynix",
    )

    logger.info("FAISS 벡터스토어 저장 완료")


if __name__ == "__main__":
    main()