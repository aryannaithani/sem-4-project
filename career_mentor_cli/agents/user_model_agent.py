"""
agents/user_model_agent.py
---------------------------
Builds and maintains the digital twin of the user.

Tracks:
- Learning pace (tasks/week)
- Consistency score (how regularly they complete tasks)
- Confidence history per skill over time
- Project complexity trajectory
- Overall learning velocity

Reads/writes: data/learning_profile.json
"""

import json
import os
from datetime import datetime, timezone, timedelta

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "data")
PROFILE_FILE = os.path.join(DATA_DIR, "learning_profile.json")
TASKS_FILE   = os.path.join(DATA_DIR, "tasks.json")
CONFIDENCE_FILE = os.path.join(DATA_DIR, "confidence.json")


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_learning_profile() -> dict:
    """Loads learning_profile.json. Returns default structure if absent."""
    if not os.path.exists(PROFILE_FILE):
        return _default_profile()
    try:
        with open(PROFILE_FILE, "r") as f:
            data = json.load(f)
        # Ensure all keys exist (schema migration)
        default = _default_profile()
        for k, v in default.items():
            if k not in data:
                data[k] = v
        return data
    except (json.JSONDecodeError, OSError):
        return _default_profile()


def save_learning_profile(profile: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=2)


def _default_profile() -> dict:
    return {
        "last_updated": "",
        "total_tasks_completed": 0,
        "sessions": [],                   # [{date, tasks_completed}]
        "skill_confidence_history": {},   # {skill: [{date, score}]}
        "consistency_score": 0,           # 0–100
        "learning_velocity": 0.0,         # tasks per day (7-day rolling)
        "avg_task_completion_days": 0.0,  # avg days to complete a task
        "project_complexity_index": 0,    # 0–100: weighted complexity of done tasks
        "strengths": [],                  # skills with confidence >= 4
        "weak_areas": [],                 # skills with confidence <= 2
    }


# ---------------------------------------------------------------------------
# Core update logic
# ---------------------------------------------------------------------------

def _load_completed_tasks() -> list:
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            tasks = json.load(f)
        return [t for t in tasks if isinstance(t, dict) and t.get("status") == "completed"]
    except (json.JSONDecodeError, OSError):
        return []


def _load_confidence() -> dict:
    if not os.path.exists(CONFIDENCE_FILE):
        return {}
    try:
        with open(CONFIDENCE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _difficulty_weight(difficulty: str) -> int:
    """Converts difficulty to a complexity weight for the project complexity index."""
    return {"beginner": 1, "intermediate": 2, "advanced": 3}.get(
        (difficulty or "").lower(), 1
    )


def _compute_consistency_score(sessions: list) -> int:
    """
    Consistency = percentage of the last 14 days that had at least one session.
    Returns 0–100.
    """
    if not sessions:
        return 0

    session_dates = set()
    for s in sessions:
        try:
            session_dates.add(s["date"][:10])  # YYYY-MM-DD
        except (KeyError, TypeError):
            pass

    today = datetime.now(timezone.utc).date()
    active_days = sum(
        1 for i in range(14)
        if str(today - timedelta(days=i)) in session_dates
    )
    return int((active_days / 14) * 100)


def _compute_velocity(sessions: list) -> float:
    """Tasks per day over the last 7 days."""
    if not sessions:
        return 0.0

    today = datetime.now(timezone.utc).date()
    cutoff = str(today - timedelta(days=7))
    recent_total = sum(
        s.get("tasks_completed", 0)
        for s in sessions
        if s.get("date", "")[:10] >= cutoff
    )
    return round(recent_total / 7.0, 2)


def record_task_completion(task: dict) -> None:
    """
    Called whenever a task is completed. Updates the learning profile:
    - Increments total completed
    - Records today's session
    - Updates project complexity index
    - Recomputes velocity and consistency
    """
    profile = load_learning_profile()
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Update total
    profile["total_tasks_completed"] = profile.get("total_tasks_completed", 0) + 1

    # Update session log (aggregate by day)
    sessions = profile.get("sessions", [])
    today_session = next((s for s in sessions if s.get("date", "")[:10] == today_str), None)
    if today_session:
        today_session["tasks_completed"] = today_session.get("tasks_completed", 0) + 1
    else:
        sessions.append({"date": today_str, "tasks_completed": 1})
    profile["sessions"] = sessions[-60:]  # keep last 60 days

    # Update project complexity index (rolling weighted avg)
    weight = _difficulty_weight(task.get("difficulty", "beginner"))
    total = profile.get("total_tasks_completed", 1)
    old_index = profile.get("project_complexity_index", 0)
    profile["project_complexity_index"] = min(
        100, int(((old_index * (total - 1)) + (weight * 33)) / total)
    )

    # Recompute velocity and consistency
    profile["consistency_score"] = _compute_consistency_score(sessions)
    profile["learning_velocity"]  = _compute_velocity(sessions)

    # Snapshot confidence into history
    confidence = _load_confidence()
    conf_history = profile.get("skill_confidence_history", {})
    for skill, score in confidence.items():
        if skill not in conf_history:
            conf_history[skill] = []
        hist = conf_history[skill]
        if not hist or hist[-1]["date"][:10] != today_str:
            hist.append({"date": today_str, "score": score})
        conf_history[skill] = hist[-20:]  # keep last 20 entries per skill

    profile["skill_confidence_history"] = conf_history

    # Strengths and weak areas
    profile["strengths"]   = [s for s, sc in confidence.items() if int(sc) >= 4]
    profile["weak_areas"]  = [s for s, sc in confidence.items() if int(sc) <= 2]

    profile["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_learning_profile(profile)


def rebuild_profile_from_tasks() -> dict:
    """
    Rebuilds the learning profile from scratch using all completed tasks.
    Call this once to seed the profile from existing data.
    """
    completed = _load_completed_tasks()
    confidence = _load_confidence()

    profile = _default_profile()
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    profile["total_tasks_completed"] = len(completed)

    # Create a synthetic session for today with all existing completions
    if completed:
        profile["sessions"] = [{"date": today_str, "tasks_completed": len(completed)}]

    # Complexity
    if completed:
        weights = [_difficulty_weight(t.get("difficulty", "beginner")) for t in completed]
        avg_weight = sum(weights) / len(weights)
        profile["project_complexity_index"] = min(100, int(avg_weight * 33))

    # Velocity and consistency
    profile["consistency_score"] = _compute_consistency_score(profile["sessions"])
    profile["learning_velocity"]  = _compute_velocity(profile["sessions"])

    # Confidence history
    conf_history = {}
    for skill, score in confidence.items():
        conf_history[skill] = [{"date": today_str, "score": score}]
    profile["skill_confidence_history"] = conf_history
    profile["strengths"]  = [s for s, sc in confidence.items() if int(sc) >= 4]
    profile["weak_areas"] = [s for s, sc in confidence.items() if int(sc) <= 2]

    profile["last_updated"] = datetime.now(timezone.utc).isoformat()
    save_learning_profile(profile)
    return profile


def get_learning_profile_summary() -> dict:
    """Returns the full learning profile, rebuilding from tasks if needed."""
    profile = load_learning_profile()
    if not profile.get("last_updated"):
        profile = rebuild_profile_from_tasks()
    return profile
