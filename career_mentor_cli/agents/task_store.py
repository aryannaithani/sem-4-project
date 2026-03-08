"""
task_store.py
--------------
Handles all persistence for the task list: reading / writing tasks.json
and updating individual task statuses.

tasks.json schema:
[
    {
        "id": 1,
        "skill": "Vector Databases",
        "task": "Learn embeddings and vector databases",
        "project": "Build a semantic search engine",
        "reason": "Vector databases are used in modern AI systems",
        "status": "pending"          # "pending" | "completed"
    },
    ...
]
"""

import json
import os

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_FILE = os.path.join(BASE_DIR, "data", "tasks.json")


# ── Loaders / savers ─────────────────────────────────────────────────────────

def load_tasks() -> list[dict]:
    """
    Loads tasks from data/tasks.json.
    Returns an empty list if the file does not yet exist.
    """
    if not os.path.exists(TASKS_FILE):
        return []

    with open(TASKS_FILE, "r") as f:
        return json.load(f)


def save_tasks(tasks: list[dict]) -> None:
    """
    Writes the task list to data/tasks.json (pretty-printed).
    """
    os.makedirs(os.path.dirname(TASKS_FILE), exist_ok=True)
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


# ── Helpers ──────────────────────────────────────────────────────────────────

def next_task_id(tasks: list[dict]) -> int:
    """
    Returns the next available integer id (max existing id + 1, or 1 if empty).
    """
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def add_tasks(new_tasks: list[dict]) -> list[dict]:
    """
    Loads existing tasks, appends new ones (assigning fresh ids),
    saves the combined list, and returns it.

    Skips any task whose 'task' text is identical to an already-stored task
    to avoid exact duplicates.
    """
    existing  = load_tasks()
    existing_texts = {t["task"].lower() for t in existing}

    if existing:
        max_id: int = 1
        for existing_task in existing:
            tid = int(existing_task["id"])
            if tid > max_id:
                max_id = tid
        start_id: int = max_id + 1
    else:
        start_id: int = 1
    counter: int = 0
    added   = []
    for t in new_tasks:
        if t["task"].lower() not in existing_texts:
            t["id"] = start_id + counter
            counter = counter + 1
            existing.append(t)
            added.append(t)

    save_tasks(existing)
    return existing


def complete_task(task_id: int) -> dict | None:
    """
    Marks the task with the given *id* as 'completed'.
    Saves the updated list and returns the completed task dict,
    or None if no task with that id was found.
    """
    tasks = load_tasks()

    target = None
    for t in tasks:
        if t["id"] == task_id:
            t["status"] = "completed"
            target = t
            break

    if target is None:
        return None

    save_tasks(tasks)
    return target


def get_completed_skill(task: dict) -> str:
    """
    Returns the skill name from a task dict.
    Falls back to the first word of the 'task' field if 'skill' is missing.
    """
    return task.get("skill") or task.get("task", "").split()[0]


def get_pending_skills(tasks: list[dict]) -> set[str]:
    """
    Returns the set of skill names that still have a pending task,
    used to avoid regenerating tasks for skills already queued.
    """
    return {get_completed_skill(t).lower() for t in tasks if t.get("status") == "pending"}
