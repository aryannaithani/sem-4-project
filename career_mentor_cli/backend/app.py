"""
backend/app.py
--------------
Full-scale FastAPI backend for the AI Career Mentor.

Endpoints:
  GET  /profile              — user profile, skills, career progress
  GET  /tasks                — all tasks
  POST /generate             — generate new tasks
  POST /complete/{task_id}   — complete a task and replan
  GET  /roadmap              — current stage progress (legacy)
  GET  /roadmap/full         — full multi-stage roadmap with all skills
  GET  /trends               — enriched trend feed with relevance
  GET  /analytics            — real-world readiness, trajectory, depth
  GET  /learning-profile     — digital twin data (pace, velocity, etc.)
  POST /mentor/chat          — conversational AI mentor
  POST /mentor/clear         — clear mentor conversation history
  POST /profile/update       — update user name / goal / github

Run with:
    cd career_mentor_cli
    uvicorn backend.app:app --reload
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Pipeline imports from main.py ─────────────────────────────────────────────
from main import (
    load_user_profile,
    get_current_state,
    generate_tasks_pipeline,
    complete_task_pipeline,
)

# ── Agent imports ─────────────────────────────────────────────────────────────
from agents.task_store        import load_tasks
from agents.roadmap_agent     import get_stage_info, load_roadmap
from agents.skill_gap_agent   import load_user_skills
from agents.trend_collector   import load_trends
from agents.analytics_agent   import get_analytics
from agents.user_model_agent  import get_learning_profile_summary
from agents.mentor_chat_agent import ask_mentor, load_chat_history, clear_chat_history

import asyncio

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Career Mentor API",
    description="Full-scale REST interface for the AI Career Mentor system.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USER_FILE = os.path.join(BASE_DIR, "data", "user.txt")

@app.on_event("startup")
async def startup_event():
    """Run background sync tasks on boot (GitHub extraction, Trend fetching)."""
    def _sync():
        try:
            from agents.github_agent import extract_skills_from_github
            profile = _profile()
            if profile.get('github'):
                extract_skills_from_github(profile['github'], profile['goal'])
        except Exception as e:
            print(f"Startup Sync Error (GitHub): {e}")
            
        try:
            from agents.trend_collector import collect_trends
            collect_trends()
        except Exception as e:
            print(f"Startup Sync Error (Trends): {e}")

    # Run sync in background so it doesn't block server startup
    asyncio.create_task(asyncio.to_thread(_sync))

# ── Request models ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    history: list = []   # list of {role, content} — optional, overrides stored

class ProfileUpdateRequest(BaseModel):
    name: str | None = None
    goal: str | None = None
    github: str | None = None


# ── Helper ────────────────────────────────────────────────────────────────────

def _profile() -> dict:
    return load_user_profile()


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/profile")
def get_profile():
    """User profile, skills, career progress, roadmap stage."""
    return get_current_state(_profile())


@app.get("/tasks")
def get_tasks():
    """All tasks (pending + completed)."""
    return {"tasks": load_tasks()}


@app.post("/generate")
def generate_tasks():
    """Run the full generation pipeline and return updated task list."""
    all_tasks = generate_tasks_pipeline(_profile())
    return {"message": "Tasks generated", "tasks": all_tasks}


@app.post("/complete/{task_id}")
def complete_task(task_id: int):
    """Mark task as complete, upgrade skill, replan."""
    profile = _profile()
    result  = complete_task_pipeline(task_id, profile)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    # Record completion in learning profile
    try:
        from agents.user_model_agent import record_task_completion
        record_task_completion(result["completed_task"])
    except Exception:
        pass

    # Refresh analytics
    try:
        from agents.analytics_agent import compute_analytics
        compute_analytics()
    except Exception:
        pass

    return {
        "message":        "Task completed",
        "completed_task": result["completed_task"],
        "updated_tasks":  result["updated_tasks"],
        "updated_skills": result["updated_skills"],
    }


@app.get("/roadmap")
def get_roadmap():
    """Current roadmap stage and progress (legacy endpoint)."""
    profile     = _profile()
    user_skills = load_user_skills()
    roadmap     = get_stage_info(profile["goal"], user_skills)
    return {
        "current_stage":  roadmap["current_stage"],
        "stage_progress": roadmap["progress_pct"],
        "skills":         user_skills,
    }


@app.get("/roadmap/full")
def get_full_roadmap():
    """
    Full multi-stage roadmap for the user's current goal.
    Returns all stages with skill-level annotations and progress per stage.
    """
    profile     = _profile()
    goal        = profile["goal"]
    user_skills = load_user_skills()
    all_roadmaps = load_roadmap()
    goal_roadmap = all_roadmaps.get(goal, {})
    user_skills_lower = {k.lower(): v.lower() for k, v in user_skills.items()}

    stages_detail = []
    for stage_name, skills in goal_roadmap.items():
        skill_details = []
        learned = 0
        for skill in skills:
            level = user_skills_lower.get(skill.lower(), "none")
            if level != "none":
                learned += 1
            skill_details.append({"name": skill, "level": level})
        total = len(skills)
        progress = int((learned / total) * 100) if total > 0 else 0
        is_complete = learned == total

        stages_detail.append({
            "name":       stage_name,
            "skills":     skill_details,
            "progress":   progress,
            "complete":   is_complete,
            "total":      total,
            "learned":    learned,
        })

    # Mark current stage
    current_stage_info = get_stage_info(goal, user_skills)
    current_stage_name = current_stage_info["current_stage"]

    return {
        "goal":          goal,
        "current_stage": current_stage_name,
        "stages":        stages_detail,
        "all_goals":     list(all_roadmaps.keys()),
    }


@app.get("/trends")
def get_trends():
    """
    Enriched trend feed: trending skills with relevance to the user's goal.
    """
    profile     = _profile()
    goal        = profile["goal"]
    user_skills = load_user_skills()
    skills_lower = {k.lower() for k in user_skills.keys()}
    trends_raw   = load_trends()

    enriched = []
    for item in trends_raw:
        if isinstance(item, str):
            name = item
        elif isinstance(item, dict):
            name = item.get("name", "")
        else:
            continue

        # Compute relevance to goal and current skills
        name_lower = name.lower()
        already_known = any(name_lower in s or s in name_lower for s in skills_lower)
        is_gap = not already_known

        enriched.append({
            "name":         name,
            "already_known": already_known,
            "is_gap":        is_gap,
            "relevance":     "high" if is_gap else "building",
        })

    return {"trends": enriched, "goal": goal}


@app.get("/analytics")
def get_analytics_endpoint():
    """
    Real-world readiness score, skill depth breakdown, career trajectory,
    trend alignment, and readiness history.
    """
    try:
        analytics = get_analytics()
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/learning-profile")
def get_learning_profile():
    """Digital twin data: learning velocity, consistency, confidence history."""
    try:
        profile = get_learning_profile_summary()
        return profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mentor/chat")
def mentor_chat(req: ChatRequest):
    """
    Conversational AI mentor. Sends user message with context and returns response.
    Optionally pass history to override server-side stored history.
    """
    try:
        # Use provided history if non-empty, else load from file
        history = req.history if req.history else None
        result  = ask_mentor(req.message, history=history)
        return {
            "response":        result["response"],
            "suggestions":     result["suggestions"],
            "history":         result["updated_history"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mentor/clear")
def mentor_clear():
    """Clears the stored mentor conversation history."""
    clear_chat_history()
    return {"message": "Conversation history cleared."}


@app.get("/mentor/history")
def mentor_history():
    """Returns the stored mentor conversation history."""
    return {"history": load_chat_history()}


@app.post("/profile/update")
def update_profile(req: ProfileUpdateRequest):
    """Update user name, goal, or github handle in user.txt."""
    current = _profile()
    name   = req.name   if req.name   is not None else current["name"]
    goal   = req.goal   if req.goal   is not None else current["goal"]
    github = req.github if req.github is not None else current["github"]

    try:
        os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
        with open(USER_FILE, "w") as f:
            f.write(f"Name: {name}\n")
            f.write(f"Goal: {goal}\n")
            f.write(f"GitHub: {github}\n")
        return {"message": "Profile updated", "name": name, "goal": goal, "github": github}
    except OSError as e:
        raise HTTPException(status_code=500, detail=str(e))
