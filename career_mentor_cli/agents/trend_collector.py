"""
agents/trend_collector.py
--------------------------
Collects current industry tech trends from GitHub Trending (public page)
and stores them in data/trends.json.

Cache: refreshed every 24 hours.
Fallback: a curated static list when network is unavailable.
"""

import json
import os
import re
from datetime import datetime, timezone

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
TRENDS_FILE = os.path.join(DATA_DIR, "trends.json")

CACHE_TTL_HOURS = 24

# ---------------------------------------------------------------------------
# Default / fallback trend list
# ---------------------------------------------------------------------------
DEFAULT_TRENDS = [
    "RAG Systems",
    "Vector Databases",
    "AI Agents",
    "LLM Fine Tuning",
    "MLOps",
    "Multimodal AI",
    "AI Safety and Alignment",
    "Agentic Workflows",
    "Real-time AI Inference",
    "LLM Evaluation",
    "Model Quantisation",
    "AI Application Development",
]

# ---------------------------------------------------------------------------
# Keyword → canonical trend name mapping
# Checked against repo names, descriptions, and topics from GitHub Trending.
# ---------------------------------------------------------------------------
TREND_KEYWORD_MAP = [
    (["rag", "retrieval-augmented", "retrieval_augmented"],      "RAG Systems"),
    (["vector", "embedding", "faiss", "pinecone", "chroma",
      "weaviate", "qdrant", "milvus"],                           "Vector Databases"),
    (["agent", "agentic", "multi-agent", "langgraph",
      "autogen", "crewai"],                                      "AI Agents"),
    (["fine-tun", "finetune", "finetuning", "lora", "qlora",
      "peft", "sft"],                                            "LLM Fine Tuning"),
    (["mlops", "mlflow", "kubeflow", "feast", "bentoml",
      "seldon", "drift"],                                        "MLOps"),
    (["multimodal", "vision-language", "vlm", "clip",
      "llava", "cogvlm"],                                        "Multimodal AI"),
    (["alignment", "rlhf", "dpo", "safety", "red-team"],        "AI Safety and Alignment"),
    (["workflow", "orchestrat", "pipeline", "langchain",
      "llamaindex"],                                             "Agentic Workflows"),
    (["inference", "serving", "triton", "vllm", "tgi",
      "tensorrt", "onnx"],                                       "Real-time AI Inference"),
    (["evaluation", "benchmark", "evals", "lm-eval",
      "ragas"],                                                  "LLM Evaluation"),
    (["quantiz", "gguf", "llama.cpp", "ollama", "exllama"],     "Model Quantisation"),
    (["llm", "gpt", "gemini", "claude", "mistral",
      "phi", "qwen"],                                            "LLM Systems"),
    (["deep-learning", "neural", "pytorch", "tensorflow"],       "Deep Learning"),
    (["fastapi", "docker", "kubernetes", "deploy"],              "Model Deployment"),
    (["data", "pandas", "spark", "airflow", "etl",
      "dbt"],                                                    "Data Engineering"),
]


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _load_trends_file() -> dict:
    if not os.path.exists(TRENDS_FILE):
        return {}
    try:
        with open(TRENDS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_trends(skills: list) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    data = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "trending_skills": skills,
    }
    with open(TRENDS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _cache_is_fresh(data: dict) -> bool:
    """Returns True if trends were last updated within the last 24 hours."""
    last_updated_str = data.get("last_updated", "")
    if not last_updated_str:
        return False
    try:
        last_updated = datetime.strptime(last_updated_str, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
        delta = datetime.now(timezone.utc) - last_updated
        return delta.total_seconds() < CACHE_TTL_HOURS * 3600
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# GitHub Trending scraper
# ---------------------------------------------------------------------------

def _fetch_github_trending_text() -> str:
    """
    Fetches the raw HTML text from https://github.com/trending.
    Returns empty string on any failure.
    """
    if not _REQUESTS_AVAILABLE:
        return ""

    url = "https://github.com/trending"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.ConnectionError:
        print("   [TrendCollector] No internet connection.")
    except requests.exceptions.Timeout:
        print("   [TrendCollector] GitHub Trending request timed out.")
    except requests.exceptions.HTTPError as e:
        print(f"   [TrendCollector] HTTP error: {e}")
    except Exception as e:
        print(f"   [TrendCollector] Unexpected error: {e}")
    return ""


def _extract_repo_text(html: str) -> list[str]:
    """
    Pulls repository names and descriptions out of GitHub Trending HTML
    using simple regex (no BeautifulSoup dependency required).

    Returns a list of lowercased text snippets.
    """
    snippets = []

    # Repo names appear as: href="/owner/repo-name"
    repo_names = re.findall(r'href="/[\w.-]+/([\w.-]+)"', html)
    snippets.extend(name.lower().replace("-", " ").replace("_", " ")
                    for name in repo_names[:60])

    # Description spans (heuristic — GitHub uses <p> tags with class containing "color")
    descriptions = re.findall(
        r'<p[^>]*class="[^"]*color[^"]*"[^>]*>\s*([^<]{10,200})\s*</p>', html
    )
    snippets.extend(desc.lower() for desc in descriptions[:40])

    return snippets


def _match_trends(snippets: list[str]) -> list[str]:
    """
    Scores keyword matches across all snippets and returns a de-duplicated,
    ordered list of matching canonical trend names.
    """
    from collections import Counter
    counts: Counter = Counter()

    combined = " ".join(snippets)
    for keywords, trend_name in TREND_KEYWORD_MAP:
        for kw in keywords:
            if kw in combined:
                counts[trend_name] += combined.count(kw)

    # Return trends sorted by frequency (most-mentioned first), then apply defaults
    ranked = [trend for trend, _ in counts.most_common()]

    # Ensure the default list fills any gaps so we always have ≥ 8 trends
    for default in DEFAULT_TRENDS:
        if default not in ranked:
            ranked.append(default)

    return ranked[:15]  # cap at 15 trends


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def collect_trends() -> list[str]:
    """
    Returns a list of trending skill names.

    Flow:
    1. Check trends.json — if fresh (< 24 h), return cached list.
    2. Attempt to scrape GitHub Trending.
    3. On success → extract keywords, update trends.json, return list.
    4. On failure → use existing trends.json or DEFAULT_TRENDS.
    """
    cached = _load_trends_file()

    if _cache_is_fresh(cached) and cached.get("trending_skills"):
        print("   📊  Using cached industry trends (< 24 hours old).")
        return cached["trending_skills"]

    print("   🌐  Fetching industry trends from GitHub Trending...")
    html = _fetch_github_trending_text()

    if html:
        snippets = _extract_repo_text(html)
        trends   = _match_trends(snippets)
        _save_trends(trends)
        print(f"   ✅  {len(trends)} trends collected and saved.")
        return trends

    # Fallback: use stale cache or defaults
    if cached.get("trending_skills"):
        print("   ⚠️   Using stale cached trends (fetch failed).")
        return cached["trending_skills"]

    print("   ⚠️   Using built-in default trend list.")
    _save_trends(DEFAULT_TRENDS)
    return DEFAULT_TRENDS


def run_trend_update() -> list[str]:
    """
    Entry point called from main.py.
    Returns the current trending skill list.
    Prints a summary line on success.
    Never raises.
    """
    try:
        trends = collect_trends()
        print(f"\n✅  Industry trends updated successfully. "
              f"({len(trends)} trending topics loaded)\n")
        return trends
    except Exception as e:
        print(f"   [Warning] Trend collection failed unexpectedly: {e}. "
              f"Using defaults.")
        return DEFAULT_TRENDS


def load_trends() -> list[str]:
    """
    Fast loader (no network call).  Reads trends.json directly.
    Returns DEFAULT_TRENDS if the file is missing or invalid.
    Used internally by task generation helpers.
    """
    data = _load_trends_file()
    return data.get("trending_skills", DEFAULT_TRENDS)
