# SWE Sim
SWE Sim is a project that uses AI to simulate a software engineering team to allow students to practice task triage and code reviews.

## Local development

### Prerequisites

- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/)
- [Bun](https://bun.sh/)
- A GitHub OAuth App for sign-in

### Configure GitHub OAuth

Create a GitHub OAuth App under `Settings > Developer settings > OAuth Apps`.
Use these local URLs:

```text
Homepage URL: http://localhost:5173
Authorization callback URL: http://127.0.0.1:8000/auth/github/callback
```

From the project root, create a local environment file:

```sh
cp .env.example .env
```

Update `.env` with the OAuth App credentials. Keep this file private; it is
ignored by Git.

```env
GITHUB_CLIENT_ID=your_github_oauth_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_client_secret
GITHUB_CALLBACK_URL=http://127.0.0.1:8000/auth/github/callback
APP_SECRET=replace-with-a-long-random-value
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=SWE-Sim
MONGODB_DATABASE=swe_sim
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

Open the frontend at http://localhost:5173 and select **Sign in with GitHub**.

After signing in, use the simulation form to create a simulation. Simulations
are saved to the MongoDB `simulations` collection and are associated with the
authenticated GitHub user.

The simulation API provides:

```text
POST /simulations   Create a simulation for the signed-in user
GET  /simulations   List the signed-in user's simulations
```

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
