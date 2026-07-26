import re
from dataclasses import dataclass, field
from typing import Optional

STOPWORDS_SET = {
    "a", "ao", "aos", "as", "com", "como", "da", "das", "de", "do", "dos",
    "e", "em", "eu", "me", "na", "nas", "no", "nos", "o", "os", "ou", "para",
    "por", "qual", "quais", "que", "sobre", "um", "uma", "voce", "tem", "sao",
    "ser", "esta", "esse", "essa", "isso", "curso", "tecnico", "desenvolvimento",
    "sistemas", "senai", "jau",
}


def normalize_text(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


INTENT_PATTERNS = {
    "mercado": [
        "mercado", "trabalho", "emprego", "empregabilidade", "carreira",
        "salario", "salarial", "vagas", "contratar", "empresa", "profissao",
        "ocupacao", "rais", "caged", "qbq", "contratacao",
    ],
    "certificacao": [
        "certificacao", "certificado", "diploma", "titulo", "conclusao",
        "formado", "formatura", "reconhecimento", "mec", "validade",
    ],
    "competencias": [
        "competencia", "habilidade", "capacidade", "socioemocional",
        "tecnica", "soft skill", "hard skill", "aprender", "desenvolver",
    ],
    "organizacao_curricular": [
        "disciplina", "materia", "grade", "curriculo", "modulo",
        "unidade curricular", "ementa", "conteudo", "aula", "componente",
        "organizacao curricular", "curriculo",
    ],
    "objetivos": [
        "objetivo", "finalidade", "proposito", "meta", "justificativa",
        "formar", "capacitar", "proporcionar",
    ],
    "requisitos": [
        "requisito", "ingressar", "entrar", "matricula", "inscricao",
        "escolaridade", "idade", " documento", "vestibular", "processo seletivo",
    ],
    "duracao": [
        "duracao", "dura", "tempo", "carga horaria", "horas", "semestre",
        "ano", "mes", "periodo", "quanto tempo",
    ],
    "avaliacao": [
        "avaliacao", "prova", "nota", "notas", "recuperacao", "reprovacao",
        "aprovacao", "media", "frequencia", "criterio de avaliacao",
    ],
    "infraestrutura": [
        "infraestrutura", "laboratorio", "sala", "equipamento", "computador",
        "software", "ferramenta", "ambiente", "recurso", "instalacao",
    ],
    "perfil": [
        "perfil", "profissional", "formado", "egresso", "atuacao",
        "formacao", "sair", "preparado", "carreira",
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

QUESTION_TYPE_PATTERNS = {
    "factual": ["quanto", "quando", "onde", "qual a carga", "quantas horas", "qual o prazo"],
    "conceitual": ["o que", "o que e", "defina", "significa", "conceito"],
    "procedural": ["como", "como funciona", "como fazer", "quais sao as etapas"],
    "comparativa": ["compare", "diferenca", "qual a diferenca", "versus", "melhor"],
    "exploratoria": ["explique", "detalhe", "analise", "discuta", "relacione", "explore"],
}


@dataclass
class AnalysisResult:
    intent: str
    intent_label: str
    complexity: str
    answer_style: str
    expected_depth: str
    question_type: str = "factual"


class QuestionAnalyzer:
    def analyze(self, question: str) -> AnalysisResult:
        normalized = normalize_text(question)
        intent = self._classify_intent(question)

        complexity = self._detect_complexity(normalized)
        answer_style = self._detect_style(normalized)
        expected_depth = self._detect_depth(normalized, complexity, answer_style)
        question_type = self._detect_question_type(normalized)

        return AnalysisResult(
            intent=intent,
            intent_label=INTENT_LABELS.get(intent, "Informacoes Gerais"),
            complexity=complexity,
            answer_style=answer_style,
            expected_depth=expected_depth,
            question_type=question_type,
        )

    def _classify_intent(self, question: str) -> str:
        normalized = normalize_text(question)
        scores = {}
        for intent, patterns in INTENT_PATTERNS.items():
            score = sum(1 for p in patterns if p in normalized)
            scores[intent] = score / max(len(patterns), 1)

        if not scores or max(scores.values()) == 0:
            for intent, patterns in INTENT_PATTERNS.items():
                for pattern in patterns:
                    first_word = pattern.split()[0]
                    if re.search(r'\b' + re.escape(first_word) + r'\b', normalized):
                        scores[intent] = scores.get(intent, 0) + 0.5

        if not scores or max(scores.values()) == 0:
            return "objetivos"

        return max(scores, key=scores.get)

    def _detect_complexity(self, normalized: str) -> str:
        simplicity_kw = ["quanto", "quando", "onde", "qtd", "numero", "data", "hora", "carga horaria", "quantas horas"]
        complexity_high = ["analise", "compare", "discuta", "avalie", "relacione", "explique em detalhes", "explore profundamente", "em profundidade", "todos os aspectos"]

        word_count = len(normalized.split())
        if any(k in normalized for k in complexity_high):
            return "alta"
        if word_count > 8:
            return "alta"
        if any(k in normalized for k in simplicity_kw):
            return "baixa"
        if word_count < 3:
            return "baixa"
        return "media"

    def _detect_style(self, normalized: str) -> str:
        objective_kw = ["quanto", "quando", "onde", "qtd", "numero", "data", "hora", "carga horaria", "quantas horas", "exatamente"]
        explanatory_kw = ["como", "por que", "significa", "explica", "defina", "descreve", "o que", "porque", "explicar", "proporcionar"]

        if any(k in normalized for k in objective_kw):
            return "objetiva"
        if any(k in normalized for k in explanatory_kw):
            return "explicativa"
        return "explicativa"

    def _detect_depth(self, normalized: str, complexity: str, style: str) -> str:
        depth_map = {"baixa": "curta", "media": "normal", "alta": "detalhada"}
        detailed_kw = ["analise", "compare", "discuta", "avalie", "relacione", "explique em detalhes", "explore profundamente", "caracteriza", "em profundidade", "compreensao ampla", "todos os aspectos"]

        if any(k in normalized for k in detailed_kw):
            return "detalhada"

        expected = depth_map.get(complexity, "normal")

        if style == "explicativa" and expected == "curta":
            return "normal"

        if "mercado" in normalized or "certificado" in normalized or "modulo" in normalized:
            return "detalhada"

        if "porque" in normalized or "compare" in normalized or "relacione" in normalized:
            return "detalhada"

        return expected

    def _detect_question_type(self, normalized: str) -> str:
        for qtype, patterns in QUESTION_TYPE_PATTERNS.items():
            if any(p in normalized for p in patterns):
                return qtype
        return "factual"


def get_intent_group_label(intent: str) -> str:
    return INTENT_LABELS.get(intent, "Informacoes Gerais")
