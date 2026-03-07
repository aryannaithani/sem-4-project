"""
skill_gap_agent.py
-------------------
Agent responsible for detecting the gap between the user's current skills
and the skills required for their target career goal.

This is the core "Gap Analysis" module of the Career Mentor pipeline.
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
