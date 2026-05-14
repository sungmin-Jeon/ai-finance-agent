# server/retrieval/dart_preprocessor.py

from server.retrieval.dart.xml_loader import (
    load_xml_text,
    extract_raw_text_from_xml,
)
from server.retrieval.dart.text_cleaner import clean_raw_text
from server.retrieval.dart.section_parser import (
    split_toc_and_body,
    parse_toc,
    split_into_sections,
    split_into_subsections,
)


def preprocess_dart_xml(xml_path: str, base_metadata: dict):
    xml_text = load_xml_text(xml_path)
    raw_text = extract_raw_text_from_xml(xml_text)
    clean_text = clean_raw_text(raw_text)

    toc_text, body_text = split_toc_and_body(clean_text)
    toc_map = parse_toc(toc_text)

    section_docs = split_into_sections(
        body_text=body_text,
        toc_map=toc_map,
        base_metadata=base_metadata,
    )

    subsection_docs = split_into_subsections(
        section_docs=section_docs,
        toc_map=toc_map,
    )

    return subsection_docs