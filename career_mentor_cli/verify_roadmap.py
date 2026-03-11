
import os
import sys

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from agents.roadmap_agent import get_stage_info

def test_stage_detection():
    print("Testing Stage Detection...")
    
    # Mock skills
    skills_1 = {
        "Python": "advanced",
        "Statistics": "beginner",
        "Machine Learning": "beginner"
    }
    
    # Should be in Foundations because some skills are beginner but none are 'none' 
    # WAIT, the rule is: "If a stage contains skills that are still at level 'none', the user is currently in that stage."
    # If all skills in Foundations are at least 'beginner', it should move to Intermediate.
    
    info_1 = get_stage_info("AI/ML Engineer", skills_1)
    print(f"Skills: {skills_1}")
    print(f"Current Stage: {info_1['current_stage']} (Expected: Intermediate)")
    
    skills_2 = {
        "Python": "advanced",
        "Statistics": "none",
        "Machine Learning": "beginner"
    }
    info_2 = get_stage_info("AI/ML Engineer", skills_2)
    print(f"Skills: {skills_2}")
    print(f"Current Stage: {info_2['current_stage']} (Expected: Foundations)")
    print(f"Stage Progress: {info_2['progress_pct']}% (Expected: 66%)")

    skills_3 = {
        "Python": "advanced",
        "Statistics": "beginner",
        "Machine Learning": "beginner",
        "Deep Learning": "beginner",
        "Data Engineering": "beginner",
        "Vector Databases": "none"
    }
    info_3 = get_stage_info("AI/ML Engineer", skills_3)
    print(f"Skills: {skills_3}")
    print(f"Current Stage: {info_3['current_stage']} (Expected: Advanced)")
    
    print("\nVerification Complete.")

if __name__ == "__main__":
    test_stage_detection()
