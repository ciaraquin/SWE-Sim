import copy
import os
import shelve
import threading
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# shortcut: local shelve file instead of MongoDB, single process only; swap back to Mongo before deploying.
LOCAL_DB_PATH = os.getenv("LOCAL_DB_PATH", "local_db")
_lock = threading.Lock()


def _db() -> shelve.Shelf:
    return shelve.open(LOCAL_DB_PATH)


def _public_user(user: dict) -> dict:
    # Answer key is excluded: the returned user is stored in the session and sent to the frontend.
    user = copy.deepcopy(user)
    if "practice_repo" in user:
        user["practice_repo"].pop("answer_key", None)
    return user


def upsert_user(gitlab_user: dict) -> dict:
    now = datetime.now(timezone.utc)
    key = f"user:{gitlab_user['id']}"
    with _lock, _db() as db:
        user = db.get(key, {"created_at": now})
        user.update(
            {
                "gitlab_id": gitlab_user["id"],
                "login": gitlab_user.get("username"),
                "name": gitlab_user.get("name"),
                "email": gitlab_user.get("public_email") or gitlab_user.get("email"),
                "avatar_url": gitlab_user.get("avatar_url"),
                "html_url": gitlab_user.get("web_url"),
                "updated_at": now,
            }
        )
        db[key] = user
    return _public_user(user)


def save_practice_repo(gitlab_id: int, practice_repo: dict) -> None:
    key = f"user:{gitlab_id}"
    with _lock, _db() as db:
        if key in db:
            user = db[key]
            user["practice_repo"] = practice_repo
            db[key] = user


def create_session(session_id: str, user: dict, access_token: str) -> None:
    with _lock, _db() as db:
        db[f"session:{session_id}"] = {
            "session_id": session_id,
            "user": user,
            "access_token": access_token,
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        }


def get_session(session_id: str) -> dict | None:
    with _lock, _db() as db:
        session = db.get(f"session:{session_id}")
    if session and session["expires_at"] < datetime.now(timezone.utc):
        return None
    return session


def delete_session(session_id: str) -> None:
    with _lock, _db() as db:
        db.pop(f"session:{session_id}", None)


def create_simulation(
    gitlab_id: int,
    title: str,
    description: str,
    team_size: int,
    difficulty: str,
) -> dict:
    simulation = {
        "simulation_id": str(uuid4()),
        "gitlab_id": gitlab_id,
        "title": title,
        "description": description,
        "team_size": team_size,
        "difficulty": difficulty,
        "status": "active",
        "created_at": datetime.now(timezone.utc),
    }
    with _lock, _db() as db:
        db[f"simulation:{simulation['simulation_id']}"] = simulation
    return simulation


def list_simulations(gitlab_id: int) -> list[dict]:
    with _lock, _db() as db:
        simulations = [v for k, v in db.items() if k.startswith("simulation:") and v["gitlab_id"] == gitlab_id]
    return sorted(simulations, key=lambda s: s["created_at"], reverse=True)


def check_database_connection() -> bool:
    with _lock, _db():
        return True
