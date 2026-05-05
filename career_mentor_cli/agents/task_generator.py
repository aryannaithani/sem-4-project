"""
task_generator.py
------------------
Agent responsible for generating personalised learning tasks
using the Gemini LLM API.

Input  : skill gaps, industry context trends, existing user projects,
         skill levels, completed tasks, current stage, confidence data
Output : structured task dicts or raw roadmap text

Provides two modes:
  generate_tasks()            -> str   (legacy, raw text)
  generate_tasks_structured() -> list  (new, used by task_store pipeline)
"""

import os
import google.generativeai as genai

# ---------------------------------------------------------------------------
# 🔑  Replace this with your actual Gemini API key, or set the environment
#     variable GEMINI_API_KEY before running the program.
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_KEY_HERE")

# Gemini model to use — gemini-2.5-flash is fast and free-tier friendly
GEMINI_MODEL = "gemini-2.5-flash"

# Difficulty progression mapping: current level → task difficulty to generate
_DIFFICULTY_PROGRESSION = {
    "none":         "beginner",
    "beginner":     "intermediate",
    "intermediate": "advanced",
    "advanced":     None,   # skill is mastered — skip as a priority
}


def _target_difficulty(skill: str, skill_levels: dict, confidence_data: dict) -> str:
    """
    Returns the difficulty level tasks should target for a given skill,
    considering the user's current level and optional confidence score.

    Rules:
    - none         → beginner
    - beginner     → intermediate  (lower if confidence ≤ 2)
    - intermediate → advanced      (lower if confidence ≤ 2)
    - advanced     → None (skip)

    Confidence overrides:
    - confidence 1-2 = low confidence → drop one level (reinforce)
    - confidence 4-5 = high confidence → keep progression as-is (already correct)
    """
    level = skill_levels.get(skill, "none").lower()
    base  = _DIFFICULTY_PROGRESSION.get(level, "beginner")

    if base is None:
        return None   # advanced → nothing to generate

    # Confidence adjustment
    confidence = confidence_data.get(skill)
    if confidence is not None:
        try:
            conf_int = int(confidence)
            if conf_int <= 2 and base == "intermediate":
                base = "beginner"    # reinforce
            elif conf_int <= 2 and base == "advanced":
                base = "intermediate"  # reinforce
        except (ValueError, TypeError):
            pass

    return base


def _build_prompt(
    skill_gaps: list[str],
    context: list[str],
    projects: list[str],
    user_name: str,
    goal: str,
    skill_levels: dict | None = None,
    completed_tasks: list[str] | None = None,
    current_stage: str = "",
    confidence_data: dict | None = None,
) -> str:
    """
    Constructs the LLM prompt from the gathered data.

    Args:
        skill_gaps      : Skills the user needs to learn.
        context         : Current industry trends (hot technologies).
        projects        : Projects the user has already built.
        user_name       : User's name for personalisation.
        goal            : The user's career goal.
        skill_levels    : Dict of {skill: level} for all user skills.
        completed_tasks : List of completed task description strings.
        current_stage   : Name of the user's current roadmap stage.
        confidence_data : Dict of {skill: confidence_score (1-5)}.

    Returns:
        str: A fully formed prompt string.
    """
    skill_levels    = skill_levels    or {}
    completed_tasks = completed_tasks or []
    confidence_data = confidence_data or {}

    gaps_str     = "\n".join(f"- {g}" for g in skill_gaps)
    context_str  = "\n".join(f"- {c}" for c in context)
    projects_str = "\n".join(f"- {p}" for p in projects) if projects else "None yet"

    # Per-skill difficulty targets
    difficulty_lines = []
    for skill in skill_gaps:
        diff = _target_difficulty(skill, skill_levels, confidence_data)
        if diff:
            conf = confidence_data.get(skill)
            conf_note = f" (confidence score: {conf}/5)" if conf is not None else ""
            difficulty_lines.append(f"- {skill}: generate {diff.upper()} level tasks{conf_note}")
        else:
            difficulty_lines.append(f"- {skill}: MASTERED — if included, generate advanced/specialist tasks only")
    difficulty_str = "\n".join(difficulty_lines) if difficulty_lines else "No specific targets."

    # Completed tasks context
    if completed_tasks:
        completed_str = "\n".join(f"- {t}" for t in completed_tasks)
    else:
        completed_str = "None yet — this is the user's starting point."

    prompt = f"""
You are an expert AI Career Mentor. Your task is to generate a highly personalised, context-aware set of learning tasks for a student.

=== STUDENT PROFILE ===
Name         : {user_name}
Career Goal  : {goal}
Current Stage: {current_stage or "Not determined"}

=== CURRENT SKILL LEVELS ===
{chr(10).join(f"- {k}: {v}" for k, v in skill_levels.items()) if skill_levels else "No skills data available."}

=== SKILL GAPS TO ADDRESS ===
{gaps_str}

=== TARGET DIFFICULTY PER SKILL ===
{difficulty_str}

=== ALREADY COMPLETED TASKS (do NOT repeat these) ===
{completed_str}

=== INDUSTRY CONTEXT & TRENDS ===
{context_str}

=== PROJECTS ALREADY BUILT ===
{projects_str}

=== TASK GENERATION RULES (FOLLOW STRICTLY) ===
1. Keep the "Task" and "Reason" fields EXTREMELY short and concise. Long text breaks the frontend UI.
2. EVERY task must include a concrete hands-on project or deliverable.
3. Tasks must logically follow and build upon the completed tasks listed above. Do NOT restart from basics if the user has already covered foundational work.
4. Tasks must match the target difficulty level for each skill (see TARGET DIFFICULTY PER SKILL above).
5. If the user has completed beginner-level tasks for a skill, generate INTERMEDIATE or ADVANCED tasks — never beginner again.
6. DO NOT repeat or closely paraphrase any task already in the COMPLETED TASKS list.
7. Tasks must be realistic and completable by a student, but should be challenging enough to advance their skill.
8. Follow a clear progression: each task should prepare the student for the next stage of their career goal.

Generate exactly {len(skill_gaps)} tasks, one per skill gap listed above.

Use this EXACT format for every task (no extra prose before or after):

Task: <Short title (max 5 words): Very short description (max 10 words)>
Skill: <skill name from the skill gaps list>
Difficulty: <beginner | intermediate | advanced>
Reason: <Short 1-sentence reason (max 10 words)>

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
    Calls the Gemini API to generate a personalised task roadmap (legacy raw-text mode).

    Returns:
        str: Raw text of the generated roadmap from Gemini.
    """
    if GEMINI_API_KEY == "YOUR_KEY_HERE":
        return _fallback_tasks(skill_gaps)

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


def generate_tasks_structured(
    skill_gaps: list[str],
    context: list[str],
    projects: list[str],
    user_name: str = "User",
    goal: str = "AI/ML Engineer",
    skill_levels: dict | None = None,
    completed_tasks: list[str] | None = None,
    current_stage: str = "",
    confidence_data: dict | None = None,
) -> list[dict]:
    """
    Generates tasks and returns them as a list of dicts:
        {"skill": ..., "task": ..., "difficulty": ..., "reason": ..., "status": "pending"}

    Calls the Gemini API when available; falls back to static suggestions otherwise.
    The 'id' key is intentionally absent — task_store.add_tasks() assigns ids.
    """
    skill_levels    = skill_levels    or {}
    completed_tasks = completed_tasks or []
    confidence_data = confidence_data or {}

    if GEMINI_API_KEY == "YOUR_KEY_HERE":
        return _fallback_tasks_structured(skill_gaps, skill_levels, confidence_data)

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    prompt = _build_prompt(
        skill_gaps=skill_gaps,
        context=context,
        projects=projects,
        user_name=user_name,
        goal=goal,
        skill_levels=skill_levels,
        completed_tasks=completed_tasks,
        current_stage=current_stage,
        confidence_data=confidence_data,
    )

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        return _parse_tasks(raw_text, skill_gaps, skill_levels, confidence_data)
    except Exception as e:
        print(f"\n[TaskGenerator] ⚠️  Gemini API call failed: {e}")
        print("[TaskGenerator] Falling back to static task suggestions.\n")
        return _fallback_tasks_structured(skill_gaps, skill_levels, confidence_data)


def _parse_tasks(
    raw_text: str,
    skill_gaps: list[str],
    skill_levels: dict | None = None,
    confidence_data: dict | None = None,
) -> list[dict]:
    """
    Parses the LLM text output (Task / Skill / Difficulty / Reason blocks)
    into a list of task dicts.

    Falls back to static suggestions for any block that cannot be parsed.
    """
    skill_levels    = skill_levels    or {}
    confidence_data = confidence_data or {}

    tasks = []
    # Split on blank-line-separated blocks
    blocks = [b.strip() for b in raw_text.split("\n\n") if b.strip()]

    for block in blocks:
        lines = block.splitlines()
        task_dict: dict = {"status": "pending"}

        for line in lines:
            line_lower = line.lower().strip()
            if line_lower.startswith("task:") or (line_lower.startswith("task ") and ":" in line_lower):
                task_dict["task"] = line.split(":", 1)[-1].strip()
            elif line_lower.startswith("skill:"):
                task_dict["skill"] = line.split(":", 1)[-1].strip()
            elif line_lower.startswith("difficulty:"):
                task_dict["difficulty"] = line.split(":", 1)[-1].strip().lower()
            elif line_lower.startswith("reason:"):
                task_dict["reason"] = line.split(":", 1)[-1].strip()

        if "task" in task_dict and "skill" in task_dict:
            # Ensure difficulty field is present and consistent with progression rules
            if "difficulty" not in task_dict:
                skill = task_dict.get("skill", "")
                task_dict["difficulty"] = _target_difficulty(skill, skill_levels, confidence_data) or "intermediate"
            tasks.append(task_dict)

    if not tasks:
        return _fallback_tasks_structured(skill_gaps, skill_levels, confidence_data)

    return tasks


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
            "Run a full EDA + hypothesis testing on the Titanic dataset and write a report",
            "Statistical thinking is the backbone of every ML algorithm.",
        ),
        "deep learning": (
            "Deep Learning",
            "Build and train a CNN image classifier from scratch using PyTorch on CIFAR-10",
            "Deep learning powers the most advanced AI systems today.",
        ),
        "data engineering": (
            "Data Engineering",
            "Build an end-to-end ETL pipeline using Apache Airflow that ingests and cleans stock data",
            "Clean, reliable data pipelines are essential for production ML.",
        ),
        "model deployment": (
            "Model Deployment",
            "Containerise a trained ML model with Docker and deploy it behind a FastAPI REST endpoint",
            "Deployment skills bridge the gap between a model and real-world impact.",
        ),
        "llm systems": (
            "LLM Systems",
            "Build a multi-turn RAG chatbot over private PDFs using LangChain + FAISS with streaming output",
            "LLM orchestration is the hottest skill in the current AI job market.",
        ),
        "vector databases": (
            "Vector Databases",
            "Build a semantic similarity search engine for arXiv abstracts using ChromaDB and sentence-transformers",
            "Vector databases are the storage layer of modern AI applications.",
        ),
        "mlops": (
            "MLOps",
            "Set up a full MLOps pipeline with MLflow experiment tracking and GitHub Actions CI/CD for model retraining",
            "MLOps practices ensure models stay reliable and maintainable in production.",
        ),
        "pytorch": (
            "PyTorch",
            "Implement a Transformer (multi-head attention + positional encoding) from scratch and train it on a toy sequence task",
            "PyTorch is the dominant framework in AI research and industry.",
        ),
        "transformers": (
            "Transformers",
            "Fine-tune DistilBERT for a domain-specific NER task using Hugging Face Trainer API",
            "Transformer architecture underpins virtually every modern LLM.",
        ),
        "feature engineering": (
            "Feature Engineering",
            "Engineer a feature set for a Kaggle tabular competition, beating a vanilla baseline by ≥5% AUC",
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
            project = f"Build a focused project demonstrating real-world use of {gap}"
            reason  = f"Hands-on experience with {gap} is essential for your career goal."

        lines.append(
            f"Task {count}\n"
            f"Task      : {project}\n"
            f"Skill     : {skill}\n"
            f"Difficulty: beginner\n"
            f"Reason    : {reason}\n"
        )
        count += 1
        if count > 5:
            break

    return "\n".join(lines)


def _fallback_tasks_structured(
    skill_gaps: list[str],
    skill_levels: dict | None = None,
    confidence_data: dict | None = None,
) -> list[dict]:
    """
    Structured fallback — returns a list of task dicts respecting difficulty progression.
    Each dict: { skill, task, difficulty, reason, status }
    """
    skill_levels    = skill_levels    or {}
    confidence_data = confidence_data or {}

    # Static suggestions keyed by difficulty → more specific tasks for higher levels
    static_by_difficulty: dict[str, dict[str, tuple]] = {
        "beginner": {
            "statistics": (
                "Statistics & Probability",
                "Analyse the Titanic dataset: compute summary statistics, visualise distributions, and run a χ² test",
                "Statistical foundations are essential before tackling any ML algorithm.",
            ),
            "deep learning": (
                "Deep Learning",
                "Build a simple MLP in PyTorch to classify MNIST digits with ≥98% accuracy",
                "Understanding basic neural network math is the entry point for deep learning.",
            ),
            "data engineering": (
                "Data Engineering",
                "Write a Python script that fetches, cleans, and stores CSV stock data using Pandas",
                "Data loading and cleaning are the first steps of any data pipeline.",
            ),
            "model deployment": (
                "Model Deployment",
                "Wrap a trained scikit-learn model in a Flask API and serve predictions locally",
                "Serving a model exposes you to the deployment workflow for the first time.",
            ),
            "llm systems": (
                "LLM Systems",
                "Use the OpenAI/Gemini API to build a simple Q&A chatbot with conversation history",
                "Direct API usage is the starting point for building LLM-powered apps.",
            ),
            "vector databases": (
                "Vector Databases",
                "Store and query sentence embeddings using ChromaDB for a small document corpus",
                "Understanding vector storage is foundational for semantic search.",
            ),
            "mlops": (
                "MLOps",
                "Track experiments for a RandomForest model using MLflow locally",
                "Experiment tracking is the first MLOps skill every practitioner needs.",
            ),
            "pytorch": (
                "PyTorch",
                "Implement linear regression and logistic regression from scratch using PyTorch tensors",
                "Building basics in PyTorch builds intuition for the autograd system.",
            ),
            "transformers": (
                "Transformers",
                "Run inference with a pre-trained HuggingFace BERT model on a sentiment classification task",
                "Using a pre-trained model is the first step to understanding transformers.",
            ),
            "feature engineering": (
                "Feature Engineering",
                "Create interaction features and handle missing values on the Titanic dataset using Pandas",
                "Feature engineering fundamentals apply across all tabular ML problems.",
            ),
        },
        "intermediate": {
            "statistics": (
                "Statistics & Probability",
                "Implement Bayesian A/B testing from scratch: compute posterior distributions and decide a winner",
                "Bayesian reasoning is the bridge from descriptive statistics to probabilistic ML models.",
            ),
            "deep learning": (
                "Deep Learning",
                "Train a ResNet-based CNN on CIFAR-10, apply data augmentation, and log results with TensorBoard",
                "Convolutional architectures and training best practices are core intermediate skills.",
            ),
            "data engineering": (
                "Data Engineering",
                "Build a scheduled Airflow DAG that ingests, validates, and loads data into a SQLite warehouse",
                "Orchestration and scheduling are what differentiate scripts from real pipelines.",
            ),
            "model deployment": (
                "Model Deployment",
                "Containerise a FastAPI ML service with Docker and add a /health and /predict endpoint with input validation",
                "Containerisation is the standard production deployment pattern.",
            ),
            "llm systems": (
                "LLM Systems",
                "Build a RAG pipeline that answers questions over your own PDF documents using LangChain + FAISS",
                "RAG is the dominant production pattern for grounding LLMs in private knowledge.",
            ),
            "vector databases": (
                "Vector Databases",
                "Build a semantic search engine for arXiv abstracts using ChromaDB and sentence-transformers",
                "Semantic search is the primary use-case that drives vector database adoption.",
            ),
            "mlops": (
                "MLOps",
                "Set up a GitHub Actions CI pipeline that retrains a model, evaluates it, and fails if accuracy drops",
                "CI for ML ensures that every code change is validated against model quality.",
            ),
            "pytorch": (
                "PyTorch",
                "Implement multi-head self-attention from scratch and verify it produces the same output as nn.MultiheadAttention",
                "Understanding self-attention at the code level is the key to mastering Transformers.",
            ),
            "transformers": (
                "Transformers",
                "Fine-tune DistilBERT for a domain-specific text classification task using HuggingFace Trainer API",
                "Fine-tuning transfers pre-trained knowledge to your specific problem cheaply.",
            ),
            "feature engineering": (
                "Feature Engineering",
                "Build a feature engineering pipeline with target encoding and polynomial features for a Kaggle tabular competition",
                "Advanced feature creation separates winning solutions from baselines.",
            ),
        },
        "advanced": {
            "statistics": (
                "Statistics & Probability",
                "Implement and benchmark a custom MCMC sampler (Metropolis-Hastings) for a Bayesian regression model",
                "Sampling-based inference is essential for advanced probabilistic modelling.",
            ),
            "deep learning": (
                "Deep Learning",
                "Implement a Vision Transformer (ViT) from scratch and evaluate it on CIFAR-100 vs a ResNet baseline",
                "Cutting-edge architectures drive the state-of-the-art in computer vision.",
            ),
            "data engineering": (
                "Data Engineering",
                "Build a streaming data pipeline with Kafka + Flink that processes and aggregates real-time events",
                "Streaming pipelines are the infrastructure backbone of real-time ML systems.",
            ),
            "model deployment": (
                "Model Deployment",
                "Deploy a model to Kubernetes with autoscaling, implement A/B traffic splitting, and add Prometheus monitoring",
                "Kubernetes-level deployment is required for production-grade ML infrastructure.",
            ),
            "llm systems": (
                "LLM Systems",
                "Build an agentic LLM system with tool use (web search + code interpreter) using LangGraph",
                "Agent frameworks are the frontier of LLM application development.",
            ),
            "vector databases": (
                "Vector Databases",
                "Build a multi-modal retrieval system combining text and image embeddings using Pinecone",
                "Multi-modal retrieval is the next frontier in production AI search.",
            ),
            "mlops": (
                "MLOps",
                "Implement a full ML platform with feature store (Feast), model registry (MLflow), and drift detection",
                "A complete ML platform represents the gold standard for production AI systems.",
            ),
            "pytorch": (
                "PyTorch",
                "Profile and optimise a Transformer training loop: implement gradient checkpointing, mixed precision, and torch.compile",
                "Training efficiency is critical for working with large-scale models.",
            ),
            "transformers": (
                "Transformers",
                "Implement LoRA fine-tuning on a 7B parameter LLM and evaluate on a domain-specific benchmark",
                "Parameter-efficient fine-tuning (PEFT) is the production standard for customising LLMs.",
            ),
            "feature engineering": (
                "Feature Engineering",
                "Build an automated feature selection pipeline using SHAP values and recursive feature elimination",
                "Automated feature selection scales engineering intuition to large feature spaces.",
            ),
        },
    }

    tasks = []
    for gap in skill_gaps[:5]:   # cap at 5 tasks
        key  = gap.lower()
        diff = _target_difficulty(gap, skill_levels, confidence_data) or "beginner"

        suggestions = static_by_difficulty.get(diff, static_by_difficulty["beginner"])
        if key in suggestions:
            skill, task_text, reason = suggestions[key]
        else:
            skill     = gap
            task_text = f"Build a real-world {diff}-level project that demonstrates practical mastery of {gap}"
            reason    = f"Hands-on practice at the {diff} level advances your journey towards {gap} mastery."

        tasks.append({
            "skill":      skill,
            "task":       task_text,
            "difficulty": diff,
            "reason":     reason,
            "status":     "pending",
        })

    return tasks
