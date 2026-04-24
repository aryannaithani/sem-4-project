"""
agents/mentor_chat_agent.py
----------------------------
Gemini-powered conversational AI mentor.

Injects full user context (skills, progress, tasks, trends, analytics)
into every conversation so the mentor behaves like an expert who truly
knows the user.

Supports multi-turn conversation history stored in data/chat_history.json.
"""

import json
import os
from datetime import datetime, timezone

import google.generativeai as genai

BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR     = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")
SKILLS_FILE  = os.path.join(DATA_DIR, "skills.json")
TASKS_FILE   = os.path.join(DATA_DIR, "tasks.json")
TRENDS_FILE  = os.path.join(DATA_DIR, "trends.json")
USER_FILE    = os.path.join(DATA_DIR, "user.txt")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_KEY_HERE")
GEMINI_MODEL   = "gemini-2.5-flash"

MAX_HISTORY = 20  # keep last N turns


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------

def _load_json(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _load_user_profile() -> dict:
    profile = {"name": "User", "goal": "AI/ML Engineer", "github": ""}
    if not os.path.exists(USER_FILE):
        return profile
    with open(USER_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line.lower().startswith("name:"):
                profile["name"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("goal:"):
                profile["goal"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("github:"):
                profile["github"] = line.split(":", 1)[1].strip()
    return profile


def load_chat_history() -> list:
    """Returns list of {role, content} dicts."""
    return _load_json(HISTORY_FILE, [])


def save_chat_history(history: list) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    # Keep only the last MAX_HISTORY turns
    with open(HISTORY_FILE, "w") as f:
        json.dump(history[-MAX_HISTORY:], f, indent=2)


def clear_chat_history() -> None:
    save_chat_history([])


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------

def _build_system_context() -> str:
    """Constructs a rich system prompt with the user's full context."""
    profile  = _load_user_profile()
    skills   = _load_json(SKILLS_FILE, {})
    all_tasks = _load_json(TASKS_FILE, [])

    pending   = [t for t in all_tasks if t.get("status") == "pending"]
    completed = [t for t in all_tasks if t.get("status") == "completed"]

    trends_data = _load_json(TRENDS_FILE, {})
    trends = trends_data.get("trending_skills", [])
    trend_names = []
    for t in trends[:8]:
        if isinstance(t, str):
            trend_names.append(t)
        elif isinstance(t, dict):
            trend_names.append(t.get("name", ""))

    # Skills summary
    skills_str = "\n".join(
        f"  - {skill}: {level}" for skill, level in skills.items()
    ) if skills else "  No skills recorded yet."

    # Pending tasks (max 5)
    pending_str = "\n".join(
        f"  [{t.get('id', '?')}] {t.get('task', '')} (Skill: {t.get('skill', '-')}, Difficulty: {t.get('difficulty', '-')})"
        for t in pending[:5]
    ) if pending else "  None currently."

    # Recent completions (max 5)
    completed_str = "\n".join(
        f"  - {t.get('task', '')}" for t in completed[-5:]
    ) if completed else "  None yet."

    trends_str = ", ".join(trend_names) if trend_names else "N/A"

    context = f"""You are an elite AI Career Mentor — not a chatbot, but a genuine mentor built to actively engineer {profile['name']}'s career in real time.

You know {profile['name']} deeply:
- Career Goal: {profile['goal']}
- GitHub: {profile['github'] or 'Not set'}

CURRENT SKILLS:
{skills_str}

ACTIVE TASKS:
{pending_str}

RECENTLY COMPLETED:
{completed_str}

CURRENT INDUSTRY TRENDS:
{trends_str}

YOUR MENTOR PHILOSOPHY:
1. Always be specific — never say "learn X", say "build Y using X, here's exactly how"
2. Challenge the user when they're underperforming; celebrate when they excel
3. Connect every recommendation to their goal: {profile['goal']}
4. Be direct and opinionated — give a single best path, not a menu of options
5. Think like a strategist: consider what the industry demands RIGHT NOW
6. When the user completes something, immediately push them to the next challenge
7. Keep responses concise but packed with insight — no fluff, no generic advice

Today: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
"""
    return context.strip()


# ---------------------------------------------------------------------------
# Core chat function
# ---------------------------------------------------------------------------

def ask_mentor(message: str, history: list | None = None) -> dict:
    """
    Sends a message to the Gemini mentor and returns a response dict:
    {
        "response": str,
        "suggestions": [str, str, str],  # 3 follow-up chips
        "updated_history": [...]
    }

    history: list of {role, content} dicts. If None, loads from file.
    """
    if history is None:
        history = load_chat_history()

    # Fallback if no API key
    if GEMINI_API_KEY == "YOUR_KEY_HERE":
        response_text = _fallback_response(message, history)
        updated_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response_text},
        ]
        save_chat_history(updated_history)
        return {
            "response": response_text,
            "suggestions": _generate_suggestions(message),
            "updated_history": updated_history,
        }

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=_build_system_context(),
        )

        # Convert history to Gemini format
        gemini_history = []
        for turn in history[-MAX_HISTORY:]:
            role = "user" if turn.get("role") == "user" else "model"
            gemini_history.append({
                "role": role,
                "parts": [{"text": turn.get("content", "")}],
            })

        chat = model.start_chat(history=gemini_history)
        resp = chat.send_message(message)
        response_text = resp.text.strip()

        # Generate 3 follow-up suggestions
        suggestions = _ai_generate_suggestions(model, message, response_text)

    except Exception as e:
        print(f"[MentorChat] ⚠️ Gemini call failed: {e}")
        response_text = _fallback_response(message, history)
        suggestions   = _generate_suggestions(message)

    updated_history = history + [
        {"role": "user",      "content": message},
        {"role": "assistant", "content": response_text},
    ]
    save_chat_history(updated_history)

    return {
        "response":         response_text,
        "suggestions":      suggestions,
        "updated_history":  updated_history,
    }


def _ai_generate_suggestions(model, user_msg: str, mentor_response: str) -> list:
    """Asks the LLM to generate 3 short follow-up question chips."""
    try:
        prompt = (
            f"Based on this conversation:\nUser: {user_msg}\nMentor: {mentor_response}\n\n"
            "Generate exactly 3 short (max 8 words each) follow-up questions the user might want to ask. "
            "Output ONLY the 3 questions, one per line, no numbering, no extra text."
        )
        resp = model.generate_content(prompt)
        lines = [l.strip() for l in resp.text.strip().splitlines() if l.strip()]
        return lines[:3] if len(lines) >= 3 else _generate_suggestions(user_msg)
    except Exception:
        return _generate_suggestions(user_msg)


def _generate_suggestions(message: str) -> list:
    """Static fallback suggestion chips."""
    msg = message.lower()
    if any(w in msg for w in ["next", "what", "do"]):
        return [
            "What project should I build first?",
            "How long will this take me?",
            "What's trending in my field right now?",
        ]
    elif any(w in msg for w in ["skill", "learn", "study"]):
        return [
            "How do I practice this skill?",
            "What's the best resource for this?",
            "Am I on track for my goal?",
        ]
    else:
        return [
            "What should I focus on this week?",
            "Am I ready for a job in my field?",
            "What are the hottest skills right now?",
        ]


def _fallback_response(message: str, history: list) -> str:
    """Returns a static but useful mentor response when the API is unavailable."""
    msg = message.lower()
    if any(w in msg for w in ["next", "what should", "focus"]):
        return (
            "Based on your current profile, I'd focus on deepening your practical skills "
            "through project-based work. Pick one gap skill and build a complete, deployable project "
            "around it — that's what interviewers and employers actually evaluate. "
            "Don't just read or watch tutorials; ship something real."
        )
    elif any(w in msg for w in ["ready", "job", "interview"]):
        return (
            "Real-world readiness isn't about having all skills — it's about depth in the right ones. "
            "Build 2-3 portfolio projects that demonstrate end-to-end capability: "
            "data → model → deployment → monitoring. That's the full stack an employer wants to see."
        )
    elif any(w in msg for w in ["trend", "market", "demand"]):
        return (
            "Right now the hottest areas are: RAG Systems, AI Agents, MLOps, and LLM Fine-tuning. "
            "The market has shifted away from pure model training toward application-layer engineering. "
            "If you can build and deploy LLM-powered applications, you're immediately valuable."
        )
    else:
        return (
            "Great question. Here's my honest assessment: the fastest path to your goal isn't studying more — "
            "it's building more. Every skill gap should be closed through a project, not a course. "
            "What specific area do you want to tackle? I'll design the exact project for you."
        )
