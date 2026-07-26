import re
from question_analyzer import get_intent_group_label


def group_results(results: list[tuple]) -> dict[str, list[tuple]]:
    groups = {}
    for item in results:
        intent = item[3]
        label = get_intent_group_label(intent)
        if label not in groups:
            groups[label] = []
        groups[label].append(item)

    if not groups and results:
        groups["Informacoes Gerais"] = results

    return groups


def build_context(results: list[tuple]) -> str:
    if not results:
        return ""

    groups = group_results(results)
    context = "==================== CONHECIMENTO RECUPERADO ====================\n\n"

    for assunto, items in groups.items():
        context += f"ASSUNTO: {assunto}\n\n"
        context += "INFORMACOES ENCONTRADAS:\n"

        fontes = []
        for content, page_num, score, _ in items:
            context += f"  {content.strip()}\n\n"
            fontes.append(f"Pagina {page_num}")

        fontes_unicas = sorted(set(fontes), key=lambda x: [int(s) for s in re.findall(r'\d+', x)])
        context += "FONTES:\n"
        for fonte in fontes_unicas:
            context += f"  * {fonte}\n"
        context += "\n---\n\n"

    return context


def build_contextual_prompt(history: list[dict], max_history: int = 5) -> str:
    if not history:
        return ""

    prompt = "==================== CONTEXTO CONVERSACIONAL ====================\n\n"
    for entry in history[-max_history:]:
        prompt += f"Mensagem {entry['timestamp']}: {entry['user_message']}\n"

    prompt += "\n=================== INICIO DA RESPOSTA ATUAL ====================\n\n"
    return prompt
