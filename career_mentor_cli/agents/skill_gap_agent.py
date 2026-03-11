"""
skill_gap_agent.py
-------------------
Agent responsible for detecting the gap between the user's current skills
and the skills required for their target career goal.

Provides functionality for reading and writing skill progression via JSON.
"""

import os
import json

# Resolve the path to data/skills.json relative to this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_PATH = os.path.join(BASE_DIR, "data", "skills.json")

VALID_LEVELS = ["none", "beginner", "intermediate", "advanced"]


def load_skills() -> dict:
    """
    Reads skills.json and returns a dictionary of skills and their levels.
    """
    if not os.path.exists(SKILLS_PATH):
        # Create an empty dictionary if file doesn't exist
        return {}

    with open(SKILLS_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_skills(skills: dict) -> None:
    """
    Saves the given dictionary of skills and their levels to skills.json.
    """
    with open(SKILLS_PATH, "w") as f:
        json.dump(skills, f, indent=4)


def load_user_skills() -> dict:
    """
    Legacy wrapper (now returns dict instead of list)
    """
    return load_skills()


def detect_skill_gaps(user_skills: dict, required_skills: list[str]) -> list[str]:
    """
    Compares the user's current skills against the required skills and
    returns the list of missing skills (case-insensitive comparison).
    A skill gap exists if the skill is not 'advanced'.

    Args:
        user_skills (dict): User's current skills mapping (name -> level).
        required_skills (list[str]): Skills required for the target role.

    Returns:
        list[str]: Skills that the user has not yet mastered.
    """
    # Create a lower-cased lookup dict from user skills
    user_skills_lower = {k.lower(): v.lower() for k, v in user_skills.items()}

    gaps = []
    for skill in required_skills:
        skill_lower = skill.lower()
        level = user_skills_lower.get(skill_lower, "none")
        if level != "advanced":
            gaps.append(skill)

    return gaps


def add_skill(skill_name: str) -> bool:
    """
    Updates the skill level for *skill_name* safely.
    Returns True if the skill level increased, False if it was already advanced
    or no change was made.
    """
    skills = load_skills()
    
    # Case insensitive key search
    actual_key = skill_name
    for k in skills:
        if k.lower() == skill_name.lower():
            actual_key = k
            break

    current_level = skills.get(actual_key, "none")
    
    if current_level == "none":
        skills[actual_key] = "beginner"
    elif current_level == "beginner":
        skills[actual_key] = "intermediate"
    elif current_level == "intermediate":
        skills[actual_key] = "advanced"
    elif current_level == "advanced":
        return False  # Stays advanced
    else:
        # Fallback to beginner if invalid level is present
        skills[actual_key] = "beginner"

    save_skills(skills)
    return True
