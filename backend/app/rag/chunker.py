from collections import Counter
from pathlib import Path
from typing import Optional
import fitz

from app.rag.ranking import rank_by_semantic_relevance, detect_section

CHUNK_WORDS = 240
CHUNK_OVERLAP = 45

NOISE_SECTIONS = [
    "sumario", "controle de revisoes", "referencias basicas",
    "referencias complementares", "sumário", "identificacao",
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

STOPWORDS = {
    "a", "ao", "aos", "as", "com", "como", "da", "das", "de", "do", "dos",
    "e", "em", "eu", "me", "na", "nas", "no", "nos", "o", "os", "ou", "para",
    "por", "qual", "quais", "que", "sobre", "um", "uma", "voce", "tem", "sao",
    "ser", "esta", "esse", "essa", "isso", "curso", "tecnico", "desenvolvimento",
    "sistemas", "senai", "jau",
}


def normalize_text(text: str) -> str:
    import unicodedata, re
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    return [
        t for t in normalize_text(text).split()
        if len(t) > 2 and t not in STOPWORDS
    ]


def clean_pdf_text(text: str) -> str:
    import re
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


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
        normalized = normalize_text(content)
        chunks.append({
            "content": content,
            "page_num": page_num,
            "normalized": normalized,
            "terms": Counter(terms),
            "section": detect_section(normalized),
        })
        if start + CHUNK_WORDS >= len(words):
            break
    return chunks


def load_pdf_chunks(pdf_path: Path) -> list[dict]:
    if not pdf_path.exists():
        print(f"ERRO: PDF nao encontrado em {pdf_path}")
        return []
    chunks = []
    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document, start=1):
            page_text = clean_pdf_text(page.get_text("text"))
            chunks.extend(split_into_chunks(page_text, page_index))
    print(f"PDF carregado: {len(chunks)} trechos indexados de {pdf_path.name}")
    return chunks


def expand_query(query: str, intent: str) -> list[str]:
    expanded_text = normalize_text(query)
    expansion = INTENT_EXPANSIONS.get(intent, "")
    if expansion:
        expanded_text += f" {expansion}"
    return list(dict.fromkeys(tokenize(expanded_text)))


def search_pdf_chunks(
    query: str,
    intent: str,
    pdf_chunks: list[dict],
    top_k: int = 12,
) -> list[tuple[str, int, float, str, Optional[str]]]:
    if not pdf_chunks:
        return []
    query_terms = expand_query(query, intent)
    if not query_terms:
        return []
    results = []
    for chunk in pdf_chunks:
        score = rank_by_semantic_relevance(
            query_terms, chunk, intent,
            INTENT_BOOST_TERMS, NOISE_SECTIONS,
        )
        if score > 1.0:
            results.append((
                chunk["content"],
                chunk["page_num"],
                score,
                intent,
                chunk.get("section"),
            ))
    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_k]
