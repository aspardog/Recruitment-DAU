# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

Automated CV evaluation system for recruitment. Uses local LLM-based semantic analysis to evaluate candidates against job requirements. All processing happens locally — no data leaves your machine.

**Production tested:** Selected 15 finalists from 2,000+ candidates for a Data Analyst position.

## Architecture

### Data Flow

```
PDFs in CANDIDATES_DIR (default: "Data Analyst/")
  ↓
cv_parser.py            # pdfplumber extraction (PyPDF2 fallback)
  ↓
local_llm_analyzer.py   # Local LLM via Ollama (100% private)
  ↓
scorer.py               # Weighted scoring across 4 categories
  ↓
Finalists/              # Top N candidates with ranked filenames
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `main.py` | Entry point, orchestrates pipeline |
| `Code/cv_parser.py` | PDF text extraction with fallback |
| `Code/local_llm_analyzer.py` | Local LLM analysis (Ollama) |
| `Code/scorer.py` | Weighted scoring: Required(35%) + Experience(30%) + Education(20%) + Preferred(15%) |

### Configuration (Two Files)

**`Parameters/model_parameters.py`** — Single source of truth for ALL evaluation criteria:
- `CANDIDATE_PROFILE`: Position details and role description
- `REQUIRED_SKILLS`, `PREFERRED_SKILLS`: Skills with keywords and weights
- `EDUCATION_KEYWORDS`, `EXPERIENCE_KEYWORDS`: Criteria by category
- `CATEGORY_WEIGHTS`: Scoring weights (must sum to 1.0)
- `CUSTOM_INSTRUCTIONS`: LLM prompt instructions by category
- `ANALYSIS_PROMPT_TEMPLATE`: Full LLM prompt with chain-of-thought
- `ASPECT_MODIFIERS`: Score boosts and penalties

**`Parameters/config.py`** — System configuration:
- `CANDIDATES_DIR`, `FINALISTS_DIR`, `NUM_FINALISTS`
- LLM settings and timeouts
- Imports all criteria from model_parameters.py

### Scoring Formula

```
Final Score = (Required × 0.35) + (Experience × 0.30) + (Education × 0.20) + (Preferred × 0.15)
```

Each category score (0-100) is based on LLM analysis with evidence extraction.

## Commands

```bash
# Run full evaluation pipeline
python main.py

# Install dependencies
pip install -r Code/requirements.txt

# Test local LLM connectivity
python test_local_llm.py

# Run individual module tests
python Code/test_cv_parser.py
python Code/test_llm_analyzer.py
python Code/test_scorer.py
```

## Configuration

### Environment Setup

```bash
cp .env.example .env
```

**Local LLM with Ollama:**
```
USE_LOCAL_LLM=true
LOCAL_LLM_BACKEND=ollama
LOCAL_LLM_MODEL=qwen2.5:3b    # For 8GB RAM
# LOCAL_LLM_MODEL=llama3.1:8b  # For 16GB+ RAM
```

### Adapting for a Different Position

Edit `Parameters/model_parameters.py`:
1. Update `CANDIDATE_PROFILE` with position details and role description
2. Modify `REQUIRED_SKILLS`, `PREFERRED_SKILLS` with relevant keywords and weights
3. Update `EDUCATION_KEYWORDS`, `EXPERIENCE_KEYWORDS` for the new role
4. Adjust `CUSTOM_INSTRUCTIONS` sections for LLM evaluation guidance
5. Review `ASPECT_MODIFIERS` boosts/penalties for domain-specific scoring
6. Update `CANDIDATES_DIR` in `config.py` to point to CV directory

## Troubleshooting

**Local LLM not responding:**
- Ensure `ollama serve` is running
- Run `python test_local_llm.py` for diagnostics
- Try a smaller model (qwen2.5:3b) if memory-constrained
- Verify model is installed: `ollama list`
