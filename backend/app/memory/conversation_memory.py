import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Turn:
    user_message: str
    intent: str
    intent_label: str
    response: str
    response_summary: str
    confidence: float = 0.0


class ConversationMemory:
    def __init__(self, max_history: int = 5):
        self.history: list[Turn] = []
        self.max_history = max_history
        self.current_topic: Optional[str] = None

    def add_turn(self, turn: Turn) -> None:
        self.history.append(turn)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        self.current_topic = turn.intent_label

    def get_history_context(self) -> str:
        if not self.history:
            return ""
        parts = ["CONTEXTO DA CONVERSA:"]
        for i, turn in enumerate(self.history, 1):
            parts.append(f"{i}. Usuario: {turn.user_message}")
            parts.append(f"   Resposta: {turn.response_summary}")
        return "\n".join(parts)

    def get_last_topic(self) -> Optional[str]:
        return self.current_topic

    def get_last_user_message(self) -> Optional[str]:
        return self.history[-1].user_message if self.history else None

    def get_last_intent(self) -> Optional[str]:
        return self.history[-1].intent if self.history else None

    def has_context(self) -> bool:
        return len(self.history) > 0

    def resolve_references(self, question: str) -> dict:
        result = {
            "resolved_question": question,
            "pronome_resolvido": False,
            "pergunta_incompleta": False,
            "assunto_mantido": False,
        }

        if not self.history:
            return result

        last_turn = self.history[-1]
        last_msg = last_turn.user_message.lower()

        normalized_q = question.lower().strip()

        has_pronoun = bool(re.search(
            r'\b(esse|essa|isso|ele|ela|desse|dessa|disso|nele|nela|seu|sua)\b',
            normalized_q,
        ))

        if has_pronoun:
            subject_match = re.search(
                r'(?:o|a|os|as)\s+(\w+(?:\s+\w+){0,3})',
                last_msg,
            )
            if subject_match:
                subject = subject_match.group(1)
                result["resolved_question"] = re.sub(
                    r'\b(esse|essa|isso|ele|ela|desse|dessa|disso|nele|nela|seu|sua)\b',
                    subject,
                    question,
                )
                result["pronome_resolvido"] = True

        is_incomplete = (
            len(normalized_q.split()) <= 3
            and not normalized_q.startswith(("o que", "quem", "onde"))
        )
        if is_incomplete:
            topic = self.current_topic or last_turn.intent_label
            result["resolved_question"] = f"{question} ({topic})"
            result["pergunta_incompleta"] = True

        if self.current_topic == last_turn.intent_label:
            result["assunto_mantido"] = True

        return result

    def clear(self) -> None:
        self.history.clear()
        self.current_topic = None
