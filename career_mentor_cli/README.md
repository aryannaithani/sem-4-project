# 🎯 AI Career Mentor CLI

A minimal CLI prototype that simulates the reasoning engine of an AI career mentor.  
It analyses your skills, detects gaps relative to your career goal, and uses Gemini AI to generate a personalised learning roadmap.

---

## 📁 Project Structure

```
career_mentor_cli/
├── main.py                  # Entry point — runs the full pipeline
├── requirements.txt
├── README.md
├── agents/
│   ├── goal_analyzer.py     # Loads required skills for the career goal
│   ├── skill_gap_agent.py   # Detects missing skills
│   └── task_generator.py    # Calls Gemini API to generate tasks
└── data/
    ├── user.txt             # Your name and career goal
    ├── skills.txt           # Your current skills
    ├── projects.txt         # Your existing projects
    ├── required_skills.txt  # Skills needed for the role
    └── context.txt          # Current industry trends
```

---

## ⚡ Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your Gemini API key

**Option A — Environment variable (recommended)**
```bash
export GEMINI_API_KEY="your_actual_key_here"
```

**Option B — Edit the source**  
Open `agents/task_generator.py` and replace `"YOUR_KEY_HERE"` with your key.

> Get a free API key at [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 3. Run

```bash
cd career_mentor_cli
python main.py
```

---

## 📝 Customising the Data Files

| File                   | What to edit                              |
|------------------------|-------------------------------------------|
| `data/user.txt`        | Your name and career goal                 |
| `data/skills.txt`      | Skills you already have (one per line)    |
| `data/projects.txt`    | Projects you've built (one per line)      |
| `data/required_skills.txt` | Skills the target role demands        |
| `data/context.txt`     | Hot industry trends you want reflected    |

---

## 🔌 How It Works (Pipeline)

```
user.txt  ──────────────────────────────────────────────► User Profile
skills.txt + required_skills.txt ──► Skill Gap Detection ► Gaps List
Gaps List + context.txt + projects.txt ──► Gemini LLM ──► Roadmap 🗺️
```

---

## 🛡️ No API Key? No Problem.

If `GEMINI_API_KEY` is not set, the system automatically falls back to a built-in static suggestion engine — so the CLI always produces useful output.

## System Architecture
User Input Files
      │
      ▼
Goal Analyzer Agent
      │
      ▼
Skill Gap Agent
      │
      ▼
Task Generator Agent
      │
      ▼
Gemini AI API
      │
      ▼
Personalised Learning Roadmap
