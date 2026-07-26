import re
from typing import Optional


class QualityChecker:
    def __init__(self):
        self.max_rewrite_attempts = 1

    def check(self, response: str, question: str, context: str) -> dict:
        checks = {
            "respondeu_exatamente": self._answered_exactly(response, question),
            "repeticoes": self._has_repetitions(response),
            "linguagem_natural": self._is_natural_language(response),
            "introducao": self._has_introduction(response),
            "conclusao": self._has_conclusion(response),
            "usa_bullets": self._uses_bullets(response),
            "usa_negrito": self._uses_bold(response),
            "sem_alucinacao": self._no_hallucination(response, context),
            "coerencia": self._is_coherent(response),
        }

        passed = sum(1 for v in checks.values() if v)
        total = len(checks)
        quality_score = (passed / total) * 100 if total > 0 else 100

        return {
            "checks": checks,
            "quality_score": quality_score,
            "passed": quality_score >= 60,
            "failures": [k for k, v in checks.items() if not v],
        }

    def _answered_exactly(self, response: str, question: str) -> bool:
        question_lower = question.lower().strip()
        if question_lower.endswith("?"):
            question_lower = question_lower[:-1]
        question_terms = set(question_lower.split()) - {"o", "a", "os", "as", "de", "do", "da", "em", "para", "com", "que", "qual", "quais"}
        if not question_terms:
            return True
        response_lower = response.lower()
        matches = sum(1 for t in question_terms if t in response_lower)
        return matches >= len(question_terms) * 0.3

    def _has_repetitions(self, response: str) -> bool:
        lines = response.lower().strip().split("\n")
        seen = set()
        for line in lines:
            normalized = re.sub(r"[^a-z0-9]", "", line.strip())
            if len(normalized) > 20 and normalized in seen:
                return False
            seen.add(normalized)

        sentences = re.split(r'[.!?]+', response.lower())
        seen_sentences = set()
        for sent in sentences:
            normalized = re.sub(r"[^a-z0-9]", "", sent.strip())
            if len(normalized) > 30 and normalized in seen_sentences:
                return False
            seen_sentences.add(normalized)

        return True

    def _is_natural_language(self, response: str) -> bool:
        unnatural_patterns = [
            r'\bchunk\b', r'\bembedding\b', r'\bscore\b', r'\btoken\b',
            r'\bvector\b', r'\bretrieval\b', r'\brerank\b', r'\bsemantic search\b',
        ]
        for pattern in unnatural_patterns:
            if re.search(pattern, response.lower()):
                return False

        sentences = re.split(r'[.!?]+', response)
        meaningful = [s for s in sentences if len(s.strip().split()) > 2]
        return len(meaningful) >= 2

    def _has_introduction(self, response: str) -> bool:
        first_line = response.strip().split("\n")[0] if response.strip() else ""
        return len(first_line.split()) >= 3

    def _has_conclusion(self, response: str) -> bool:
        conclusion_indicators = [
            "em resumo", "em suma", "concluindo", "para concluir",
            "por fim", "finalmente", "em síntese", "resumindo",
            "espero ter", "qualquer duvida", "tem mais alguma",
            "gostaria de saber mais",
        ]
        last_part = response.lower()[-300:] if len(response) > 300 else response.lower()
        return any(indicator in last_part for indicator in conclusion_indicators)

    def _uses_bullets(self, response: str) -> bool:
        return bool(re.search(r'^[•\-*]\s', response, re.MULTILINE))

    def _uses_bold(self, response: str) -> bool:
        return bool(re.search(r'\*\*', response))

    def _no_hallucination(self, response: str, context: str) -> bool:
        if not context:
            return True
        context_lower = context.lower()

        data_patterns = [
            r'(\d+)\s*horas?',
            r'(\d+)\s*(semestre|ano|mes)',
            r'carga\s*hor[aá]ria\s*(de\s*)?(\d+)',
        ]

        for pattern in data_patterns:
            response_matches = re.findall(pattern, response.lower())
            if not response_matches:
                continue
            context_matches = re.findall(pattern, context_lower)
            response_values = {m[-1] if isinstance(m, tuple) else m for m in response_matches}
            context_values = {m[-1] if isinstance(m, tuple) else m for m in context_matches}
            if response_values and context_values:
                for rv in response_values:
                    if rv not in context_values:
                        return False
        return True

    def _is_coherent(self, response: str) -> bool:
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if len(s.strip().split()) > 2]
        if len(sentences) < 2:
            return True
        transitions = 0
        transition_words = [
            "alem disso", "tambem", "por exemplo", "portanto", "assim",
            "dessa forma", "no entanto", "porem", "primeiro", "segundo",
            "finalmente", "outro", "alem", "como", "isto e", "ou seja",
        ]
        for sent in sentences:
            if any(tw in sent.lower() for tw in transition_words):
                transitions += 1
        return transitions >= max(1, len(sentences) * 0.2)

    def rewrite(self, response: str) -> str:
        lines = response.split("\n")
        seen = set()
        clean = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                clean.append(line)
                continue
            normalized = re.sub(r"[^a-z0-9]", "", stripped.lower())
            if normalized in seen:
                continue
            seen.add(normalized)
            clean.append(line)

        response = "\n".join(clean)
        response = re.sub(r"\n{3,}", "\n\n", response)
        response = re.sub(r"[*•]\s*[*•]", "•", response)
        response = re.sub(r"\*\*\s+", "**", response)
        response = re.sub(r"\s+\*\*", "**", response)
        response = re.sub(r"^\s+", "", response, flags=re.MULTILINE)
        response = re.sub(r"[ \t]+$", "", response, flags=re.MULTILINE)

        return response.strip()
