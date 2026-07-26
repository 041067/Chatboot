import re
import unicodedata
from difflib import SequenceMatcher

STOPWORDS = {
    "a", "ao", "aos", "as", "com", "como", "da", "das", "de", "do", "dos",
    "e", "em", "eu", "me", "na", "nas", "no", "nos", "o", "os", "ou", "para",
    "por", "qual", "quais", "que", "sobre", "um", "uma", "voce", "tem", "sao",
    "ser", "esta", "esse", "essa", "isso", "curso", "tecnico", "desenvolvimento",
    "sistemas", "senai", "jau",
}

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    return [
        token for token in normalize_text(text).split()
        if len(token) > 2 and token not in STOPWORDS
    ]


def clean_pdf_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def redundancy_filter(results: list[tuple], threshold: float = 0.80) -> list[tuple]:
    if not results:
        return results
    filtered = [results[0]]
    for item in results[1:]:
        content = item[0]
        is_redundant = False
        for kept in filtered:
            kept_content = kept[0]
            similarity = SequenceMatcher(None, content, kept_content).ratio()
            if similarity >= threshold:
                is_redundant = True
                break
        if not is_redundant:
            filtered.append(item)
    return filtered


def summarize_response(response: str, max_chars: int = 200) -> str:
    if len(response) <= max_chars:
        return response
    return response[:max_chars].rsplit(" ", 1)[0] + "..."
