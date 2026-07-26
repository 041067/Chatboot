import re
from utils import normalize_text

INTENT_PATTERNS = {
    "mercado": [
        "mercado", "trabalho", "emprego", "empregabilidade", "carreira",
        "salario", "salarial", "vagas", "contratar", "empresa", "profissao",
        "ocupacao", "rais", "caged", "qbq", "contratacao"
    ],
    "certificacao": [
        "certificacao", "certificado", "diploma", "titulo", "conclusao",
        "formado", "formatura", "reconhecimento", "mec", "validade"
    ],
    "competencias": [
        "competencia", "habilidade", "capacidade", "socioemocional",
        "tecnica", "soft skill", "hard skill", "aprender", "desenvolver"
    ],
    "organizacao_curricular": [
        "disciplina", "materia", "grade", "curriculo", "modulo",
        "unidade curricular", "ementa", "conteudo", "aula", "componente",
        "organizacao curricular", "curriculo"
    ],
    "objetivos": [
        "objetivo", "finalidade", "proposito", "meta", "justificativa",
        "formar", "capacitar", "proporcionar"
    ],
    "requisitos": [
        "requisito", "ingressar", "entrar", "matricula", "inscricao",
        "escolaridade", "idade", " documento", "vestibular", "processo seletivo"
    ],
    "duracao": [
        "duracao", "dura", "tempo", "carga horaria", "horas", "semestre",
        "ano", "mes", "periodo", "quanto tempo"
    ],
    "avaliacao": [
        "avaliacao", "prova", "nota", "notas", "recuperacao", "reprovacao",
        "aprovacao", "media", "frequencia", "critério de avaliacao"
    ],
    "infraestrutura": [
        "infraestrutura", "laboratorio", "sala", "equipamento", "computador",
        "software", "ferramenta", "ambiente", "recurso", "instalacao"
    ],
    "perfil": [
        "perfil", "profissional", "formado", "egresso", "atuação",
        "formacao", "sair", "preparado", "carreira"
    ],
}

INTENT_LABELS = {
    "mercado": "Mercado de Trabalho",
    "certificacao": "Certificacao e Diplomas",
    "competencias": "Competencias Profissionais",
    "organizacao_curricular": "Organizacao Curricular",
    "objetivos": "Objetivos do Curso",
    "requisitos": "Requisitos de Acesso",
    "duracao": "Duracao e Carga Horaria",
    "avaliacao": "Processos de Avaliacao",
    "infraestrutura": "Infraestrutura e Recursos",
    "perfil": "Perfil Profissional de Conclusao",
}


def classify_intent(question: str) -> str:
    normalized = normalize_text(question)
    scores = {}

    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        n_patterns = len(patterns)
        for pattern in patterns:
            if pattern in normalized:
                score += 1
        if n_patterns > 0:
            scores[intent] = score / n_patterns

    if not scores or max(scores.values()) == 0:
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(r'\b' + re.escape(pattern.split()[0]) + r'\b', normalized):
                    scores[intent] = scores.get(intent, 0) + 0.5

    if not scores or max(scores.values()) == 0:
        return "objetivos"

    return max(scores, key=scores.get)


def get_intent_group_label(intent: str) -> str:
    return INTENT_LABELS.get(intent, "Informacoes Gerais")


SIMPLICITY_KEYWORDS = ["quanto", "quando", "onde", "qtd", "nmero", "data",
                       "hora", "carga horaria", "quantas horas"]
COMPLEXITY_HIGH = ["analise", "compare", "discuta", "avalie", "relacione",
                   "explique em detalhes", "explore profundamente",
                   "em profundidade", "todos os aspectos"]
STYLE_OBJECTIVE = ["quanto", "quando", "onde", "qtd", "nmero", "data",
                   "hora", "carga horaria", "quantas horas", "exatamente"]
STYLE_EXPLANATORY = ["como", "por que", "significa", "explica", "defina",
                     "describe", "o que", "porquê", "explicar", "proporcionar"]
DEPTH_DETAILED = ["analise", "compare", "discuta", "avalie", "relacione",
                  "explique em detalhes", "explore profundamente",
                  "caracteriza", "em profundidade",
                  "compreensão ampla", "todos os aspectos"]


def analyze_user_question(question: str) -> dict:
    normalized = normalize_text(question)
    intent = classify_intent(question)

    complexity = "média"
    if any(k in normalized for k in SIMPLICITY_KEYWORDS):
        complexity = "baixa"
    elif any(k in normalized for k in COMPLEXITY_HIGH):
        complexity = "alta"

    answer_style = "explicativa"
    if any(k in normalized for k in STYLE_OBJECTIVE):
        answer_style = "objetiva"
    elif any(k in normalized for k in STYLE_EXPLANATORY):
        answer_style = "explicativa"

    expected_depth = {"baixa": "curta", "média": "normal", "alta": "detalhada"}[complexity]
    if any(k in normalized for k in DEPTH_DETAILED):
        expected_depth = "detalhada"

    word_count = len(normalized.split())
    if word_count < 3:
        complexity = "baixa"
    elif word_count > 8:
        complexity = "alta"
    expected_depth = {"baixa": "curta", "média": "normal", "alta": "detalhada"}.get(complexity, "normal")

    if answer_style == "explicativa" and expected_depth == "curta":
        expected_depth = "normal"

    if "mercado" in normalized or "certificado" in normalized or "módulo" in normalized:
        answer_style = "explicativa"
        expected_depth = "detalhada"

    if "porquê" in normalized or "compare" in normalized or "relacione" in normalized:
        answer_style = "explicativa"
        expected_depth = "detalhada"

    return {
        "intent": intent,
        "complexity": complexity,
        "answer_style": answer_style,
        "expected_depth": expected_depth,
    }
