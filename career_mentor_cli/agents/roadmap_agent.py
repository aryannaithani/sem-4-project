import os
import json

# Resolve paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROADMAP_PATH = os.path.join(BASE_DIR, "data", "roadmap.json")

def load_roadmap() -> dict:
    """Reads roadmap.json and returns the career progression data."""
    if not os.path.exists(ROADMAP_PATH):
        return {}
    with open(ROADMAP_PATH, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def get_stage_info(goal: str, user_skills: dict) -> dict:
    """
    Determines current stage, progress, and skills for a given goal.
    
    Algorithm:
    1. Load roadmap for goal.
    2. Evaluate each stage in order.
    3. If a stage has any skill at level "none", that is the current stage.
    """
    roadmaps = load_roadmap()
    goal_roadmap = roadmaps.get(goal, {})
    
    if not goal_roadmap:
        return {
            "current_stage": "Unknown",
            "progress_pct": 0,
            "stage_skills": [],
            "all_stages": []
        }

    stages = list(goal_roadmap.keys())
    user_skills_lower = {k.lower(): v.lower() for k, v in user_skills.items()}

    current_stage = stages[-1] # Default to last stage if all completed
    
    for stage in stages:
        stage_skills = goal_roadmap[stage]
        # Check if stage is completed (all skills at least 'beginner')
        is_completed = True
        for skill in stage_skills:
            level = user_skills_lower.get(skill.lower(), "none")
            if level == "none":
                is_completed = False
                break
        
        if not is_completed:
            current_stage = stage
            break

    # Calculate stage progress
    current_stage_skills = goal_roadmap.get(current_stage, [])
    learned_count = sum(1 for s in current_stage_skills 
                        if user_skills_lower.get(s.lower(), "none") != "none")
    
    total_count = len(current_stage_skills)
    progress_pct = int((learned_count / total_count * 100)) if total_count > 0 else 0

    return {
        "current_stage": current_stage,
        "progress_pct": progress_pct,
        "stage_skills": current_stage_skills,
        "all_stages": stages
    }

def is_stage_just_completed(goal: str, user_skills: dict, upgraded_skill: str) -> bool:
    """
    Checks if the upgrade of upgraded_skill just finished a stage.
    """
    roadmaps = load_roadmap()
    goal_roadmap = roadmaps.get(goal, {})
    user_skills_lower = {k.lower(): v.lower() for k, v in user_skills.items()}

    for stage, skills in goal_roadmap.items():
        if upgraded_skill.lower() in [s.lower() for s in skills]:
            # This skill belongs to this stage. Check if all other skills in this stage are done.
            is_completed = True
            for s in skills:
                if user_skills_lower.get(s.lower(), "none") == "none":
                    is_completed = False
                    break
            
            # If it's completed now, we should check if it was COMPLETED by this upgrade
            # But the logic is: if it's completed now, and it's the current stage of interest.
            return is_completed
            
    return False
