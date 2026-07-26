from dataclasses import dataclass
from typing import Optional


@dataclass
class BuiltPrompt:
    system: str
    user: str
    tokens_estimate: int


DEPTH_CONFIG = {
    "curta": "Responda de forma breve e objetiva.",
    "normal": "Explique de forma clara e completa.",
    "detalhada": "Responda de forma detalhada e completa.",
    "professor": "Ensine como um professor experiente, conectando conceitos.",
}

STYLE_ADAPTATIONS = {
    "objetiva": "Seja direto e objetivo. Prefira fatos a explicacoes longas.",
    "explicativa": "Seja didatico e explicativo. Ajude o usuario a compreender o conteudo.",
}

PROFESSOR_INSTRUCTION = (
    "Conecte conceitos, mostre relacoes entre disciplinas, "
    "explique o proposito de cada componente e guie o aprendizado."
)


class PromptBuilder:
    def build(
        self,
        question: str,
        context: str,
        intent_label: str,
        depth: str = "normal",
        style: str = "explicativa",
        plan_structure: Optional[list[str]] = None,
        history: str = "",
        goal: str = "",
    ) -> BuiltPrompt:
        depth_desc = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["normal"])
        style_adapt = STYLE_ADAPTATIONS.get(style, STYLE_ADAPTATIONS["explicativa"])

        system_parts = [
            "IDENTIDADE: Especialista Oficial do Curso Tecnico em Desenvolvimento de Sistemas - SENAI Jau.",
            "",
            "REGRAS:",
            "- Responda APENAS com base no Plano de Curso fornecido.",
            "- Interprete e explique; nao copie trechos literalmente.",
            "- Se nao encontrar a informacao, informe educadamente.",
            "- Nunca invente dados, disciplinas, cargas horarias ou regras.",
            "- Nunca mencione RAG, chunk, embedding, score ou processo de busca.",
            "",
            "ESTILO:",
            "- Linguagem natural, didatica e acolhedora.",
            "- Use **negrito** para destaques.",
            "- Use topicos para listas.",
            "- Varie expressoes como 'Na pratica...', 'Em outras palavras...', 'Um ponto importante e...'",
            "- Explique siglas e termos tecnicos.",
            "- Conecte diferentes partes do Plano de Curso quando relevante.",
            "- Evite repeticoes e estruturas engessadas.",
            f"- {depth_desc}",
            f"- {style_adapt}",
        ]

        if depth == "professor":
            system_parts.append(f"- {PROFESSOR_INSTRUCTION}")

        if plan_structure:
            structure_lines = [f"{i+1}. {s}" for i, s in enumerate(plan_structure)]
            system_parts.append("")
            system_parts.append("ESTRUTURA DA RESPOSTA:")
            system_parts.extend(structure_lines)

        system_prompt = "\n".join(system_parts)

        user_parts = []
        if history:
            user_parts.append(history)
        user_parts.append(f"Pergunta: {question}")
        if intent_label:
            user_parts.append(f"Assunto: {intent_label}")
        if goal:
            user_parts.append(f"Objetivo da pergunta: {goal}")
        user_parts.append(context) if context else None

        user_prompt = "\n\n".join(p for p in user_parts if p)

        tokens_estimate = len(system_prompt.split()) + len(user_prompt.split())

        return BuiltPrompt(
            system=system_prompt,
            user=user_prompt,
            tokens_estimate=tokens_estimate,
        )
