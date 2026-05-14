# server/retrieval/text_cleaner.py

import re


def clean_raw_text(raw_text: str) -> str:
    lines = [line.strip() for line in raw_text.split("\n")]
    lines = [line for line in lines if line]

    clean_text = "\n".join(lines)
    clean_text = re.sub(r"\n{2,}", "\n", clean_text)

    return clean_text