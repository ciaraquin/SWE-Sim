# SWE Sim
SWE Sim is a project that uses AI to simulate a software engineering team to allow students to practice task triage and code reviews.

## Local development

### Prerequisites

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/)
- [Bun](https://bun.sh/)
- A GitLab OAuth application for sign-in

### Configure GitLab OAuth

Create an OAuth application at
https://gitlab.scss.tcd.ie/-/profile/applications. Set the redirect URI to the
callback below and enable the `api` scope (needed to create the practice repo
and merge request). To use a different GitLab server, such as gitlab.com, set
`GITLAB_URL` in `.env`.

```text
Redirect URI: http://localhost:8000/auth/gitlab/callback
```

From the project root, create a local environment file:

```sh
cp .env.example .env
```

Update `.env` with the OAuth App credentials. Keep this file private; it is
ignored by Git.

```env
GITLAB_CLIENT_ID=your_gitlab_application_id
GITLAB_CLIENT_SECRET=your_gitlab_application_secret
GITLAB_CALLBACK_URL=http://localhost:8000/auth/gitlab/callback
GITLAB_URL=https://gitlab.scss.tcd.ie
APP_SECRET=replace-with-a-long-random-value
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=SWE-Sim
MONGODB_DATABASE=swe_sim
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
```

### Start the backend

Run these commands from the project root:

```sh
uv sync
uv run uvicorn backend.main:app --reload
```

The backend will be available at:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health/database

### Start the frontend

Open a second terminal:

```sh
cd frontend
bun install
bun run dev
```

Open the frontend at http://localhost:5173 and select **Sign in with GitLab**.

After signing in, use the simulation form to create a simulation. Simulations
are saved to the MongoDB `simulations` collection and are associated with the
authenticated GitLab user.

The simulation API provides:

```text
POST /simulations   Create a simulation for the signed-in user
GET  /simulations   List the signed-in user's simulations
```

### Run a task with a persona

`backend.task_runner.execute_task` reads persona instructions from a file,
sends them with a task description to the OpenAI Responses API, and saves the
generated text to the requested output file. Responses must include an
`Injected Errors / Deviations` section describing intentional defects and
other unmet task requirements; responses without that section are rejected.

```python
from backend.task_runner import execute_task

result = execute_task(
    task_description="Implement the shopping cart task.",
    persona_file="context/persona_good.md",
    output_file="shopping-cart-result.md",
)
```

Set `OPENAI_API_KEY` in `.env` before calling the function. `OPENAI_MODEL` is
optional and defaults to `gpt-4o-mini`. The function returns the generated text
as well as writing it to the output file.

### Verify the backend

With the backend running, this command should return `{"Hello":"World"}`:

```sh
curl http://127.0.0.1:8000/
```

To verify MongoDB, open:

```text
http://127.0.0.1:8000/health/database
```

The expected response is:

```json
{"database":"connected"}
```

### Troubleshooting

If `uv` reports that `VIRTUAL_ENV` belongs to another project, leave the
active environment and recreate this project's environment:

```sh
deactivate
uv venv --clear .venv
uv sync
```

Then start the backend again with:

```sh
uv run uvicorn backend.main:app --reload
```
