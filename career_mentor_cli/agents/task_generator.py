"""
task_generator.py
------------------
Agent responsible for generating personalised learning tasks
using the Gemini LLM API.

Input  : skill gaps, industry context trends, existing user projects
Output : a structured roadmap of tasks with project ideas and rationale

This is the "Recommendation Engine" of the Career Mentor pipeline.
"""

import os
import google.generativeai as genai

# ---------------------------------------------------------------------------
# 🔑  Replace this with your actual Gemini API key, or set the environment
#     variable GEMINI_API_KEY before running the program.
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_KEY_HERE")

# Gemini model to use — gemini-1.5-flash is fast and free-tier friendly
GEMINI_MODEL = "gemini-2.5-flash"


def _build_prompt(
    skill_gaps: list[str],
    context: list[str],
    projects: list[str],
    user_name: str,
    goal: str,
) -> str:
    """
    Constructs the LLM prompt from the gathered data.

    Args:
        skill_gaps : Skills the user needs to learn.
        context    : Current industry trends (hot technologies).
        projects   : Projects the user has already built.
        user_name  : User's name for personalisation.
        goal       : The user's career goal.

    Returns:
        str: A fully formed prompt string.
    """
    gaps_str     = "\n".join(f"- {g}" for g in skill_gaps)
    context_str  = "\n".join(f"- {c}" for c in context)
    projects_str = "\n".join(f"- {p}" for p in projects)

    prompt = f"""
You are an expert AI Career Mentor. Your job is to generate a personalised, actionable learning roadmap.

Student Name : {user_name}
Career Goal  : {goal}

Skill Gaps (skills the student needs to learn):
{gaps_str}

Industry Trends (current hot topics in the field):
{context_str}

Existing Projects (already built by the student):
{projects_str}

Generate exactly 5 personalised learning tasks. For each task provide:
1. Skill to Learn
2. Hands-on Project Idea (different from existing projects, relevant to industry trends)
3. Why this helps reach the career goal

Use this exact format for every task (no extra prose before or after):

Task <number>
Skill     : <skill name>
Project   : <project idea>
Reason    : <one-sentence explanation>

Be specific, practical, and encouraging.
"""
    return prompt.strip()


def generate_tasks(
    skill_gaps: list[str],
    context: list[str],
    projects: list[str],
    user_name: str = "User",
    goal: str = "AI/ML Engineer",
) -> str:
    """
    Calls the Gemini API to generate a personalised task roadmap.

    Args:
        skill_gaps : Missing skills detected by SkillGapAgent.
        context    : Industry trends from context.txt.
        projects   : User's existing projects from projects.txt.
        user_name  : User's name (from user.txt).
        goal       : User's career goal (from user.txt).

    Returns:
        str: Raw text of the generated roadmap from Gemini.
    """
    if GEMINI_API_KEY == "YOUR_KEY_HERE":
        # Graceful fallback when no API key is configured
        return _fallback_tasks(skill_gaps)

    # Configure the Gemini client
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)

    prompt = _build_prompt(skill_gaps, context, projects, user_name, goal)

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"\n[TaskGenerator] ⚠️  Gemini API call failed: {e}")
        print("[TaskGenerator] Falling back to static task suggestions.\n")
        return _fallback_tasks(skill_gaps)


# ---------------------------------------------------------------------------
# Fallback — used when the API key is missing or the API call fails
# ---------------------------------------------------------------------------

def _fallback_tasks(skill_gaps: list[str]) -> str:
    """
    Returns a static set of task suggestions based on the detected skill gaps.
    Used as a graceful fallback when no Gemini API key is available.
    """
    static_suggestions = {
        "statistics": (
            "Statistics & Probability",
            "Analyse a real-world dataset (e.g. Titanic) and produce a statistical report",
            "Statistical thinking is the backbone of every ML algorithm.",
        ),
        "deep learning": (
            "Deep Learning",
            "Build an image classifier using CNNs with PyTorch/TensorFlow",
            "Deep learning powers the most advanced AI systems today.",
        ),
        "data engineering": (
            "Data Engineering",
            "Build an ETL pipeline that ingests, cleans, and stores stock-market data",
            "Clean, reliable data pipelines are essential for production ML.",
        ),
        "model deployment": (
            "Model Deployment",
            "Deploy a sentiment-analysis model as a REST API using FastAPI + Docker",
            "Deployment skills bridge the gap between a model and real-world impact.",
        ),
        "llm systems": (
            "LLM Systems",
            "Build a RAG-based Q&A bot over your own PDF documents using LangChain",
            "LLM orchestration is the hottest skill in the current AI job market.",
        ),
        "vector databases": (
            "Vector Databases",
            "Build a semantic search engine for research papers using ChromaDB",
            "Vector databases are the storage layer of modern AI applications.",
        ),
        "mlops": (
            "MLOps",
            "Set up a CI/CD pipeline for a ML model using GitHub Actions + MLflow",
            "MLOps practices ensure models stay reliable and maintainable in production.",
        ),
        "pytorch": (
            "PyTorch",
            "Implement a transformer from scratch to understand self-attention",
            "PyTorch is the dominant framework in AI research and industry.",
        ),
        "transformers": (
            "Transformers",
            "Fine-tune a pre-trained BERT model for a custom text classification task",
            "Transformer architecture underpins virtually every modern LLM.",
        ),
        "feature engineering": (
            "Feature Engineering",
            "Explore and engineer features on a Kaggle tabular dataset to beat a baseline",
            "Good features often matter more than model choice in real-world ML.",
        ),
    }

    lines = []
    count = 1
    for gap in skill_gaps:
        key = gap.lower()
        if key in static_suggestions:
            skill, project, reason = static_suggestions[key]
        else:
            skill   = gap
            project = f"Build a small project that uses {gap}"
            reason  = f"Learning {gap} moves you closer to your career goal."

        lines.append(
            f"Task {count}\n"
            f"Skill     : {skill}\n"
            f"Project   : {project}\n"
            f"Reason    : {reason}\n"
        )
        count += 1
        if count > 5:
            break

    return "\n".join(lines)
