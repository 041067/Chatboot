import re


def post_process(response: str) -> str:
    if not response:
        return response

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

    lines = response.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("**") and stripped.endswith("**") and len(stripped) > 4:
            lines[i] = line.replace(stripped, stripped)
    response = "\n".join(lines)

    return response.strip()
