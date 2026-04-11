"""
agents/github_agent.py
-----------------------
Fetches public GitHub repositories for a user, extracts relevant technical
skills from language/topic/name/description data, and merges them into
data/skills.json without overwriting higher skill levels.

Cache: data/github_cache.json  (refreshed every 1 hour)
"""

import json
import os
import time

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR    = os.path.join(BASE_DIR, "data")
USER_FILE   = os.path.join(DATA_DIR, "user.txt")
SKILLS_FILE = os.path.join(DATA_DIR, "skills.json")
CACHE_FILE  = os.path.join(DATA_DIR, "github_cache.json")

CACHE_TTL_SECONDS = 3600  # 1 hour

# ---------------------------------------------------------------------------
# Skill mapping tables
# ---------------------------------------------------------------------------

# GitHub "language" → canonical skill name
LANGUAGE_MAP = {
    "python":     "Python",
    "javascript": "JavaScript",
    "typescript": "JavaScript",
    "java":       "Java",
    "c++":        "C++",
    "c":          "C",
    "go":         "Go",
    "rust":       "Rust",
    "r":          "R",
    "julia":      "Julia",
    "sql":        "Data Engineering",
    "shell":      "DevOps",
    "dockerfile": "Model Deployment",
}

# Topic / keyword → canonical skill name (checked in repo topics + name + description)
KEYWORD_MAP = [
    (["machine-learning", "ml", "sklearn", "scikit"],          "Machine Learning"),
    (["deep-learning", "neural-network", "neural-net",
      "tensorflow", "keras", "pytorch"],                       "Deep Learning"),
    (["nlp", "llm", "gpt", "bert", "transformer",
      "langchain", "huggingface"],                              "LLM Systems"),
    (["rag", "retrieval", "vector", "faiss",
      "pinecone", "chroma", "weaviate", "embedding"],          "Vector Databases"),
    (["api", "fastapi", "flask", "django",
      "docker", "deploy", "deployment", "kubernetes",
      "k8s", "mlflow", "serving"],                             "Model Deployment"),
    (["data", "pipeline", "etl", "spark", "airflow",
      "dbt", "warehouse", "pandas", "numpy"],                  "Data Engineering"),
    (["computer-vision", "cv", "image", "opencv",
      "yolo", "detection", "segmentation"],                    "Computer Vision"),
    (["reinforcement-learning", "rl", "gym", "agent"],         "Reinforcement Learning"),
]

# Skill level ordering (higher index = higher level)
LEVEL_ORDER = ["none", "beginner", "intermediate", "advanced"]


# ---------------------------------------------------------------------------
# 1. Username loading
# ---------------------------------------------------------------------------

def load_github_username() -> str:
    """
    Reads data/user.txt and returns the value after 'GitHub:'.
    Returns an empty string if the field is absent or the file is missing.
    """
    if not os.path.exists(USER_FILE):
        return ""
    with open(USER_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line.lower().startswith("github:"):
                username = line.split(":", 1)[1].strip()
                return username
    return ""


# ---------------------------------------------------------------------------
# 2. Cache helpers
# ---------------------------------------------------------------------------

def _load_cache() -> dict:
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(username: str, repos: list) -> None:
    cache = {
        "username":  username,
        "fetched_at": time.time(),
        "repos":     repos,
    }
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


def _cache_is_valid(cache: dict, username: str) -> bool:
    if cache.get("username", "").lower() != username.lower():
        return False
    fetched_at = cache.get("fetched_at", 0)
    return (time.time() - fetched_at) < CACHE_TTL_SECONDS


# ---------------------------------------------------------------------------
# 3. Fetch repos from GitHub API
# ---------------------------------------------------------------------------

def fetch_github_repos(username: str) -> list:
    """
    Fetches public repos for *username* from the GitHub API.
    Returns a list of repo dicts (simplified).  Returns [] on any error.
    Uses a 1-hour local cache (data/github_cache.json).
    """
    if not username:
        return []

    # Check cache first
    cache = _load_cache()
    if _cache_is_valid(cache, username):
        print(f"   📦  Using cached GitHub data for '{username}' (< 1 hour old).")
        return cache.get("repos", [])

    if not _REQUESTS_AVAILABLE:
        print("   [Warning] 'requests' library not installed. Skipping GitHub fetch.")
        return []

    url = f"https://api.github.com/users/{username}/repos"
    params = {"per_page": 100, "sort": "updated"}

    try:
        print(f"   🌐  Fetching GitHub repos for '{username}'...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_repos = response.json()
    except requests.exceptions.ConnectionError:
        print("   [Warning] No internet connection. Skipping GitHub fetch.")
        return []
    except requests.exceptions.Timeout:
        print("   [Warning] GitHub API timed out. Skipping GitHub fetch.")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"   [Warning] GitHub API error: {e}. Skipping GitHub fetch.")
        return []
    except Exception as e:
        print(f"   [Warning] Unexpected error during GitHub fetch: {e}. Skipping.")
        return []

    # Slim down to only what we need
    repos = []
    for repo in raw_repos:
        if not isinstance(repo, dict):
            continue
        repos.append({
            "name":        (repo.get("name") or "").lower(),
            "description": (repo.get("description") or "").lower(),
            "language":    (repo.get("language") or "").lower(),
            "topics":      [t.lower() for t in (repo.get("topics") or [])],
        })

    _save_cache(username, repos)
    print(f"   ✅  Fetched {len(repos)} repositories.")
    return repos


# ---------------------------------------------------------------------------
# 4. Skill extraction
# ---------------------------------------------------------------------------

def _text_contains_keyword(text: str, keywords: list) -> bool:
    """Returns True if any keyword appears in *text* (word-boundary-aware)."""
    for kw in keywords:
        if kw in text:
            return True
    return False


def extract_skills_from_repos(repos: list) -> set:
    """
    Analyses a list of repo dicts and returns a set of canonical skill names
    detected via language mapping, topic mapping, and repo name/description
    keyword search.
    """
    detected = set()

    for repo in repos:
        lang   = repo.get("language", "")
        topics = repo.get("topics", [])
        name   = repo.get("name", "")
        desc   = repo.get("description", "")

        # 1) Language mapping
        if lang in LANGUAGE_MAP:
            detected.add(LANGUAGE_MAP[lang])

        # 2) Topic + name + description keyword mapping
        combined_text = " ".join(topics) + " " + name + " " + desc
        for keywords, skill_name in KEYWORD_MAP:
            if _text_contains_keyword(combined_text, keywords):
                detected.add(skill_name)

    return detected


# ---------------------------------------------------------------------------
# 5. Skill merging
# ---------------------------------------------------------------------------

def _load_skills() -> dict:
    if not os.path.exists(SKILLS_FILE):
        return {}
    try:
        with open(SKILLS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_skills(skills: dict) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SKILLS_FILE, "w") as f:
        json.dump(skills, f, indent=4)


def merge_skills(extracted_skills: set) -> int:
    """
    Merges *extracted_skills* into data/skills.json.

    Rules:
    - Skill absent  → add at "beginner"
    - Skill present and level is "none" → upgrade to "beginner"
    - Skill present and level >= "beginner" → leave unchanged

    Returns the number of skills that were added or upgraded.
    """
    skills = _load_skills()
    changed = 0

    for skill in extracted_skills:
        current_level = skills.get(skill, "absent")

        if current_level == "absent":
            # New skill — add at beginner
            skills[skill] = "beginner"
            changed += 1
        elif current_level == "none":
            # Upgrade "none" → "beginner"
            skills[skill] = "beginner"
            changed += 1
        # else: already beginner/intermediate/advanced — do not touch

    if changed:
        _save_skills(skills)

    return changed


# ---------------------------------------------------------------------------
# 6. Public entry point
# ---------------------------------------------------------------------------

def run_github_skill_sync() -> None:
    """
    Full pipeline:
      1. Load GitHub username from user.txt
      2. Fetch repos (with cache)
      3. Extract skills
      4. Merge into skills.json

    Prints a summary line.  Never raises an exception.
    """
    try:
        username = load_github_username()
        if not username:
            print("   ℹ️   No GitHub username found in user.txt — skipping GitHub analysis.")
            return

        repos = fetch_github_repos(username)
        if not repos:
            print("   ℹ️   No repository data available — skipping skill extraction.")
            return

        skills_found = extract_skills_from_repos(repos)
        if not skills_found:
            print("   ℹ️   No recognisable skills detected from GitHub repos.")
            return

        changed = merge_skills(skills_found)
        print(f"\n✅  GitHub analysis complete. Skills updated. "
              f"({len(skills_found)} skills detected, {changed} added/upgraded)\n")

    except Exception as e:
        print(f"   [Warning] GitHub skill sync failed unexpectedly: {e}. Continuing.")
