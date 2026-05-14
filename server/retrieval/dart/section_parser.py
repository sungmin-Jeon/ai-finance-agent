# server/retrieval/dart_section_parser.py

import re
from collections import defaultdict

from langchain_core.documents import Document


def split_toc_and_body(clean_text: str):
    matches = list(
        re.finditer(r"^I\. 회사의 개요$", clean_text, flags=re.MULTILINE)
    )

    if len(matches) < 2:
        raise ValueError("'I. 회사의 개요'가 2번 이상 발견되지 않았습니다.")

    toc_start = matches[0].start()
    body_start = matches[1].start()

    toc_text = clean_text[toc_start:body_start].strip()
    body_text = clean_text[body_start:].strip()

    return toc_text, body_text


def parse_toc(toc_text: str) -> dict:
    section_pattern = r"^(?:I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII)\. .+$"
    subsection_pattern = r"^[1-9](?:-\d+)?\. .+$"

    toc_map = defaultdict(list)
    current_section = None

    for line in toc_text.splitlines():
        line = line.strip()

        if not line or set(line) == {"-"}:
            continue

        if re.match(section_pattern, line):
            current_section = line
            toc_map[current_section] = []
            continue

        if current_section and re.match(subsection_pattern, line):
            toc_map[current_section].append(line)

    return dict(toc_map)


def split_into_sections(
    body_text: str,
    toc_map: dict,
    base_metadata: dict,
) -> list[Document]:
    section_titles = list(toc_map.keys())

    section_pattern = (
        r"^(" + "|".join(re.escape(title) for title in section_titles) + r")$"
    )

    matches = list(re.finditer(section_pattern, body_text, flags=re.MULTILINE))

    section_docs = []

    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body_text)

        section_title = match.group().strip()
        section_text = body_text[start:end].strip()

        section_docs.append(
            Document(
                page_content=section_text,
                metadata={
                    **base_metadata,
                    "section": section_title,
                },
            )
        )

    return section_docs


def split_into_subsections(
    section_docs: list[Document],
    toc_map: dict,
) -> list[Document]:
    subsection_docs = []

    for section_doc in section_docs:
        section_title = section_doc.metadata["section"]
        section_text = section_doc.page_content
        subsection_titles = toc_map.get(section_title, [])

        if not subsection_titles:
            subsection_docs.append(
                Document(
                    page_content=section_text,
                    metadata={
                        **section_doc.metadata,
                        "subsection": None,
                        "section_path": section_title,
                    },
                )
            )
            continue

        subsection_pattern = (
            r"^(" + "|".join(re.escape(title) for title in subsection_titles) + r")$"
        )

        matches = list(
            re.finditer(subsection_pattern, section_text, flags=re.MULTILINE)
        )

        if not matches:
            subsection_docs.append(
                Document(
                    page_content=section_text,
                    metadata={
                        **section_doc.metadata,
                        "subsection": None,
                        "section_path": section_title,
                    },
                )
            )
            continue

        for idx, match in enumerate(matches):
            start = match.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(section_text)

            subsection_title = match.group().strip()
            subsection_text = section_text[start:end].strip()

            subsection_docs.append(
                Document(
                    page_content=subsection_text,
                    metadata={
                        **section_doc.metadata,
                        "subsection": subsection_title,
                        "section_path": f"{section_title} > {subsection_title}",
                    },
                )
            )

    return subsection_docs