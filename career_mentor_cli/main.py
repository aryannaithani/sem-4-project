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

# ── Data file paths ──────────────────────────────────────────────────────────
DATA_DIR      = os.path.join(BASE_DIR, "data")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.txt")
CONTEXT_FILE  = os.path.join(DATA_DIR, "context.txt")
USER_FILE     = os.path.join(DATA_DIR, "user.txt")

# ── Display constants ────────────────────────────────────────────────────────
BAR  = "─" * 60
DBAR = "═" * 60


# ── Generic file loaders ─────────────────────────────────────────────────────

def load_user_profile() -> dict:
    """
    Parses user.txt and returns a dict with 'name' and 'goal' keys.
    Expected format:
        Name: Aryan
        Goal: AI/ML Engineer
    """
    profile = {"name": "User", "goal": "Unknown"}
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

def print_task_board(tasks: list, user_name: str = "User", goal: str = "") -> None:
    """Renders the task board with [ ] / [X] status markers and career progress."""
    user_skills = load_user_skills()
    required_skills = load_required_skills()
    
    # Calculate career progress
    total_required = len(required_skills)
    learned_count = sum(1 for rs in required_skills 
                        if user_skills.get(rs, user_skills.get(rs.lower(), "none")) != "none")
    
    progress_pct = int((learned_count / total_required * 100)) if total_required > 0 else 0

    print(f"\n{DBAR}")
    print(f"   📋  CAREER MENTOR TASK BOARD")
    if user_name and user_name != "User":
        print(f"   👤  {user_name}  •  Goal: {goal}")
    print(f"   📈  Career Progress: {progress_pct}%")
    print(f"{DBAR}")

    print("\n   Active Tasks\n")

    if not tasks:
        print("   (No tasks yet — run  python main.py  to generate some!)")
    else:
        for t in tasks:
            if t.get("status") != "completed":
                task_id = t.get("id", "?")
                task_text = t.get("task", "(unnamed task)")
                skill_text = t.get("skill", "-")
                print(f"   [ ] Task {task_id}: {task_text}")
                print(f"       Skill: {skill_text}\n")
    
    # Also show completed tasks
    done = [t for t in tasks if t.get("status") == "completed"]
    for t in done:
        task_id = t.get("id", "?")
        task_text = t.get("task", "(unnamed task)")
        skill_text = t.get("skill", "-")
        print(f"   [X] Task {task_id}: {task_text}")
        print(f"       Skill: {skill_text}\n")

    print(DBAR)
    pending = [t for t in tasks if t.get("status") != "completed"]
    print(f"   ✅  {len(done)} completed   •   ⏳  {len(pending)} pending")
    print(f"{DBAR}\n")


def print_task_detail(task: dict) -> None:
    """Prints the full details of a single task (used after completion)."""
    print(f"\n{BAR}")
    print(f"   ✅  Task {task.get('id')} marked as COMPLETED")
    print(f"{BAR}")
    print(f"   Skill    : {task.get('skill', '-')}")
    print(f"   Task     : {task.get('task', '-')}")
    print(f"   Project  : {task.get('project', '-')}")
    print(f"   Reason   : {task.get('reason', '-')}")
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

    print("[2/4] Loading context and projects...")
    context  = load_list_file(CONTEXT_FILE)
    projects = load_list_file(PROJECTS_FILE)

    print("[3/4] Detecting skill gaps...")
    skill_gaps = detect_skill_gaps(user_skills, required_skills)

    # Enforce task limit
    MAX_ACTIVE_TASKS = 5
    current_tasks = load_tasks()
    existing_pending = [t for t in current_tasks if t.get("status") == "pending"]
    pending_skills = {get_completed_skill(t).lower() for t in existing_pending}
    
    new_gaps = [g for g in skill_gaps if g.lower() not in pending_skills]

    slots_available = MAX_ACTIVE_TASKS - len(existing_pending)

    if not new_gaps or slots_available <= 0:
        print("   No new gaps to generate tasks for, or max tasks reached.\n")
        return current_tasks

    # Limit to available slots
    new_gaps = new_gaps[:slots_available]

    print(f"[4/4] Generating tasks for {len(new_gaps)} gap(s) via AI...\n")
    new_tasks = generate_tasks_structured(
        skill_gaps=new_gaps,
        context=context,
        projects=projects,
        user_name=user_name,
        goal=goal,
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
    Marks a task complete, updates skills.txt, and triggers replanning.
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
    was_upgraded = add_skill(skill_name)
    if was_upgraded:
        print(f"📚  Skill upgraded in skills.json:  {skill_name}")
    else:
        print(f"📚  Skill level maintained: {skill_name} (no change)")

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
