import base64
import hashlib
import hmac
import os
import secrets
import time
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi.responses import RedirectResponse

load_dotenv()

from backend.database import (
    check_database_connection,
    create_simulation,
    create_session,
    delete_session,
    get_session,
    list_simulations,
    upsert_user,
)
from backend.gitlab_mr import create_practice_mr

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.scss.tcd.ie")
GITLAB_AUTHORIZE_URL = f"{GITLAB_URL}/oauth/authorize"
GITLAB_TOKEN_URL = f"{GITLAB_URL}/oauth/token"
GITLAB_USER_URL = f"{GITLAB_URL}/api/v4/user"
GITLAB_CALLBACK_URL = os.getenv(
    "GITLAB_CALLBACK_URL", "http://localhost:8000/auth/gitlab/callback"
)
APP_SECRET = os.getenv("APP_SECRET", "development-only-change-me")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
SESSION_COOKIE = "swe_sim_session"


class SimulationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)
    team_size: int = Field(default=3, ge=1, le=10)
    difficulty: str = Field(default="Intermediate", pattern="^(Beginner|Intermediate|Advanced)$")


def create_oauth_state() -> str:
    payload = f"{int(time.time())}:{secrets.token_urlsafe(24)}"
    signature = hmac.new(APP_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{payload}:{encoded_signature}"


def is_valid_oauth_state(state: str) -> bool:
    try:
        timestamp, nonce, signature = state.split(":")
        payload = f"{timestamp}:{nonce}"
        expected = hmac.new(APP_SECRET.encode(), payload.encode(), hashlib.sha256).digest()
        expected_signature = base64.urlsafe_b64encode(expected).decode().rstrip("=")
        return (
            hmac.compare_digest(signature, expected_signature)
            and time.time() - int(timestamp) < 600
        )
    except (ValueError, TypeError):
        return False


@app.get("/auth/gitlab")
def gitlab_login():
    client_id = os.getenv("GITLAB_CLIENT_ID")
    if not client_id:
        return {"error": "GITLAB_CLIENT_ID is not configured"}

    params = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": GITLAB_CALLBACK_URL,
            "response_type": "code",
            "scope": "api",
            "state": create_oauth_state(),
        }
    )
    return RedirectResponse(f"{GITLAB_AUTHORIZE_URL}?{params}")


@app.get("/auth/gitlab/callback")
async def gitlab_callback(
    background_tasks: BackgroundTasks,
    code: str | None = None,
    state: str | None = None,
):
    if not code or not state or not is_valid_oauth_state(state):
        return {"error": "Invalid GitLab OAuth callback"}

    client_id = os.getenv("GITLAB_CLIENT_ID")
    client_secret = os.getenv("GITLAB_CLIENT_SECRET")
    if not client_id or not client_secret:
        return {"error": "GitLab OAuth credentials are not configured"}

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            GITLAB_TOKEN_URL,
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": GITLAB_CALLBACK_URL,
                "grant_type": "authorization_code",
            },
            headers={"Accept": "application/json"},
        )
        token_response.raise_for_status()
        access_token = token_response.json().get("access_token")
        if not access_token:
            return {"error": "GitLab did not return an access token"}

        user_response = await client.get(
            GITLAB_USER_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )
        user_response.raise_for_status()

    gitlab_user = user_response.json()
    try:
        stored_user = upsert_user(gitlab_user)
    except Exception as error:
        raise HTTPException(status_code=503, detail="Unable to save user") from error

    if not stored_user.get("practice_repo"):
        background_tasks.add_task(create_practice_mr, access_token, stored_user["gitlab_id"])

    session_id = secrets.token_urlsafe(32)
    try:
        create_session(session_id, stored_user, access_token)
    except Exception as error:
        raise HTTPException(status_code=503, detail="Unable to create session") from error

    response = RedirectResponse(FRONTEND_URL)
    response.set_cookie(
        SESSION_COOKIE,
        session_id,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
    )
    return response


@app.get("/auth/me")
def current_user(request: Request):
    session_id = request.cookies.get(SESSION_COOKIE)
    session = get_session(session_id) if session_id else None
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"user": session["user"]}


def authenticated_session(request: Request) -> dict:
    session_id = request.cookies.get(SESSION_COOKIE)
    session = get_session(session_id) if session_id else None
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return session


@app.post("/simulations", status_code=201)
def start_simulation(payload: SimulationCreate, request: Request):
    session = authenticated_session(request)
    try:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=422, detail="Title cannot be blank")
        return create_simulation(
            session["user"]["gitlab_id"],
            title,
            payload.description.strip(),
            payload.team_size,
            payload.difficulty,
        )
    except Exception as error:
        raise HTTPException(status_code=503, detail="Unable to create simulation") from error


@app.get("/simulations")
def simulations_for_user(request: Request):
    session = authenticated_session(request)
    try:
        return {"simulations": list_simulations(session["user"]["gitlab_id"])}
    except Exception as error:
        raise HTTPException(status_code=503, detail="Unable to load simulations") from error


@app.post("/auth/logout", status_code=204)
def logout(request: Request, response: Response):
    session_id = request.cookies.get(SESSION_COOKIE)
    if session_id:
        delete_session(session_id)
    response.delete_cookie(SESSION_COOKIE)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health/database")
def database_health():
    try:
        connected = check_database_connection()
    except Exception:
        connected = False
    return {"database": "connected" if connected else "unavailable"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}