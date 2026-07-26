import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ResponsePlan:
    goal: str
    structure: list[str]
    depth: str
    style: str
    key_points: list[str] = field(default_factory=list)
    required_elements: list[str] = field(default_factory=lambda: [
        "responder diretamente", "explicar conceitos", "usar exemplos", "concluir"
    ])
    max_sections: int = 4
    use_bullets: bool = True
    use_bold: bool = True


QUESTION_GOALS = {
    "definicao": ["o que", "o que e", "o que sao", "defina", "significa", "conceito"],
    "comparacao": ["compare", "diferenca", "diferenca entre", "versus", "vs", "qual a diferenca"],
    "procedimento": ["como", "como fazer", "como funciona", "processo", "etapas"],
    "causa_efeito": ["por que", "porque", "qual a razao", "motivo"],
    "listagem": ["quais", "quais sao", "liste", "enumere", "exemplos de", "tipos de"],
    "verificacao": ["existe", "tem", "possui", "contem", "ha"],
    "quantificacao": ["quanto", "quantos", "quantas", "carga horaria", "duracao", "tempo"],
    "localizacao": ["onde", "aonde", "em qual"],
    "detalhamento": ["explique em detalhes", "detalhe", "aprofundar", "em profundidade"],
    "simples": [],
}

GOAL_STRUCTURES = {
    "definicao": ["Definicao do conceito", "Caracteristicas principais", "Exemplos relevantes", "Conexao com o curso"],
    "comparacao": ["Contexto da comparacao", "Pontos em comum", "Diferencas principais", "Relevancia pratica"],
    "procedimento": ["Visao geral do processo", "Etapas detalhadas", "Requisitos necessarios", "Resultado esperado"],
    "causa_efeito": ["Contextualizacao", "Causa ou origem", "Efeitos ou consequencias", "Aplicacao pratica"],
    "listagem": ["Contexto da listagem", "Itens principais", "Detalhamento de cada item", "Consideracoes finais"],
    "verificacao": ["Resposta direta", "Detalhamento", "Condicoes e requisitos", "Informacoes adicionais"],
    "quantificacao": ["Resposta numerica direta", "Contexto da medicao", "Comparacao se aplicavel", "Observacoes"],
    "localizacao": ["Resposta direta", "Contexto", "Detalhamento do local", "Informacoes de contato"],
    "detalhamento": ["Introducao ao tema", "Analise aprofundada", "Conexoes com outras areas", "Sintese final"],
    "simples": ["Resposta direta", "Explicacao basica", "Detalhe complementar", "Conclusao"],
}


def detect_goal(question: str) -> str:
    normalized = question.lower().strip()
    for goal, patterns in QUESTION_GOALS.items():
        for pattern in patterns:
            if normalized.startswith(pattern) or pattern in normalized:
                return goal
    return "simples"


def define_structure(goal: str, depth: str) -> list[str]:
    base_structure = GOAL_STRUCTURES.get(goal, GOAL_STRUCTURES["simples"])
    if depth == "curta":
        return base_structure[:2] if len(base_structure) >= 2 else base_structure
    elif depth == "detalhada":
        return base_structure + ["Aprofundamento adicional", "Recursos e referencias do plano"]
    return base_structure


def choose_depth(question: str, analyzer_result: dict) -> str:
    return analyzer_result.get("expected_depth", "normal")


def choose_style(question: str, analyzer_result: dict) -> str:
    return analyzer_result.get("answer_style", "explicativa")


def extract_key_points(question: str, context: str) -> list[str]:
    points = []
    question_terms = set(question.lower().split())
    if context:
        words = context.split()
        mid = len(words) // 2
        points.append(words[0] if words else question)
        if len(words) > mid:
            points.append(words[mid])
        if words:
            points.append(words[-1])
    return points


def create_response_plan(question: str, analyzer_result: dict, context: str = "") -> ResponsePlan:
    goal = detect_goal(question)
    depth = choose_depth(question, analyzer_result)
    style = choose_style(question, analyzer_result)
    structure = define_structure(goal, depth)
    key_points = extract_key_points(question, context)

    return ResponsePlan(
        goal=goal,
        structure=structure,
        depth=depth,
        style=style,
        key_points=key_points,
    )
