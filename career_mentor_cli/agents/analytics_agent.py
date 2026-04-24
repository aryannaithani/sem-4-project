"""
agents/analytics_agent.py
--------------------------
Computes higher-order metrics about the user's career progress.

Outputs:
- real_world_readiness (0–100): weighted by skill depth, project complexity, trend alignment
- skill_depth_breakdown: surface vs deep per skill
- career_trajectory: accelerating / steady / stagnating
- trend_alignment_score: % of user's skills that are currently in demand
- readiness_history: time-series of readiness scores

Reads/writes: data/analytics.json
"""

import json
import os
from datetime import datetime, timezone

BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR        = os.path.join(BASE_DIR, "data")
ANALYTICS_FILE  = os.path.join(DATA_DIR, "analytics.json")
SKILLS_FILE     = os.path.join(DATA_DIR, "skills.json")
TRENDS_FILE     = os.path.join(DATA_DIR, "trends.json")
TASKS_FILE      = os.path.join(DATA_DIR, "tasks.json")
CONFIDENCE_FILE = os.path.join(DATA_DIR, "confidence.json")

LEVEL_WEIGHTS = {"none": 0, "beginner": 25, "intermediate": 60, "advanced": 100}

# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_analytics() -> dict:
    if not os.path.exists(ANALYTICS_FILE):
        return _default_analytics()
    try:
        with open(ANALYTICS_FILE, "r") as f:
            data = json.load(f)
        default = _default_analytics()
        for k, v in default.items():
            if k not in data:
                data[k] = v
        return data
    except (json.JSONDecodeError, OSError):
        return _default_analytics()


def save_analytics(data: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(ANALYTICS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _default_analytics() -> dict:
    return {
        "last_updated": "",
        "real_world_readiness": 0,
        "skill_depth_breakdown": {},
        "career_trajectory": "starting",
        "trend_alignment_score": 0,
        "readiness_history": [],       # [{date, score}]
        "top_strength_skills": [],
        "highest_priority_gaps": [],
    }


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_skills() -> dict:
    if not os.path.exists(SKILLS_FILE):
        return {}
    try:
        with open(SKILLS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _load_trends() -> list:
    if not os.path.exists(TRENDS_FILE):
        return []
    try:
        with open(TRENDS_FILE, "r") as f:
            data = json.load(f)
        raw = data.get("trending_skills", [])
        # Support both old (list of strings) and new (list of dicts) format
        result = []
        for item in raw:
            if isinstance(item, str):
                result.append(item.lower())
            elif isinstance(item, dict):
                result.append(item.get("name", "").lower())
        return result
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


def _load_tasks() -> list:
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------

def _compute_skill_depth(skills: dict, confidence: dict) -> dict:
    """
    For each skill, determines depth category:
    - 'surface': level beginner and confidence < 3 (or no confidence)
    - 'developing': intermediate, or beginner with confidence >= 3
    - 'deep': advanced, or intermediate with confidence >= 4
    """
    depth_map = {}
    for skill, level in skills.items():
        conf = confidence.get(skill)
        conf_int = int(conf) if conf is not None else None

        if level == "advanced":
            depth = "deep"
        elif level == "intermediate":
            depth = "deep" if conf_int and conf_int >= 4 else "developing"
        elif level == "beginner":
            depth = "developing" if conf_int and conf_int >= 3 else "surface"
        else:
            depth = "surface"

        depth_map[skill] = {
            "level": level,
            "depth": depth,
            "confidence": conf_int,
        }
    return depth_map


def _compute_trend_alignment(skills: dict, trends: list) -> int:
    """% of non-none skills that appear in the trending list."""
    active_skills = {s.lower() for s, l in skills.items() if l != "none"}
    if not active_skills:
        return 0
    aligned = sum(
        1 for s in active_skills
        if any(s in t or t in s for t in trends)
    )
    return min(100, int((aligned / len(active_skills)) * 100))


def _compute_real_world_readiness(
    skills: dict,
    confidence: dict,
    depth_map: dict,
    completed_tasks: list,
    trend_alignment: int,
    complexity_index: int,
) -> int:
    """
    Weighted readiness score (0–100):
    - 40% skill depth score (avg weighted level × confidence boost)
    - 30% project complexity index
    - 20% trend alignment
    - 10% task volume
    """
    # Skill depth score
    if skills:
        depth_weights = {"surface": 20, "developing": 55, "deep": 90}
        skill_scores = []
        for skill, info in depth_map.items():
            base = depth_weights.get(info["depth"], 20)
            conf_boost = (info["confidence"] or 3) / 5.0  # normalize
            skill_scores.append(base * conf_boost)
        skill_depth_score = sum(skill_scores) / len(skill_scores) if skill_scores else 0
    else:
        skill_depth_score = 0

    # Task volume component (capped at 100 beyond 20 tasks)
    task_volume = min(100, len(completed_tasks) * 5)

    rwr = (
        skill_depth_score * 0.40 +
        complexity_index  * 0.30 +
        trend_alignment   * 0.20 +
        task_volume       * 0.10
    )
    return min(100, int(rwr))


def _compute_trajectory(history: list) -> str:
    """
    Compares last 3 readiness entries to determine direction.
    """
    if len(history) < 2:
        return "starting"
    scores = [h["score"] for h in history[-3:]]
    delta = scores[-1] - scores[0]
    if delta >= 5:
        return "accelerating"
    elif delta <= -5:
        return "regressing"
    else:
        return "steady"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_analytics(learning_profile: dict | None = None) -> dict:
    """
    Computes all analytics and saves to analytics.json.
    Pass learning_profile if available to avoid re-loading.
    Returns the analytics dict.
    """
    from agents.user_model_agent import get_learning_profile_summary

    if learning_profile is None:
        learning_profile = get_learning_profile_summary()

    skills       = _load_skills()
    trends       = _load_trends()
    confidence   = _load_confidence()
    all_tasks    = _load_tasks()
    completed    = [t for t in all_tasks if t.get("status") == "completed"]
    complexity   = learning_profile.get("project_complexity_index", 0)

    depth_map       = _compute_skill_depth(skills, confidence)
    trend_alignment = _compute_trend_alignment(skills, trends)
    readiness       = _compute_real_world_readiness(
        skills, confidence, depth_map, completed, trend_alignment, complexity
    )

    analytics = load_analytics()
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Update readiness history (one entry per day)
    history = analytics.get("readiness_history", [])
    if history and history[-1]["date"][:10] == today_str:
        history[-1]["score"] = readiness
    else:
        history.append({"date": today_str, "score": readiness})
    history = history[-30:]  # keep 30 days

    # Top strength skills (deep, sorted by confidence)
    strengths = sorted(
        [(s, info) for s, info in depth_map.items() if info["depth"] == "deep"],
        key=lambda x: (x[1]["confidence"] or 0),
        reverse=True,
    )

    # Highest priority gaps (surface skills, sorted by trend alignment)
    trend_set = set(trends)
    gaps = sorted(
        [(s, info) for s, info in depth_map.items() if info["depth"] == "surface"],
        key=lambda x: any(x[0].lower() in t or t in x[0].lower() for t in trend_set),
        reverse=True,
    )

    analytics.update({
        "last_updated":           datetime.now(timezone.utc).isoformat(),
        "real_world_readiness":   readiness,
        "skill_depth_breakdown":  depth_map,
        "career_trajectory":      _compute_trajectory(history),
        "trend_alignment_score":  trend_alignment,
        "readiness_history":      history,
        "top_strength_skills":    [s for s, _ in strengths[:5]],
        "highest_priority_gaps":  [s for s, _ in gaps[:5]],
    })

    save_analytics(analytics)
    return analytics


def get_analytics() -> dict:
    """Returns analytics, computing fresh if > 1 hour stale."""
    data = load_analytics()
    last = data.get("last_updated", "")
    if last:
        try:
            dt = datetime.fromisoformat(last)
            age_seconds = (datetime.now(timezone.utc) - dt).total_seconds()
            if age_seconds < 3600:
                return data
        except ValueError:
            pass
    return compute_analytics()
