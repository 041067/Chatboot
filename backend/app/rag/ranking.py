from typing import Optional


SECTION_KEYWORDS = {
    "identificacao": ["identificacao do curso", "identificacao", "eixo tecnologico"],
    "objetivos": ["objetivos", "justificativa", "finalidade"],
    "requisitos": ["requisitos de acesso", "matricula", "ingresso", "processo seletivo"],
    "organizacao_curricular": ["organizacao curricular", "unidade curricular", "quadro de organizacao"],
    "competencias": ["competencias profissionais", "bases tecnologicas", "capacidades"],
    "perfil": ["perfil profissional", "perfil do egresso", "competencias profissionais"],
    "mercado": ["mercado de trabalho", "empregabilidade", "ocupacao", "atividades"],
    "avaliacao": ["avaliacao", "recuperacao de estudos", "instrumentos de avaliacao"],
    "infraestrutura": ["infraestrutura", "laboratorio", "ambiente pedagogico"],
    "certificacao": ["certificacao", "certificados", "diplomas", "conclusao"],
    "duracao": ["operacionalizacao", "carga horaria", "duracao"],
}


def detect_section(normalized_chunk: str) -> Optional[str]:
    for section, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            if kw in normalized_chunk:
                return section
    return None


def rank_by_semantic_relevance(
    query_terms: list[str],
    chunk: dict,
    intent: str,
    intent_boost_terms: dict[str, list[str]],
    noise_sections: list[str],
) -> float:
    normalized_chunk = chunk["normalized"]
    term_counts = chunk["terms"]
    unique_terms = set(query_terms)
    matched_terms = [t for t in unique_terms if term_counts.get(t, 0) > 0]

    if not matched_terms:
        return 0.0

    coverage = len(matched_terms) / max(len(unique_terms), 1)
    frequency_score = sum(min(term_counts[t], 5) for t in matched_terms)

    query_text = " ".join(query_terms)
    phrase_score = 5.0 if query_text and query_text in normalized_chunk else 0.0

    score = (coverage * 10.0) + (frequency_score * 0.8) + phrase_score

    boost_terms = intent_boost_terms.get(intent, [])
    for term in boost_terms:
        if normalize_text_internal(term) in normalized_chunk:
            score += 6.0

    section = detect_section(normalized_chunk)
    if section == intent:
        score += 8.0

    section_penalty = 10.0 if any(s in normalized_chunk for s in noise_sections) else 0.0
    score -= section_penalty

    title_weight = _title_weight(normalized_chunk)
    score *= title_weight

    return max(score, 0.0)


def _title_weight(normalized_chunk: str) -> float:
    title_indicators = [
        "plano de curso", "curso tecnico", "desenvolvimento de sistemas",
        "eixo tecnologico", "informacao e comunicacao",
    ]
    for indicator in title_indicators:
        if indicator in normalized_chunk:
            return 1.0
    words = normalized_chunk.split()
    if len(words) < 15:
        return 0.7
    return 1.0


def normalize_text_internal(text: str) -> str:
    import unicodedata, re
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()
