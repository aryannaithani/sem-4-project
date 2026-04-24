"""
goal_analyzer.py
-----------------
Agent responsible for loading and parsing the required skills
for the user's target career goal.

This acts as the "Goal Understanding" module of the Career Mentor pipeline.
It extracts the required skills dynamically from the multi-stage roadmap.
"""

import os
from .roadmap_agent import load_roadmap

# Resolve the path to data/user.txt relative to this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USER_PATH = os.path.join(BASE_DIR, "data", "user.txt")


def _get_current_goal() -> str:
    """Helper to read the current goal from user.txt if not provided."""
    goal = "Software Engineer"
    if os.path.exists(USER_PATH):
        with open(USER_PATH, "r") as f:
            for line in f:
                if line.startswith("Goal:"):
                    goal = line.split("Goal:")[1].strip()
                    break
    return goal


def load_required_skills(goal: str = None) -> list[str]:
    """
    Reads the roadmap for the current goal and returns a flattened list 
    of all required skills across all stages.

    Args:
        goal (str, optional): The career goal. Defaults to reading from user.txt.

    Returns:
        List[str]: A list of required skills for the career goal.
    """
    curr_goal = goal or _get_current_goal()
    roadmap = load_roadmap()
    goal_roadmap = roadmap.get(curr_goal, {})
    
    # Flatten all skills across all stages for this goal
    skills = []
    for stage, stage_skills in goal_roadmap.items():
        skills.extend(stage_skills)
        
    return skills
