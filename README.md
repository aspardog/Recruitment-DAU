# CV Evaluation System with AI

**Automated resume screening powered by LLM semantic analysis.**

Evaluate thousands of CVs in minutes with AI-powered scoring that understands context, not just keywords. Get ranked finalists with detailed justifications for each score.

> **Real-world tested:** This system was used to select the **top 15 finalists from over 2,000 candidates** for a Data Analyst position at an international NGO.

---

## Privacy & Data Protection

> **Your candidates' data stays under your control.**

This system was designed with **privacy as a core principle**. CVs contain highly sensitive personal information — employment history, education, contact details, and more. We take this seriously:

| Feature | Privacy Benefit |
|---------|-----------------|
| **100% Local Processing** | All analysis runs on your machine with Ollama — no data leaves your computer |
| **No External Services** | No tracking, analytics, or third-party data collection |
| **Local Caching** | Response cache stored locally in `.cache/` directory |
| **No Data Retention** | System processes CVs in memory, no persistent storage of parsed content |
| **Open Source** | Full transparency — audit the code yourself |

### Compliance

- **GDPR**: Local processing supports data minimization and purpose limitation principles
- **CCPA**: No sale or sharing of personal information
- **SOC 2**: No third-party data processors involved

> **All CV data stays on your infrastructure.** The system uses Ollama for local LLM inference, ensuring candidate information never leaves your network.

---

## Features

### Privacy-First Design
- **100% Local Processing** — Run entirely offline with Ollama, no data leaves your machine
- **No External Dependencies** — Zero tracking, analytics, or third-party data collection
- **GDPR/CCPA Ready** — Full control over candidate data processing and retention

### Intelligent Analysis
- **Semantic Understanding** — LLM comprehends context, synonyms, and implied skills
- **Evidence-Based Scoring** — Each score includes extracted evidence from the CV
- **Chain-of-Thought Reasoning** — Transparent explanations for every scoring decision
- **Recency Weighting** — Recent experience valued higher than older roles

### Flexibility & Control
- **Weighted Categories** — Customizable weights for skills, education, and experience
- **Local Caching** — 30-day response cache stored locally, prevents redundant processing
- **Detailed Reports** — Finalists report with category-by-category justifications
- **Fully Configurable** — Adapt to any position by editing a single configuration file

### Production Tested
- **Proven at Scale** — Successfully evaluated 2,000+ CVs in a real recruitment process
- **Accurate Ranking** — Selected 15 finalists that matched human expert assessment
- **Fast Processing** — ~3-5 seconds per CV with local LLM

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r Code/requirements.txt
```

### 2. Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull qwen2.5:3b      # For 8GB RAM
ollama pull llama3.1:8b     # For 16GB+ RAM

# Start the server
ollama serve
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
USE_LOCAL_LLM=true
LOCAL_LLM_BACKEND=ollama
LOCAL_LLM_MODEL=qwen2.5:3b
```

### 4. Add CVs

Place PDF files in the candidates directory (default: `Data Analyst/`)

### 5. Run Evaluation

```bash
python main.py
```

### 6. View Results

- **Console**: Real-time progress and final ranking
- **Finalists/**: Top N candidates with renamed files (`Rank_1_Score_85_Name.pdf`)
- **Report**: `Finalists/REPORTE_FINALISTAS.txt` with detailed justifications

---

## How It Works

```
                          ┌─────────────────────┐
                          │   PDF CVs (Input)   │
                          │   (e.g., 2,000+)    │
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                          │    cv_parser.py     │
                          │  Text Extraction    │
                          │  (pdfplumber/PyPDF2)│
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                          │ local_llm_analyzer  │
                          │   (Ollama Local)    │
                          │  Semantic Analysis  │
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                          │     scorer.py       │
                          │  Weighted Scoring   │
                          │  4 Categories       │
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                          │  Ranked Finalists   │
                          │  (e.g., Top 15)     │
                          │    + Report         │
                          └─────────────────────┘
```

### Scoring Formula

Each candidate receives a **final score (0-100)** calculated as:

```
Final Score = (Required Skills × 35%) + (Experience × 30%) + (Education × 20%) + (Preferred Skills × 15%)
```

| Category | Weight | What It Measures |
|----------|--------|------------------|
| **Required Skills** | 35% | Core technical skills (Python, R, Git, domain expertise) |
| **Experience** | 30% | Relevant work history (NGO, research, policy, social science) |
| **Education** | 20% | Academic background (Master's preferred, relevant fields) |
| **Preferred Skills** | 15% | Nice-to-have skills (SQL, Stata, bilingual, visualization) |

### Score Interpretation

| Score | Meaning |
|-------|---------|
| 90-100 | Exceptional candidate — near-perfect match |
| 80-89 | Excellent candidate — highly qualified |
| 70-79 | Strong candidate — meets requirements well |
| 60-69 | Acceptable candidate — meets basic requirements |
| <60 | Below threshold — missing critical skills |

---

## Testing

The system includes comprehensive tests for each module to ensure reliability.

### Run All Tests

```bash
# Test local LLM connection and response quality
python test_local_llm.py

# Test PDF parsing module
python Code/test_cv_parser.py

# Test LLM analyzer module
python Code/test_llm_analyzer.py

# Test scoring module
python Code/test_scorer.py
```

### Test Descriptions

| Test File | What It Tests |
|-----------|---------------|
| `test_local_llm.py` | Ollama connectivity, model availability, response format validation |
| `Code/test_cv_parser.py` | PDF text extraction, encoding handling, multi-page documents |
| `Code/test_llm_analyzer.py` | LLM response parsing, JSON validation, score extraction |
| `Code/test_scorer.py` | Weighted scoring calculation, ranking algorithm, edge cases |

### Pre-Production Checklist

Before running on real CVs:

```bash
# 1. Verify Ollama is running
curl http://localhost:11434/api/tags

# 2. Test LLM connection
python test_local_llm.py

# 3. Run module tests
python Code/test_cv_parser.py
python Code/test_llm_analyzer.py
python Code/test_scorer.py

# 4. Test with a small sample (2-3 CVs) before full batch
```

---

## Configuration

### Directory Structure

```
Recruitment/
├── main.py                    # Entry point
├── test_local_llm.py          # Test local LLM setup
│
├── Code/                      # Core modules
│   ├── cv_parser.py           # PDF text extraction
│   ├── llm_analyzer.py        # LLM analysis interface
│   ├── local_llm_analyzer.py  # Local LLM (Ollama)
│   ├── scorer.py              # Weighted scoring
│   ├── test_*.py              # Unit tests
│   └── requirements.txt       # Dependencies
│
├── Parameters/                # Configuration
│   ├── model_parameters.py    # ALL evaluation criteria (SINGLE SOURCE OF TRUTH)
│   └── config.py              # System settings
│
├── Data Analyst/              # INPUT: Candidate CVs (PDF)
└── Finalists/                 # OUTPUT: Top candidates + report
```

### Evaluation Criteria (`Parameters/model_parameters.py`)

This is the **single source of truth** for all evaluation criteria:

| Variable | Purpose |
|----------|---------|
| `CANDIDATE_PROFILE` | Position title, organization, role description |
| `REQUIRED_SKILLS` | Core skills with keywords and weights |
| `PREFERRED_SKILLS` | Nice-to-have skills with keywords and weights |
| `EDUCATION_KEYWORDS` | Academic criteria (degrees, fields) |
| `EXPERIENCE_KEYWORDS` | Work experience criteria |
| `CATEGORY_WEIGHTS` | Weights for final score calculation |
| `CUSTOM_INSTRUCTIONS` | Detailed LLM instructions per category |
| `ASPECT_MODIFIERS` | Score boosts and penalties |

### System Settings (`Parameters/config.py`)

| Variable | Default | Purpose |
|----------|---------|---------|
| `NUM_FINALISTS` | 15 | How many top candidates to select |
| `CANDIDATES_DIR` | "Data Analyst" | Input directory with CVs |
| `FINALISTS_DIR` | "Finalists" | Output directory for results |
| `CACHE_EXPIRY_DAYS` | 30 | How long to cache LLM responses |

---

## LLM Setup (Ollama)

### Installation

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download
```

### Model Selection

| Model | RAM Required | Speed | Quality |
|-------|-------------|-------|---------|
| `qwen2.5:3b` | 8 GB | ~3s/CV | Good — recommended for most hardware |
| `llama3.1:8b` | 16 GB | ~5s/CV | Better — recommended for quality |
| `llama3.1:70b` | 48 GB | ~30s/CV | Best — for critical evaluations |

```bash
# Pull your chosen model
ollama pull qwen2.5:3b

# Start the server
ollama serve

# Verify installation
ollama list
```

### Configuration (.env)

```bash
USE_LOCAL_LLM=true
LOCAL_LLM_BACKEND=ollama
LOCAL_LLM_MODEL=qwen2.5:3b
```

---

## Adapting for a Different Position

To evaluate candidates for a different role:

### 1. Update Position Details

Edit `Parameters/model_parameters.py`:

```python
CANDIDATE_PROFILE = {
    'position_title': 'Your Position Title',
    'organization': 'Your Organization',
    'role_description': 'Detailed description of the role...',
}
```

### 2. Define Required Skills

```python
REQUIRED_SKILLS = {
    'skill_name': {
        'keywords': ['keyword1', 'keyword2', 'tool_name'],
        'weight': 15,
        'description': 'What this skill represents'
    },
}
```

### 3. Configure Preferred Skills

```python
PREFERRED_SKILLS = {
    'nice_to_have_skill': {
        'keywords': ['keyword1', 'keyword2'],
        'weight': 8,
        'description': 'Why this skill is valuable'
    },
}
```

### 4. Set Education & Experience Criteria

Update `EDUCATION_KEYWORDS` and `EXPERIENCE_KEYWORDS` with relevant criteria for your position.

### 5. Adjust Score Modifiers

```python
ASPECT_MODIFIERS = {
    'boosts': {
        'ideal_background': 1.30,      # +30% for ideal candidates
    },
    'penalties': {
        'missing_core_skill': 0.85,    # -15% for missing basics
    }
}
```

### 6. Update LLM Instructions

Modify `CUSTOM_INSTRUCTIONS` to guide the LLM on what to prioritize.

### 7. Set Input Directory

In `Parameters/config.py`:

```python
CANDIDATES_DIR = "Your Position Name"
```

---

## Troubleshooting

### Ollama Not Responding

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve

# Verify model is installed
ollama list


# Re-pull model if needed
ollama pull qwen2.5:3b
```

### PDF Parsing Issues

- Ensure PDFs are not password-protected
- Check for scanned images (OCR not supported)
- Verify PDF is not corrupted by opening it manually

### Memory Issues

- Use a smaller model (`qwen2.5:3b` instead of `llama3.1:8b`)
- Close other applications to free RAM
- Reduce `MAX_CV_LENGTH` in `model_parameters.py`

### Slow Processing

- Ensure Ollama is using GPU if available
- Use a smaller, faster model
- Check system resources with `htop` or Activity Monitor

---

## Output Files

After running `python main.py`:

| File | Description |
|------|-------------|
| `Finalists/Rank_1_Score_85_Name.pdf` | Top candidate CV with rank and score in filename |
| `Finalists/REPORTE_FINALISTAS.txt` | Detailed report with justifications per category |

### Report Format

```
================================================================================
REPORTE DE FINALISTAS - Position Title
Generado: 2024-01-15 14:30
================================================================================

RANK #1: candidate_name.pdf
Score Final: 85.2/100
------------------------------------------------------------
Desglose: Required=88% | Education=82% | Preferred=75% | Experience=90%

Justificación por categoría:

  REQUIRED SKILLS:
    - Python: 92/100
      "5 years pandas, numpy, data analysis at World Bank..."
    - R: 85/100
      "ggplot2, tidyverse, statistical modeling..."

  EXPERIENCE:
    - NGO Experience: 95/100
      "3 years at UNDP, policy research..."
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.
