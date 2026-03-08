"""
skill_gap_agent.py
-------------------
Agent responsible for detecting the gap between the user's current skills
and the skills required for their target career goal.

This is the core "Gap Analysis" module of the Career Mentor pipeline.
Also provides add_skill() to persist newly acquired skills.
"""

import os

# Resolve the path to data/skills.txt relative to this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_PATH = os.path.join(BASE_DIR, "data", "skills.txt")


def load_user_skills() -> list[str]:
    """
    Reads skills.txt and returns a cleaned list of the user's current skills.

    Returns:
        List[str]: A list of skills the user currently possesses.
    """
    if not os.path.exists(SKILLS_PATH):
        raise FileNotFoundError(f"[SkillGapAgent] Could not find: {SKILLS_PATH}")

    with open(SKILLS_PATH, "r") as f:
        skills = [line.strip() for line in f.readlines() if line.strip()]

    return skills


def detect_skill_gaps(user_skills: list[str], required_skills: list[str]) -> list[str]:
    """
    Compares the user's current skills against the required skills and
    returns the list of missing skills (case-insensitive comparison).

    Args:
        user_skills (List[str]): Skills the user currently has.
        required_skills (List[str]): Skills required for the target role.

    Returns:
        List[str]: Skills that the user is missing.
    """
    # Normalise to lowercase for a fair case-insensitive comparison
    user_skills_lower = {s.lower() for s in user_skills}

    gaps = [
        skill for skill in required_skills
        if skill.lower() not in user_skills_lower
    ]

    return gaps


def add_skill(skill_name: str) -> bool:
    """
    Appends *skill_name* to skills.txt if it is not already listed
    (case-insensitive comparison).

    Returns:
        True  — if the skill was newly added.
        False — if it was already present (no-op).
    """
    existing = []
    if os.path.exists(SKILLS_PATH):
        with open(SKILLS_PATH, "r") as f:
            existing = [line.strip() for line in f if line.strip()]

    if skill_name.lower() in {s.lower() for s in existing}:
        return False

    with open(SKILLS_PATH, "a") as f:
        f.write(f"\n{skill_name}")

    return True
