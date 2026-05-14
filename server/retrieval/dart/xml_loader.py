# server/retrieval/xml_loader.py

from bs4 import BeautifulSoup


def load_xml_text(xml_path: str) -> str:
    with open(xml_path, "r", encoding="utf-8") as f:
        return f.read()

def extract_raw_text_from_xml(xml_text: str) -> str:
    soup = BeautifulSoup(xml_text, "xml")
    return soup.get_text(separator="\n")