# Quick Start Guide

## Setup (3 steps)

### 1. Install Dependencies
```bash
pip install -r Code/requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (for cloud LLM)
# OR set USE_LOCAL_LLM=true for local LLM
```

### 3. Run
```bash
python main.py
```

## Architecture

```
INPUT: PDFs in "Data Analyst/"
  ↓
LLM Analysis (Groq Cloud or Local Ollama)
  → Granular scoring 0-100 per skill
  ↓
OUTPUT: Top N finalists in "Finalists/"
```

## Configuration

All evaluation criteria are in `Parameters/model_parameters.py`:
- `REQUIRED_SKILLS`, `PREFERRED_SKILLS`: Skills with keywords and weights
- `EDUCATION_KEYWORDS`, `EXPERIENCE_KEYWORDS`: Education/experience criteria
- `CATEGORY_WEIGHTS`: Scoring weights (default: Required 40%, Education 30%, Preferred 20%, Experience 10%)
- `CUSTOM_INSTRUCTIONS`: Detailed instructions for LLM

System settings are in `Parameters/config.py`:
- `NUM_FINALISTS`: How many top candidates to select
- `CANDIDATES_DIR`: Input directory with CV PDFs

## Scoring Formula

```
Final Score = (Required Skills × 40%) + (Education × 30%) +
              (Preferred Skills × 20%) + (Experience × 10%)
```

## Tests

```bash
python Code/test_cv_parser.py
python Code/test_scorer.py
python Code/test_llm_analyzer.py
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | `pip install -r Code/requirements.txt` |
| `No PDF files found` | Add PDFs to `Data Analyst/` |
| `GROQ_API_KEY not found` | Create `.env` with your API key |
| `LLM failed to initialize` | Check API key or run `python test_local_llm.py` |

---

For local LLM setup, see `Documentation/LOCAL_LLM_SETUP.md`
