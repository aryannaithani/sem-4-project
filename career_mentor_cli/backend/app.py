"""
backend/app.py
--------------
FastAPI application that exposes the AI Career Mentor functionality as a REST API.

All heavy logic is delegated to the existing agents and pipeline functions in
main.py.  No business logic is duplicated here.

Run with:
    cd career_mentor_cli
    uvicorn backend.app:app --reload
"""

import os
import sys

# ---------------------------------------------------------------------------
# Ensure career_mentor_cli root is on sys.path so that the existing agent
# imports (and main.py pipeline functions) resolve correctly when uvicorn
# starts from the career_mentor_cli directory.
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ── Import shared pipeline functions from main.py ────────────────────────────
from main import (
    load_user_profile,
    get_current_state,
    generate_tasks_pipeline,
    complete_task_pipeline,
)

# ── Import agents used directly by some endpoints ───────────────────────────
from agents.task_store   import load_tasks
from agents.roadmap_agent import get_stage_info
from agents.skill_gap_agent import load_user_skills

# ────────────────────────────────────────────────────────────────────────────
# App setup
# ────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Career Mentor API",
    description="REST interface for the AI Career Mentor CLI system.",
    version="1.0.0",
)

# CORS — allow all origins so a future frontend (React / Vue / etc.) can connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper ───────────────────────────────────────────────────────────────────

def _profile() -> dict:
    """Loads the user profile once per request."""
    return load_user_profile()


# ────────────────────────────────────────────────────────────────────────────
# Endpoints
# ────────────────────────────────────────────────────────────────────────────

@app.get("/profile", summary="Get user profile and career progress")
def get_profile():
    """
    Returns the current user profile, skills, overall career progress,
    current roadmap stage, and stage-level progress.

    Example response:
    ```json
    {
      "name": "Aryan",
      "goal": "AI/ML Engineer",
      "skills": {"Python": "intermediate", "PyTorch": "none"},
      "career_progress": 40,
      "current_stage": "Intermediate",
      "stage_progress": 60
    }
    ```
    """
    profile = _profile()
    return get_current_state(profile)


@app.get("/tasks", summary="Get all tasks")
def get_tasks():
    """
    Returns all tasks (pending + completed) loaded from tasks.json.

    Example response:
    ```json
    {
      "tasks": [
        {"id": 1, "skill": "PyTorch", "task": "...", "status": "pending"},
        ...
      ]
    }
    ```
    """
    tasks = load_tasks()
    return {"tasks": tasks}


@app.post("/generate", summary="Generate new tasks")
def generate_tasks():
    """
    Runs the full task generation pipeline:
    loads skills → detects gaps → calls the LLM → saves tasks.json.

    Returns the updated task list.

    Example response:
    ```json
    {
      "message": "Tasks generated",
      "tasks": [...]
    }
    ```
    """
    profile   = _profile()
    all_tasks = generate_tasks_pipeline(profile)
    return {
        "message": "Tasks generated",
        "tasks":   all_tasks,
    }


@app.post("/complete/{task_id}", summary="Mark a task as complete")
def complete_task(task_id: int):
    """
    Marks the task with the given **task_id** as completed, upgrades the
    relevant skill, then replans (generates new tasks if needed).

    Returns the updated task list and updated skills.

    Example response:
    ```json
    {
      "message": "Task completed",
      "updated_tasks": [...],
      "updated_skills": {"Python": "intermediate", ...}
    }
    ```
    """
    profile = _profile()
    result  = complete_task_pipeline(task_id, profile)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return {
        "message":        "Task completed",
        "completed_task": result["completed_task"],
        "updated_tasks":  result["updated_tasks"],
        "updated_skills": result["updated_skills"],
    }


@app.get("/roadmap", summary="Get current roadmap stage")
def get_roadmap():
    """
    Returns the user's current roadmap stage, progress within that stage,
    and the full skills dictionary.

    Example response:
    ```json
    {
      "current_stage": "Intermediate",
      "stage_progress": 60,
      "skills": {"Python": "intermediate", "PyTorch": "none"}
    }
    ```
    """
    profile     = _profile()
    user_skills = load_user_skills()
    roadmap     = get_stage_info(profile["goal"], user_skills)

    return {
        "current_stage":  roadmap["current_stage"],
        "stage_progress": roadmap["progress_pct"],
        "skills":         user_skills,
    }
