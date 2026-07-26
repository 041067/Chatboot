from difflib import SequenceMatcher
from typing import Optional


def deduplicate_chunks(chunks: list[tuple[str, int, float, str, Optional[str]]], threshold: float = 0.75) -> list[tuple[str, int, float, str, Optional[str]]]:
    if not chunks:
        return chunks
    filtered = [chunks[0]]
    for item in chunks[1:]:
        content = item[0]
        is_redundant = False
        for kept in filtered:
            similarity = SequenceMatcher(None, content, kept[0]).ratio()
            if similarity >= threshold:
                is_redundant = True
                break
        if not is_redundant:
            filtered.append(item)
    return filtered


def merge_similar_chunks(chunks: list[tuple[str, int, float, str, Optional[str]]], merge_threshold: float = 0.65) -> list[tuple[str, int, float, str, Optional[str]]]:
    if not chunks:
        return chunks
    merged = []
    used = set()
    for i, a in enumerate(chunks):
        if i in used:
            continue
        group = [a]
        used.add(i)
        for j, b in enumerate(chunks):
            if j in used:
                continue
            sim = SequenceMatcher(None, a[0], b[0]).ratio()
            if sim >= merge_threshold:
                group.append(b)
                used.add(j)
        if len(group) > 1:
            merged_content = _merge_texts([g[0] for g in group])
            avg_score = sum(g[2] for g in group) / len(group)
            pages = sorted(set(g[1] for g in group))
            merged.append((
                merged_content,
                pages[0],
                avg_score,
                a[3],
                a[4],
            ))
        else:
            merged.append(a)
    return merged


def _merge_texts(texts: list[str]) -> str:
    sentences = []
    seen = set()
    for text in texts:
        for sentence in text.replace("\n", " ").split(". "):
            stripped = sentence.strip()
            if not stripped:
                continue
            normalized = stripped.lower().strip()
            if normalized not in seen:
                seen.add(normalized)
                sentences.append(stripped)
    return ". ".join(sentences) + "." if sentences else texts[0]


def order_by_relevance(chunks: list[tuple]) -> list[tuple]:
    return sorted(chunks, key=lambda x: x[2], reverse=True)


def separate_by_subject(chunks: list[tuple]) -> dict[str, list[tuple]]:
    groups: dict[str, list[tuple]] = {}
    for item in chunks:
        subject = item[4] or "Informacoes Gerais"
        if subject not in groups:
            groups[subject] = []
        groups[subject].append(item)
    for subject in groups:
        groups[subject] = sorted(groups[subject], key=lambda x: x[2], reverse=True)
    return groups
