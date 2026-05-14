# server/retrieval/file_utils.py

from pathlib import Path


def find_xml_files(directory: str | Path) -> list[Path]:
    """압축 해제 폴더에서 XML 파일 목록을 반환한다."""

    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"폴더가 존재하지 않습니다: {directory}")

    xml_files = sorted(directory.glob("*.xml"))

    if not xml_files:
        raise FileNotFoundError(
            f"XML 파일을 찾을 수 없습니다: {directory}"
        )

    return xml_files


def get_main_xml_file(
    directory: str | Path,
    rcept_no: str | None = None,
) -> Path:
    """
    메인 XML 파일을 선택한다.
    일반적으로 {rcept_no}.xml 형식을 우선 사용한다.
    """

    directory = Path(directory)

    if rcept_no:
        candidate = directory / f"{rcept_no}.xml"
        if candidate.exists():
            return candidate

    xml_files = find_xml_files(directory)

    return xml_files[0]