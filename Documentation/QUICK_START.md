# Quick Start Guide

Get up and running in 5 minutes. All processing happens locally — no data leaves your computer.

## Setup (4 steps)

### 1. Install Dependencies
```bash
pip install -r Code/requirements.txt
```

### 2. Install Ollama
```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull qwen2.5:3b

# Start the server
ollama serve
```

### 3. Configure Environment
```bash
cp .env.example .env
```

The default configuration uses local LLM (Ollama). No changes needed.

### 4. Run
```bash
python main.py
```

## Architecture

```
INPUT: PDFs in "Data Analyst/"
  ↓
Local LLM Analysis (Ollama)
  → Granular scoring 0-100 per skill
  → Evidence extraction from CV
  ↓
OUTPUT: Top N finalists in "Finalists/"
```

## Configuration

All evaluation criteria are in `Parameters/model_parameters.py`:
- `REQUIRED_SKILLS`, `PREFERRED_SKILLS`: Skills with keywords and weights
- `EDUCATION_KEYWORDS`, `EXPERIENCE_KEYWORDS`: Education/experience criteria
- `CATEGORY_WEIGHTS`: Scoring weights
- `CUSTOM_INSTRUCTIONS`: Detailed instructions for LLM

System settings are in `Parameters/config.py`:
- `NUM_FINALISTS`: How many top candidates to select (default: 15)
- `CANDIDATES_DIR`: Input directory with CV PDFs

## Scoring Formula

```
Final Score = (Required Skills × 35%) + (Experience × 30%) +
              (Education × 20%) + (Preferred Skills × 15%)
```

## Tests

```bash
# Test LLM connection
python test_local_llm.py

# Test individual modules
python Code/test_cv_parser.py
python Code/test_scorer.py
python Code/test_llm_analyzer.py
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | `pip install -r Code/requirements.txt` |
| `No PDF files found` | Add PDFs to `Data Analyst/` directory |
| `LLM failed to initialize` | Ensure `ollama serve` is running |
| `Connection refused` | Start Ollama: `ollama serve` |
| `Model not found` | Pull model: `ollama pull qwen2.5:3b` |

---

For detailed LLM setup, see `Documentation/LOCAL_LLM_SETUP.md`
