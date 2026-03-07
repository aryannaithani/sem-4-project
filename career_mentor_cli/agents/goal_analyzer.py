"""
goal_analyzer.py
-----------------
Agent responsible for loading and parsing the required skills
for the user's target career goal.

This acts as the "Goal Understanding" module of the Career Mentor pipeline.
"""

import os

# Resolve the path to data/required_skills.txt relative to this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED_SKILLS_PATH = os.path.join(BASE_DIR, "data", "required_skills.txt")


def load_required_skills() -> list[str]:
    """
    Reads required_skills.txt and returns a cleaned list of required skill strings.

    Returns:
        List[str]: A list of required skills for the career goal.
    """
    if not os.path.exists(REQUIRED_SKILLS_PATH):
        raise FileNotFoundError(f"[GoalAnalyzer] Could not find: {REQUIRED_SKILLS_PATH}")

    with open(REQUIRED_SKILLS_PATH, "r") as f:
        skills = [line.strip() for line in f.readlines() if line.strip()]

    return skills
