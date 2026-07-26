import time
from pathlib import Path
from typing import Optional

from app.rag.chunker import load_pdf_chunks, search_pdf_chunks
from app.rag.fusion import deduplicate_chunks, merge_similar_chunks, order_by_relevance, separate_by_subject
from app.rag.planner import create_response_plan
from app.services.analyzer import QuestionAnalyzer, get_intent_group_label
from app.llm.prompt_builder import PromptBuilder
from app.llm.groq_service import GroqService
from app.llm.quality_checker import QualityChecker
from app.llm.confidence import calculate_confidence
from app.memory.conversation_memory import ConversationMemory, Turn
from app.core.metrics import QueryMetrics, register_metrics


class ResponseService:
    def __init__(self, pdf_path: Path):
        self.analyzer = QuestionAnalyzer()
        self.prompt_builder = PromptBuilder()
        self.llm = GroqService()
        self.quality_checker = QualityChecker()
        self.memory = ConversationMemory(max_history=5)
        self.pdf_chunks = load_pdf_chunks(pdf_path)

    def process(self, question: str) -> dict:
        metrics = QueryMetrics(start_time=time.time())

        analysis = self.analyzer.analyze(question)
        metrics.intent = analysis.intent
        metrics.intent_label = analysis.intent_label
        metrics.depth = analysis.expected_depth
        metrics.style = analysis.answer_style

        ref_resolution = self.memory.resolve_references(question)
        resolved_question = ref_resolution["resolved_question"]

        plan = create_response_plan(resolved_question, {
            "expected_depth": analysis.expected_depth,
            "answer_style": analysis.answer_style,
        })

        search_start = time.time()
        raw_chunks = search_pdf_chunks(resolved_question, analysis.intent, self.pdf_chunks)
        metrics.search_time_ms = (time.time() - search_start) * 1000

        if not raw_chunks:
            no_context_msg = (
                "Desculpe, mas nao encontrei essa informacao especifica no Plano de Curso atual. "
                "Posso responder perguntas sobre objetivos, requisitos, carga horaria, unidades curriculares, "
                "perfil profissional, mercado de trabalho, estagio e certificacao do curso."
            )
            response_turn = Turn(
                user_message=question,
                intent=analysis.intent,
                intent_label=analysis.intent_label,
                response=no_context_msg,
                response_summary=no_context_msg[:200],
                confidence=0.0,
            )
            self.memory.add_turn(response_turn)
            return {
                "response": no_context_msg,
                "sources": [],
                "analysis": {
                    "intent": analysis.intent,
                    "intent_label": analysis.intent_label,
                    "complexity": analysis.complexity,
                    "expected_depth": analysis.expected_depth,
                    "answer_style": analysis.answer_style,
                    "question_type": analysis.question_type,
                },
                "plan": {
                    "goal": plan.goal,
                    "structure": plan.structure,
                    "depth": plan.depth,
                },
                "confidence": {
                    "confidence": 0.0,
                    "level": "nenhum",
                    "message": "Nao foram encontradas informacoes no Plano de Curso.",
                },
                "metrics": metrics.to_dict(),
            }

        fused = deduplicate_chunks(raw_chunks)
        fused = merge_similar_chunks(fused)
        fused = order_by_relevance(fused)
        subjects = separate_by_subject(fused)

        context_parts = []
        for subject, items in subjects.items():
            context_parts.append(f"--- {subject} ---")
            for content, page_num, score, _, _ in items[:4]:
                context_parts.append(content.strip())
        context_str = "\n\n".join(context_parts)

        avg_score = sum(c[2] for c in fused) / max(len(fused), 1) if fused else 0
        metrics.chunk_count = len(fused)
        metrics.avg_score = avg_score

        history_str = self.memory.get_history_context()

        built = self.prompt_builder.build(
            question=resolved_question,
            context=context_str,
            intent_label=analysis.intent_label,
            depth=analysis.expected_depth,
            style=analysis.answer_style,
            plan_structure=plan.structure,
            history=history_str,
            goal=plan.goal,
        )
        metrics.tokens_sent = built.tokens_estimate

        llm_start = time.time()
        response, tokens_sent_actual, tokens_received = self.llm.generate(
            built.system, built.user, temperature=0.1,
        )
        metrics.llm_time_ms = (time.time() - llm_start) * 1000
        metrics.tokens_sent = tokens_sent_actual
        metrics.tokens_received = tokens_received

        quality_result = self.quality_checker.check(response, resolved_question, context_str)

        if not quality_result["passed"]:
            response = self.quality_checker.rewrite(response)

        confidence_result = calculate_confidence(fused, avg_score, quality_result["quality_score"])
        metrics.confidence = confidence_result["confidence"]

        if confidence_result["level"] == "baixo" and confidence_result["message"]:
            response = response + "\n\n" + confidence_result["message"]

        response_turn = Turn(
            user_message=question,
            intent=analysis.intent,
            intent_label=analysis.intent_label,
            response=response,
            response_summary=response[:200],
            confidence=confidence_result["confidence"],
        )
        self.memory.add_turn(response_turn)

        register_metrics(metrics)

        return {
            "response": response,
            "sources": [
                {"page": c[1], "score": round(c[2], 2)}
                for c in fused[:5]
            ],
            "analysis": {
                "intent": analysis.intent,
                "intent_label": analysis.intent_label,
                "complexity": analysis.complexity,
                "expected_depth": analysis.expected_depth,
                "answer_style": analysis.answer_style,
                "question_type": analysis.question_type,
            },
            "plan": {
                "goal": plan.goal,
                "structure": plan.structure,
                "depth": plan.depth,
            },
            "confidence": confidence_result,
            "metrics": metrics.to_dict(),
        }

    def reset_memory(self) -> None:
        self.memory.clear()

    def get_metrics(self) -> list[dict]:
        from app.core.metrics import get_metrics_history
        return get_metrics_history()
