# server/retrieval/dart/client.py

import os
import zipfile
import logging
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger(__name__)


class DartAPIError(Exception):
    pass


def get_dart_api_key() -> str:
    api_key = os.getenv("OPEN_DART_API_KEY")

    if not api_key:
        raise DartAPIError("OPEN_DART_API_KEY가 .env 파일에 설정되어 있지 않습니다.")

    return api_key


def download_disclosure_document(
    rcept_no: str,
    save_dir: str = "data/raw/dart",
    overwrite: bool = False,
) -> Path:
    api_key = get_dart_api_key()

    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    zip_path = save_dir / f"{rcept_no}.zip"
    extract_dir = save_dir / rcept_no

    if extract_dir.exists() and any(extract_dir.iterdir()) and not overwrite:
        logger.info("기존 DART 문서 재사용: %s", extract_dir)
        return extract_dir

    url = "https://opendart.fss.or.kr/api/document.xml"
    params = {
        "crtfc_key": api_key,
        "rcept_no": rcept_no,
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").lower()
    first_bytes = response.content[:500].lower()

    if "xml" in content_type or b"<status>" in first_bytes:
        raise DartAPIError(f"OpenDART API 오류 응답:\n{response.text[:1000]}")

    with open(zip_path, "wb") as f:
        f.write(response.content)

    extract_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
    except zipfile.BadZipFile as e:
        raise DartAPIError(f"다운로드된 파일이 ZIP 형식이 아닙니다: {zip_path}") from e

    logger.info("DART 문서 다운로드 및 압축 해제 완료: %s", extract_dir)

    return extract_dir


def download_business_report(
    rcept_no: str,
    save_dir: str = "data/raw/dart",
    overwrite: bool = False,
) -> Path:
    return download_disclosure_document(
        rcept_no=rcept_no,
        save_dir=save_dir,
        overwrite=overwrite,
    )