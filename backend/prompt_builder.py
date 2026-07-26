DEPTH_CONFIG = {
    "curta": {
        "descricao": "Responda de forma breve e objetiva.",
        "estrutura": (
            "1. **Resumo** — 1-2 linhas respondendo diretamente.\n"
            "2. **Explicacao** — 2-3 linhas, apenas o essencial.\n"
            "3. **Detalhes** — 1-2 topicos curtos.\n"
            "4. **Conclusao** — 1 linha de encerramento."
        ),
    },
    "normal": {
        "descricao": "Explique de forma clara e completa.",
        "estrutura": (
            "1. **Resumo** — Introdução curta respondendo a pergunta.\n"
            "2. **Explicacao** — Desenvolvimento didático com conceitos e conexões.\n"
            "3. **Detalhes** — Informações complementares em tópicos.\n"
            "4. **Conclusao** — Encerramento positivo."
        ),
    },
    "detalhada": {
        "descricao": "Responda de forma detalhada e completa.",
        "estrutura": (
            "1. **Resumo** — Contextualização inicial.\n"
            "2. **Explicacao** — Explicação completa com conexões entre assuntos.\n"
            "3. **Detalhes** — Informações extensas em tópicos.\n"
            "4. **Conclusao** — Síntese e convite para novas perguntas."
        ),
    },
    "professor": {
        "descricao": "Ensine como um professor experiente, conectando conceitos.",
        "estrutura": (
            "1. **Resumo** — Contextualização pedagógica.\n"
            "2. **Explicacao** — Ensino completo relacionando diferentes partes do plano.\n"
            "3. **Detalhes** — Aprofundamento com exemplos e conexões.\n"
            "4. **Conclusao** — Síntese do aprendizado com direcionamento."
        ),
    },
}

BASE_SYSTEM_PROMPT = (
    "IDENTIDADE: Especialista Oficial do Curso Técnico em Desenvolvimento de Sistemas - SENAI Jaú.\n\n"
    "REGRAS:\n"
    "- Responda APENAS com base no Plano de Curso fornecido.\n"
    "- Interprete e explique; não copie trechos literalmente.\n"
    "- Se não encontrar a informação, informe educadamente.\n"
    "- Nunca invente dados, disciplinas, cargas horárias ou regras.\n"
    "- Nunca mencione RAG, chunk, embedding, score ou processo de busca.\n\n"
    "ESTILO:\n"
    "- Linguagem natural, didática e acolhedora.\n"
    "- Use **negrito** para destaques.\n"
    "- Use tópicos (•) para listas.\n"
    "- Varie expressões: \"Na prática...\", \"Em outras palavras...\", \"Um ponto importante é...\"\n"
    "- Explique siglas e termos técnicos.\n"
    "- Conecte diferentes partes do Plano de Curso quando relevante.\n"
    "- Evite repetições e estruturas engessadas.\n"
)

STYLE_ADAPTATIONS = {
    "objetiva": "\nTOM: Seja direto e objetivo. Prefira fatos a explicações longas.\n",
    "explicativa": "\nTOM: Seja didático e explicativo. Ajude o usuário a compreender o conteúdo.\n",
}


def PromptBuilder(question: str, context: str, intent_label: str, depth: str = "normal",
                  style: str = "explicativa", history: str = "") -> tuple[str, str]:
    depth_cfg = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["normal"])

    system_prompt = BASE_SYSTEM_PROMPT
    if depth == "professor":
        system_prompt += (
            "\nCOMO PROFESSOR: Conecte conceitos, mostre relações entre disciplinas, "
            "explique o propósito de cada componente e guie o aprendizado.\n"
        )
    system_prompt += STYLE_ADAPTATIONS.get(style, "")
    system_prompt += f"\nESTRUTURA DA RESPOSTA:\n{depth_cfg['estrutura']}\n"

    user_prompt_parts = []
    if history:
        user_prompt_parts.append(history)
    user_prompt_parts.append(f"Pergunta: {question}")
    user_prompt_parts.append(f"Assunto: {intent_label}")
    user_prompt_parts.append(context)
    user_prompt_parts.append(f"Instrução: {depth_cfg['descricao']} Siga a estrutura obrigatória.")

    return system_prompt, "\n\n".join(user_prompt_parts)
