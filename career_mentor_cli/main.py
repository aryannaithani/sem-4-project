"""
main.py
--------
Entry point for the AI Career Mentor CLI.

Pipeline:
  1. Load user profile   (user.txt)
  2. Load user skills    (skills.txt)
  3. Load required skills for the goal (required_skills.txt via GoalAnalyzer)
  4. Load industry context  (context.txt)
  5. Load existing projects (projects.txt)
  6. Detect skill gaps   (SkillGapAgent)
  7. Generate tasks      (TaskGenerator via Gemini LLM)
  8. Print the final roadmap

Run:
    python main.py

Dependencies:
    pip install google-generativeai
"""

import os
import sys

# ---------------------------------------------------------------------------
# Ensure that the project root is on sys.path so imports work correctly
# regardless of where the user calls the script from.
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from agents.goal_analyzer import load_required_skills
from agents.skill_gap_agent import load_user_skills, detect_skill_gaps
from agents.task_generator import generate_tasks

# ── Data file paths ─────────────────────────────────────────────────────────
DATA_DIR      = os.path.join(BASE_DIR, "data")
USER_FILE     = os.path.join(DATA_DIR, "user.txt")
PROJECTS_FILE = os.path.join(DATA_DIR, "projects.txt")
CONTEXT_FILE  = os.path.join(DATA_DIR, "context.txt")


# ── Helper loaders ───────────────────────────────────────────────────────────

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


def load_list_file(filepath: str) -> list[str]:
    """
    Generic loader — reads a plain text file (one item per line)
    and returns a cleaned list, skipping empty lines.
    """
    if not os.path.exists(filepath):
        print(f"[Warning] {filepath} not found. Returning empty list.")
        return []

    with open(filepath, "r") as f:
        return [line.strip() for line in f if line.strip()]


# ── Display helpers ──────────────────────────────────────────────────────────

SEPARATOR = "─" * 60


def print_header(user_name: str, goal: str) -> None:
    print(f"\n{'═' * 60}")
    print(f"   🎯  CAREER MENTOR REPORT")
    print(f"{'═' * 60}")
    print(f"   User  : {user_name}")
    print(f"   Goal  : {goal}")
    print(f"{'═' * 60}\n")


def print_skill_gaps(gaps: list[str]) -> None:
    print(f"📌  Detected Skill Gaps  ({len(gaps)} found)")
    print(SEPARATOR)
    if not gaps:
        print("   ✅  No skill gaps detected — you're all set!")
    else:
        for gap in gaps:
            print(f"   •  {gap}")
    print()


def print_tasks(tasks_text: str) -> None:
    print(f"🗺️   Recommended Learning Roadmap")
    print(SEPARATOR)
    print(tasks_text)
    print(f"\n{'═' * 60}")
    print("   ✨  Good luck on your journey! Keep building!")
    print(f"{'═' * 60}\n")


# ── Main pipeline ────────────────────────────────────────────────────────────

def main() -> None:
    # ── Step 1 : Load user profile ───────────────────────────────────────────
    print("\n[1/6] Loading user profile...")
    profile   = load_user_profile()
    user_name = profile["name"]
    goal      = profile["goal"]

    # ── Step 2 : Load user's current skills ──────────────────────────────────
    print("[2/6] Loading current skills...")
    user_skills = load_user_skills()

    # ── Step 3 : Load required skills for the goal ───────────────────────────
    print("[3/6] Analyzing required skills for goal...")
    required_skills = load_required_skills()

    # ── Step 4 : Load industry context ───────────────────────────────────────
    print("[4/6] Loading industry context...")
    context = load_list_file(CONTEXT_FILE)

    # ── Step 5 : Load existing projects ──────────────────────────────────────
    print("[5/6] Loading existing projects...")
    projects = load_list_file(PROJECTS_FILE)

    # ── Step 6 : Detect skill gaps ───────────────────────────────────────────
    print("[6/6] Detecting skill gaps...\n")
    skill_gaps = detect_skill_gaps(user_skills, required_skills)

    # ── Print the report header + gaps ───────────────────────────────────────
    print_header(user_name, goal)
    print_skill_gaps(skill_gaps)

    if not skill_gaps:
        print("No tasks needed — you already have all required skills. 🎉")
        return

    # ── Step 7 : Generate personalised tasks via LLM ─────────────────────────
    print("⚙️   Generating personalised tasks via Gemini AI...\n")
    tasks_text = generate_tasks(
        skill_gaps=skill_gaps,
        context=context,
        projects=projects,
        user_name=user_name,
        goal=goal,
    )

    # ── Step 8 : Print the roadmap ────────────────────────────────────────────
    print_tasks(tasks_text)


if __name__ == "__main__":
    main()
