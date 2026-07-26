from typing import Optional


def calculate_confidence(
    chunks: list[tuple],
    avg_score: float,
    quality_score: float = 100.0,
) -> dict:
    if not chunks:
        return {
            "confidence": 0.0,
            "level": "nenhum",
            "message": "Nao foram encontradas informacoes no Plano de Curso.",
        }

    n_chunks = len(chunks)
    pages_found = len(set(c[1] for c in chunks))
    top_score = max(c[2] for c in chunks) if chunks else 0

    score_factor = min(avg_score / 15.0, 1.0) * 40
    coverage_factor = min(n_chunks / 6.0, 1.0) * 20
    page_factor = min(pages_found / 5.0, 1.0) * 15
    top_factor = min(top_score / 25.0, 1.0) * 10
    quality_factor = (quality_score / 100.0) * 15

    confidence = score_factor + coverage_factor + page_factor + top_factor + quality_factor
    confidence = min(max(confidence, 0), 100)

    if confidence >= 85:
        level = "alto"
        message = ""
    elif confidence >= 60:
        level = "medio"
        message = ""
    elif confidence >= 30:
        level = "baixo"
        message = "Essa informacao aparece parcialmente no Plano de Curso."
    else:
        level = "baixo"
        message = "Essa informacao aparece parcialmente no Plano de Curso."

    return {
        "confidence": round(confidence, 1),
        "level": level,
        "message": message,
    }
