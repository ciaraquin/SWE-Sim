import logging
import os
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from backend.database import save_practice_repo
from backend.task_runner import execute_task

GITLAB_API_URL = f"{os.getenv('GITLAB_URL', 'https://gitlab.scss.tcd.ie')}/api/v4"
CONTEXT_DIR = Path(__file__).resolve().parent.parent / "context"
TASK_FILE = CONTEXT_DIR / "tasks.md"
PERSONA_FILES = [CONTEXT_DIR / "persona_good.md", CONTEXT_DIR / "persona_bad.md"]

logger = logging.getLogger(__name__)


def create_practice_mr(access_token: str, gitlab_id: int) -> None:
    """Create a repo in the user's GitLab with a persona-written MR to review."""
    try:
        _create_practice_mr(access_token, gitlab_id)
    except Exception:
        # Runs as a background task; practice_repo stays unset so the next login retries.
        logger.exception("Failed to create practice MR for GitLab user %s", gitlab_id)


def _create_practice_mr(access_token: str, gitlab_id: int) -> None:
    task = TASK_FILE.read_text(encoding="utf-8")
    persona_file = random.choice(PERSONA_FILES)
    result = execute_task(task, persona_file)

    code_match = re.search(r"```python\n(.*?)```", result, re.DOTALL)
    if not code_match:
        raise ValueError("Persona response did not contain a python code block")
    file_match = re.search(r"`([\w/]+\.py)`", task)
    file_path = file_match.group(1) if file_match else "solution.py"
    branch = f"feature/{Path(file_path).stem}"

    with httpx.Client(
        base_url=GITLAB_API_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30.0,
    ) as client:
        project = _post(
            client,
            "/projects",
            {
                "name": f"swe-sim-practice-{int(time.time())}",
                "visibility": "private",
                "initialize_with_readme": True,
            },
        )
        default_branch = project.get("default_branch") or "main"
        _post(
            client,
            f"/projects/{project['id']}/repository/commits",
            {
                "branch": branch,
                "start_branch": default_branch,
                "commit_message": f"Implement {file_path}",
                "actions": [
                    {"action": "create", "file_path": file_path, "content": code_match.group(1)}
                ],
            },
        )
        merge_request = _post(
            client,
            f"/projects/{project['id']}/merge_requests",
            {
                "source_branch": branch,
                "target_branch": default_branch,
                "title": f"Implement {file_path}",
                "description": task,
            },
        )

    save_practice_repo(
        gitlab_id,
        {
            "project_url": project["web_url"],
            "mr_url": merge_request["web_url"],
            "persona": persona_file.stem,
            "answer_key": result,
            "created_at": datetime.now(timezone.utc),
        },
    )


def _post(client: httpx.Client, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    response.raise_for_status()
    return response.json()
