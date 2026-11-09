import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-4o-mini"
ERROR_REPORTING_INSTRUCTIONS = """\
In your response, include a Markdown section titled "## Injected Errors / Deviations".
List each intentional error, omission, or incorrect behavior in the code relative
to the task, including the relevant file or class/method and its impact. Preserve
persona-driven defects; do not fix them unless the task explicitly asks you to.
Also identify other task requirements the code does not meet, and distinguish
those from intentional persona-driven defects. If there are none, state "None."
"""


def execute_task(
    task_description: str,
    persona_file: str | Path,
    output_file: str | Path | None = None,
    *,
    model: str | None = None,
) -> str:
    """Run a task, require an injected-error report, and save the response."""
    load_dotenv()

    if not task_description.strip():
        raise ValueError("task_description cannot be blank")

    persona = Path(persona_file).read_text(encoding="utf-8")
    if not persona.strip():
        raise ValueError("persona file cannot be blank")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    response = httpx.post(
        OPENAI_RESPONSES_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
            "instructions": f"{persona.rstrip()}\n\n{ERROR_REPORTING_INSTRUCTIONS}",
            "input": task_description,
        },
        timeout=60.0,
    )
    response.raise_for_status()

    response_data = response.json()
    result = "\n".join(
        content["text"]
        for item in response_data.get("output", [])
        if item.get("type") == "message"
        for content in item.get("content", [])
        if content.get("type") == "output_text"
    )
    if not result:
        raise ValueError("OpenAI response did not contain any output text")
    if "## Injected Errors / Deviations" not in result:
        raise ValueError(
            'OpenAI response is missing the required "Injected Errors / Deviations" section'
        )

    if output_file is not None:
        Path(output_file).write_text(result, encoding="utf-8")
    return result
