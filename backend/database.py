import os
from datetime import datetime, timezone
from uuid import uuid4

from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "swe_sim")

client = MongoClient(MONGODB_URI) if MONGODB_URI else None
database = client[MONGODB_DATABASE] if client else None


def upsert_user(github_user: dict) -> dict:
    if database is None:
        raise RuntimeError("MONGODB_URI is not configured")

    users = database.users
    users.create_index("github_id", unique=True)

    user = {
        "github_id": github_user["id"],
        "login": github_user.get("login"),
        "name": github_user.get("name"),
        "email": github_user.get("email"),
        "avatar_url": github_user.get("avatar_url"),
        "html_url": github_user.get("html_url"),
        "updated_at": datetime.now(timezone.utc),
    }
    users.update_one(
        {"github_id": user["github_id"]},
        {"$set": user, "$setOnInsert": {"created_at": user["updated_at"]}},
        upsert=True,
    )
    return user


def create_session(session_id: str, user: dict, access_token: str) -> None:
    if database is None:
        raise RuntimeError("MONGODB_URI is not configured")

    sessions = database.sessions
    sessions.create_index("expires_at", expireAfterSeconds=0)
    sessions.replace_one(
        {"session_id": session_id},
        {
            "session_id": session_id,
            "user": user,
            "access_token": access_token,
            "expires_at": datetime.fromtimestamp(
                datetime.now(timezone.utc).timestamp() + 60 * 60 * 24 * 7,
                timezone.utc,
            ),
        },
        upsert=True,
    )


def get_session(session_id: str) -> dict | None:
    if database is None:
        return None
    return database.sessions.find_one({"session_id": session_id})


def delete_session(session_id: str) -> None:
    if database is not None:
        database.sessions.delete_one({"session_id": session_id})


def create_simulation(github_id: int, title: str) -> dict:
    if database is None:
        raise RuntimeError("MONGODB_URI is not configured")

    simulations = database.simulations
    simulations.create_index([("github_id", 1), ("created_at", -1)])
    simulation = {
        "simulation_id": str(uuid4()),
        "github_id": github_id,
        "title": title,
        "status": "active",
        "created_at": datetime.now(timezone.utc),
    }
    simulations.insert_one(simulation)
    return simulation


def list_simulations(github_id: int) -> list[dict]:
    if database is None:
        raise RuntimeError("MONGODB_URI is not configured")

    return list(
        database.simulations.find(
            {"github_id": github_id},
            {"_id": 0},
        ).sort("created_at", -1)
    )


def check_database_connection() -> bool:
    if client is None:
        return False

    client.admin.command("ping")
    return True