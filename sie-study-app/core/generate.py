import json
from typing import Generator

from core.claude_client import get_claude_client


SYSTEM_PROMPT = (
    "You are an expert at writing FINRA SIE exam practice questions. "
    "Generate questions that match the style, difficulty, and content coverage of the actual SIE exam. "
    "Return ONLY valid JSON — no commentary, no markdown fences, no extra text. "
    "The correct answer should require actual knowledge, not just process of elimination. "
    "Make distractors plausible but clearly wrong to someone who knows the material. "
    "Avoid trick questions."
)


def generate_questions(
    topic_id: int,
    topic_name: str,
    topic_description: str,
    difficulty: str,
    count: int,
) -> list[dict]:
    client = get_claude_client()

    user_prompt = (
        f"Generate {count} {difficulty} multiple-choice practice questions for the SIE exam topic: "
        f'"{topic_name}".\n\n'
        f"This topic covers: {topic_description}\n\n"
        "Return a JSON array where each element has exactly these keys:\n"
        '{\n'
        '  "stem": "the question text",\n'
        '  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},\n'
        '  "correct": "A",\n'
        '  "explanation": "clear explanation of why the correct answer is right and why each distractor is wrong"\n'
        "}\n\n"
        "Requirements:\n"
        "- Each question must have exactly 4 options (A, B, C, D)\n"
        "- The correct field must be exactly one of: A, B, C, D\n"
        "- Distribute correct answers across A/B/C/D — don't always use A\n"
        f"- Generate exactly {count} questions"
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown fences if present despite instructions
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

    data = json.loads(raw)

    validated = []
    for item in data:
        if not all(k in item for k in ("stem", "options", "correct", "explanation")):
            continue
        if not all(k in item["options"] for k in ("A", "B", "C", "D")):
            continue
        if item["correct"] not in ("A", "B", "C", "D"):
            continue
        validated.append(item)

    return validated
