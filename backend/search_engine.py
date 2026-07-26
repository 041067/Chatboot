from collections import Counter
from pathlib import Path
import re
import fitz

from utils import normalize_text, tokenize, clean_pdf_text, redundancy_filter

CHUNK_WORDS = 240
CHUNK_OVERLAP = 45

NOISE_SECTIONS = [
    "sumario", "controle de revisoes", "referencias basicas",
    "referencias complementares", "sumário", "identificacao"
]

INTENT_EXPANSIONS = {
    "mercado": "mercado trabalho empregabilidade ocupacao vagas salario rais caged desenvolvedor sistemas tecnologia informacao empregos contratacao atividades profissionais atuacao demanda",
    "certificacao": "certificados diplomas diploma tecnico conclusao ensino medio certificacao reconhecimento titulo formacao",
    "competencias": "competencias profissionais capacidades tecnicas socioemocionais habilidades atitudes bases tecnologicas conhecimentos",
    "organizacao_curricular": "unidade curricular unidades curriculares organizacao curricular modulo basico modulo especifico ementa conteudos formativos disciplina materias grade",
    "objetivos": "objetivos justificativa finalidade formar profissionais capacidades habilitar objetivo proposito",
    "requisitos": "requisitos acesso matricula ingresso escolaridade idade ensino fundamental documentos processo seletivo",
    "duracao": "duracao carga horaria 1200 horas um ano meio tres semestres operacionalizacao periodo tempo",
    "avaliacao": "avaliacao recuperacao estudos frequencia notas aprovacao reprovacao criterios instrumentos avaliativos",
    "infraestrutura": "infraestrutura laboratorios informatica equipamentos salas ambiente aprendizagem recursos ferramentas software",
    "perfil": "perfil profissional conclusao competencias contexto trabalho atividades atribuicoes formado egresso",
}

INTENT_BOOST_TERMS = {
    "mercado": ["mercado de trabalho", "empregabilidade", "ocupacao", "atividades profissionais", "vagas", "desenvolvedor de sistemas", "rais", "caged"],
    "certificacao": ["certificados e diplomas", "certificacao", "diploma de tecnico", "conclusao do curso"],
    "competencias": ["competencias profissionais", "capacidades tecnicas", "socioemocionais", "bases tecnologicas"],
    "organizacao_curricular": ["unidade curricular", "organizacao curricular", "quadros de organizacao curricular", "modulo basico", "modulo especifico"],
    "objetivos": ["tem por objetivo habilitar", "objetivos", "justificativa e objetivo", "finalidade"],
    "requisitos": ["requisitos de acesso", "matricula", "ingresso"],
    "duracao": ["carga horaria total", "carga horaria de 1 200 horas", "1200 horas", "um ano e meio", "3 semestres", "operacionalizacao"],
    "avaliacao": ["avaliacao", "recuperacao de estudos", "instrumentos de avaliacao", "frequencia", "notas"],
    "infraestrutura": ["infraestrutura", "laboratorio de informatica", "ambiente pedagogico", "recursos didaticos"],
    "perfil": ["perfil profissional de conclusao", "perfil do egresso", "competencias profissionais"],
}


def split_into_chunks(text: str, page_num: int) -> list[dict]:
    words = text.split()
    if not words:
        return []

    chunks = []
    step = max(1, CHUNK_WORDS - CHUNK_OVERLAP)
    for start in range(0, len(words), step):
        chunk_words = words[start:start + CHUNK_WORDS]
        if not chunk_words:
            continue

        content = " ".join(chunk_words)
        terms = tokenize(content)
        chunks.append({
            "content": content,
            "page_num": page_num,
            "normalized": normalize_text(content),
            "terms": Counter(terms),
        })

        if start + CHUNK_WORDS >= len(words):
            break

    return chunks


def load_pdf_chunks(pdf_path: Path) -> list[dict]:
    if not pdf_path.exists():
        print(f"ERRO: PDF não encontrado em {pdf_path}")
        return []

    chunks = []
    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document, start=1):
            page_text = clean_pdf_text(page.get_text("text"))
            chunks.extend(split_into_chunks(page_text, page_index))

    print(f"PDF carregado: {len(chunks)} trechos indexados de {pdf_path.name}")
    return chunks


def expand_query(query: str, intent: str) -> list[str]:
    normalized_query = normalize_text(query)
    expanded_text = normalized_query

    expansion = INTENT_EXPANSIONS.get(intent, "")
    if expansion:
        expanded_text += f" {expansion}"

    return list(dict.fromkeys(tokenize(expanded_text)))


def intent_boost(normalized_chunk: str, intent: str) -> float:
    boost = 0.0
    terms = INTENT_BOOST_TERMS.get(intent, [])
    for term in terms:
        if normalize_text(term) in normalized_chunk:
            boost += 4.0
    return boost


def noise_penalty(normalized_chunk: str) -> float:
    return 8.0 if any(section in normalized_chunk for section in NOISE_SECTIONS) else 0.0


def search_pdf(query: str, intent: str, pdf_chunks: list[dict]) -> list[tuple[str, int, float, str]]:
    if not pdf_chunks:
        return []

    normalized_query = normalize_text(query)
    query_terms = expand_query(query, intent)
    if not query_terms:
        return []

    results = []
    unique_terms = set(query_terms)

    for chunk in pdf_chunks:
        term_counts = chunk["terms"]
        normalized_chunk = chunk["normalized"]
        matched_terms = [term for term in unique_terms if term_counts.get(term, 0) > 0]

        if not matched_terms:
            continue

        coverage = len(matched_terms) / max(len(unique_terms), 1)
        frequency_score = sum(min(term_counts[term], 5) for term in matched_terms)
        phrase_score = 3.0 if normalized_query and normalized_query in normalized_chunk else 0.0
        score = (coverage * 8.0) + (frequency_score * 0.6) + phrase_score
        score += intent_boost(normalized_chunk, intent)
        score -= noise_penalty(normalized_chunk)

        if score > 1.0:
            results.append((chunk["content"], chunk["page_num"], score, intent))

    results.sort(key=lambda x: x[2], reverse=True)
    results = results[:12]
    results = redundancy_filter(results)

    return results[:6]
