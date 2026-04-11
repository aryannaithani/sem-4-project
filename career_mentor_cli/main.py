"""
main.py
--------
Entry point for the AI Career Mentor CLI.

Supports two commands:

    python main.py
        Load existing tasks from data/tasks.json if present;
        otherwise run the full pipeline and generate new tasks.
        Display the task board with [ ] / [X] status markers.

    python main.py complete <task_id>
        Mark the given task as completed, update data/skills.txt,
        detect remaining skill gaps, and append any newly generated
        tasks to data/tasks.json before displaying the updated board.

Dependencies:
    pip install google-generativeai
"""

import json
import os
import sys

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so imports work correctly regardless
# of where the user calls the script from.
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from agents.goal_analyzer   import load_required_skills
from agents.skill_gap_agent import load_user_skills, detect_skill_gaps, add_skill
from agents.task_generator  import generate_tasks_structured
from agents.task_store      import load_tasks, add_tasks, complete_task, get_completed_skill, get_pending_skills
from agents.roadmap_agent   import get_stage_info
from agents.github_agent    import run_github_skill_sync
from agents.trend_collector import run_trend_update, load_trends

# ── Data file paths ──────────────────────────────────────────────────────────
DATA_DIR         = os.path.join(BASE_DIR, "data")
PROJECTS_FILE    = os.path.join(DATA_DIR, "projects.txt")
CONTEXT_FILE     = os.path.join(DATA_DIR, "context.txt")
USER_FILE        = os.path.join(DATA_DIR, "user.txt")
CONFIDENCE_FILE  = os.path.join(DATA_DIR, "confidence.json")

# ── Display constants ────────────────────────────────────────────────────────
BAR  = "─" * 60
DBAR = "═" * 60

# ── Difficulty label colours (unicode badges) ─────────────────────────────────
_DIFF_BADGE = {
    "beginner":     "🟢 Beginner",
    "intermediate": "🟡 Intermediate",
    "advanced":     "🔴 Advanced",
}


# ── Confidence storage helpers ────────────────────────────────────────────────

def load_confidence() -> dict:
    """Loads confidence scores from data/confidence.json. Returns {} if absent."""
    if not os.path.exists(CONFIDENCE_FILE):
        return {}
    try:
        with open(CONFIDENCE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_confidence(data: dict) -> None:
    """Persists confidence scores to data/confidence.json."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIDENCE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def ask_confidence(skill_name: str) -> None:
    """
    Optionally prompts the user for a confidence score (1-5) after completing a task.
    Stores the result in confidence.json. Silently skips if the user presses Enter.
    """
    try:
        raw = input(
            f"\n💡 How confident are you in  '{skill_name}'?  "
            "(1 = very low  …  5 = very high, Enter to skip): "
        ).strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return

    if not raw:
        return  # user skipped

    try:
        score = int(raw)
        if 1 <= score <= 5:
            data = load_confidence()
            data[skill_name] = score
            save_confidence(data)
            if score <= 2:
                print(f"   📝  Got it — next tasks for '{skill_name}' will be reinforcement-focused.")
            elif score >= 4:
                print(f"   📝  Great confidence! Next tasks for '{skill_name}' will push further.")
            else:
                print(f"   📝  Confidence noted — progression will stay on track.")
        else:
            print("   (Score out of range — skipping.)")
    except ValueError:
        print("   (Not a number — skipping.)")


# ── Generic file loaders ─────────────────────────────────────────────────────

def load_user_profile() -> dict:
    """
    Parses user.txt and returns a dict with 'name', 'goal', and 'github' keys.
    Expected format:
        Name: Aryan
        Goal: AI/ML Engineer
        GitHub: aryan-naithani
    """
    profile = {"name": "User", "goal": "Unknown", "github": ""}
    if not os.path.exists(USER_FILE):
        print(f"[Warning] {USER_FILE} not found. Using defaults.")
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


def load_list_file(filepath: str) -> list:
    """
    Generic loader — reads a plain-text file (one item per line)
    and returns a cleaned list, skipping empty lines.
    """
    if not os.path.exists(filepath):
        print(f"[Warning] {filepath} not found. Returning empty list.")
        return []

    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]


# ── Display helpers ──────────────────────────────────────────────────────────

def _diff_badge(task: dict) -> str:
    """Returns a readable difficulty badge string, or empty string if absent."""
    raw = task.get("difficulty", "").lower().strip()
    return _DIFF_BADGE.get(raw, f"⚪ {raw.capitalize()}" if raw else "")


def print_task_board(tasks: list, user_name: str = "User", goal: str = "") -> None:
    """Renders the task board with [ ] / [X] status markers and career progress."""
    user_skills = load_user_skills()
    required_skills = load_required_skills()

    # Calculate career progress
    total_required = len(required_skills)
    learned_count = sum(1 for rs in required_skills
                        if user_skills.get(rs, user_skills.get(rs.lower(), "none")) != "none")
    progress_pct = int((learned_count / total_required * 100)) if total_required > 0 else 0

    # Roadmap Progress
    roadmap_info = get_stage_info(goal, user_skills)
    current_stage = roadmap_info["current_stage"]
    stage_progress = roadmap_info["progress_pct"]

    print(f"\n{DBAR}")
    print(f"   📋  AI CAREER MENTOR")
    if user_name and user_name != "User":
        print(f"   👤  {user_name}  •  Goal: {goal}")
    else:
        print(f"   🎯  Goal: {goal}")
    print(f"\n   📍  Current Stage: {current_stage}")
    print(f"   📊  Stage Progress: {stage_progress}%")
    print(f"   📈  Career Progress: {progress_pct}%")
    print(f"{DBAR}")

    print("\n   Active Tasks\n")

    if not tasks:
        print("   (No tasks yet — run  python main.py  to generate some!)")
    else:
        for t in tasks:
            if t.get("status") != "completed":
                task_id   = t.get("id", "?")
                task_text = t.get("task", "(unnamed task)")
                skill     = t.get("skill", "-")
                badge     = _diff_badge(t)
                print(f"   [ ] Task {task_id}: {task_text}")
                if badge:
                    print(f"       Skill: {skill}  |  Difficulty: {badge}\n")
                else:
                    print(f"       Skill: {skill}\n")

    # Completed tasks
    done = [t for t in tasks if t.get("status") == "completed"]
    if done:
        print(f"   {'─' * 54}")
        print("   Completed Tasks\n")
        for t in done:
            task_id   = t.get("id", "?")
            task_text = t.get("task", "(unnamed task)")
            skill     = t.get("skill", "-")
            badge     = _diff_badge(t)
            print(f"   [X] Task {task_id}: {task_text}")
            if badge:
                print(f"       Skill: {skill}  |  Difficulty: {badge}\n")
            else:
                print(f"       Skill: {skill}\n")

    print(DBAR)
    pending = [t for t in tasks if t.get("status") != "completed"]
    print(f"   ✅  {len(done)} completed   •   ⏳  {len(pending)} pending")
    print(f"{DBAR}\n")


def print_task_detail(task: dict) -> None:
    """Prints the full details of a single task (used after completion)."""
    badge = _diff_badge(task)
    print(f"\n{BAR}")
    print(f"   ✅  Task {task.get('id')} marked as COMPLETED")
    print(f"{BAR}")
    print(f"   Skill      : {task.get('skill', '-')}")
    if badge:
        print(f"   Difficulty : {badge}")
    print(f"   Task       : {task.get('task', '-')}")
    print(f"   Reason     : {task.get('reason', '-')}")
    print(f"{BAR}\n")


def print_gap_summary(gaps: list) -> None:
    """Prints detected skill gaps."""
    if gaps:
        print(f"📌  {len(gaps)} remaining skill gap(s): {', '.join(gaps)}")
    else:
        print("🎉  No remaining skill gaps — you're all set!")


# ── Pipeline helpers ─────────────────────────────────────────────────────────

def run_generation_pipeline(profile: dict) -> list:
    """
    Full pipeline: load skills/context/projects → detect gaps
    → generate structured tasks → save to tasks.json.

    Returns the full (combined) task list after saving.
    """
    user_name = profile["name"]
    goal      = profile["goal"]

    print("[1/4] Loading skills and required skills...")
    user_skills     = load_user_skills()
    required_skills = load_required_skills()

    print("[2/4] Loading context, projects, confidence, and completed tasks...")
    context         = load_list_file(CONTEXT_FILE)
    projects        = load_list_file(PROJECTS_FILE)
    confidence_data = load_confidence()

    # Merge live trends into context (dedup, trends first)
    live_trends = load_trends()
    seen = set(c.lower() for c in context)
    for trend in live_trends:
        if trend.lower() not in seen:
            context.append(trend)
            seen.add(trend.lower())

    # Collect completed task descriptions for the LLM context
    all_current_tasks = load_tasks()
    completed_task_texts = [
        t.get("task", "")
        for t in all_current_tasks
        if t.get("status") == "completed" and t.get("task")
    ]

    print("[3/4] Detecting skill gaps for current stage...")
    roadmap_info = get_stage_info(goal, user_skills)
    stage_skills    = roadmap_info["stage_skills"]
    current_stage   = roadmap_info["current_stage"]

    all_skill_gaps = detect_skill_gaps(user_skills, required_skills)
    # Only generate tasks for skills in the current stage
    skill_gaps = [g for g in all_skill_gaps if g.lower() in [s.lower() for s in stage_skills]]

    # Enforce task limit
    MAX_ACTIVE_TASKS = 5
    existing_pending = [t for t in all_current_tasks if t.get("status") == "pending"]
    pending_skills   = {get_completed_skill(t).lower() for t in existing_pending}

    new_gaps = [g for g in skill_gaps if g.lower() not in pending_skills]

    slots_available = MAX_ACTIVE_TASKS - len(existing_pending)

    if not new_gaps or slots_available <= 0:
        print("   No new gaps to generate tasks for, or max tasks reached.\n")
        return all_current_tasks

    # Limit to available slots
    new_gaps = new_gaps[:slots_available]

    print(f"[4/4] Generating adaptive tasks for {len(new_gaps)} gap(s) via AI...\n")
    new_tasks = generate_tasks_structured(
        skill_gaps=new_gaps,
        context=context,
        projects=projects,
        user_name=user_name,
        goal=goal,
        skill_levels=user_skills,
        completed_tasks=completed_task_texts,
        current_stage=current_stage,
        confidence_data=confidence_data,
    )

    all_tasks = add_tasks(new_tasks)
    return all_tasks


# ── Command handlers ─────────────────────────────────────────────────────────

def handle_default(profile: dict) -> None:
    """
    `python main.py`
    Loads tasks from tasks.json if they exist; otherwise generates them.
    """
    existing = load_tasks()

    if existing:
        print("📂  Loading existing tasks from tasks.json...\n")
        print_task_board(existing, profile["name"], profile["goal"])
    else:
        print("🆕  No saved tasks found — generating a personalised roadmap...\n")
        all_tasks = run_generation_pipeline(profile)
        print_task_board(all_tasks, profile["name"], profile["goal"])
        print("💾  Tasks saved to  data/tasks.json\n")


def handle_complete(task_id_str: str, profile: dict) -> None:
    """
    `python main.py complete <task_id>`
    Marks a task complete, updates skills.json, records optional confidence,
    and triggers replanning.
    """
    # ── Validate the id argument ─────────────────────────────────────────────
    try:
        task_id = int(task_id_str)
    except ValueError:
        print(f"\n[Error] '{task_id_str}' is not a valid task id. "
              f"Usage: python main.py complete <task_id>\n")
        sys.exit(1)

    # ── Mark the task as completed ───────────────────────────────────────────
    completed = complete_task(task_id)
    if completed is None:
        print(f"\n[Error] No task with id {task_id} found in tasks.json.\n")
        sys.exit(1)

    print_task_detail(completed)

    # ── Update skills ────────────────────────────────────────────────────────
    skill_name = get_completed_skill(completed)

    # Check current stage before upgrade
    user_skills_before  = load_user_skills()
    stage_info_before   = get_stage_info(profile["goal"], user_skills_before)

    was_upgraded        = add_skill(skill_name)
    user_skills_after   = load_user_skills()
    stage_info_after    = get_stage_info(profile["goal"], user_skills_after)

    if was_upgraded:
        print(f"📚  Skill upgraded in skills.json:  {skill_name}")
    else:
        print(f"📚  Skill level maintained: {skill_name} (no change)")

    # Check for stage completion
    if stage_info_before["current_stage"] != stage_info_after["current_stage"]:
        print(f"\n🌟  Stage Completed: {stage_info_before['current_stage']}")
        print(f"🔓  New Stage Unlocked: {stage_info_after['current_stage']}")

    # ── Optional confidence feedback ─────────────────────────────────────────
    ask_confidence(skill_name)

    print()

    # ── Replanning: detect new gaps and generate tasks if needed ─────────────
    print("🔄  Replanning based on updated skills...\n")
    all_tasks = run_generation_pipeline(profile)

    # ── Summarise remaining gaps ─────────────────────────────────────────────
    user_skills     = load_user_skills()
    required_skills = load_required_skills()
    remaining_gaps  = detect_skill_gaps(user_skills, required_skills)
    print_gap_summary(remaining_gaps)
    print()

    # ── Display updated task board ────────────────────────────────────────────
    print_task_board(all_tasks, profile["name"], profile["goal"])


# ── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    profile = load_user_profile()

    # ── GitHub skill sync (runs on every startup, cached for 1 hour) ─────────
    print("🔍  Analysing GitHub profile for skill updates...")
    run_github_skill_sync()

    # ── Industry trend update (runs on every startup, cached for 24 hours) ───
    print("📈  Checking industry trends...")
    run_trend_update()

    args = sys.argv[1:]   # strip the script name

    if len(args) == 0:
        handle_default(profile)

    elif len(args) == 2 and args[0].lower() == "complete":
        handle_complete(args[1], profile)

    else:
        print("\nUsage:")
        print("  python main.py                   — show / generate task board")
        print("  python main.py complete <id>     — complete a task and replan\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
