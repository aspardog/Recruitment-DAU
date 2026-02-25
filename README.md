# CV Evaluation System with AI

**Automated resume screening powered by LLM semantic analysis.**

Evaluate hundreds of CVs in minutes with AI-powered scoring that understands context, not just keywords. Get ranked finalists with detailed justifications for each score.

---

## Privacy & Data Protection

> **Your candidates' data stays under your control.**

This system was designed with **privacy as a core principle**. CVs contain highly sensitive personal information — employment history, education, contact details, and more. We take this seriously:

| Feature | Privacy Benefit |
|---------|-----------------|
| **Local LLM Option** | 100% offline processing — no data leaves your computer |
| **No External Services** | No tracking, analytics, or third-party data collection |
| **Local Caching** | Response cache stored locally in `.cache/` directory |
| **No Data Retention** | System processes CVs in memory, no persistent storage of parsed content |
| **Open Source** | Full transparency — audit the code yourself |

### Privacy Modes

**Maximum Privacy (Recommended for sensitive data):**
```bash
USE_LOCAL_LLM=true
LOCAL_LLM_BACKEND=ollama
```
- All processing happens on your machine
- Zero network requests during CV analysis
- Ideal for: HR departments, legal compliance, GDPR requirements

**Cloud Mode (Groq API):**
```bash
USE_LOCAL_LLM=false
GROQ_API_KEY=your_key
```
- CV text is sent to Groq's API for analysis
- Subject to [Groq's privacy policy](https://groq.com/privacy-policy/)
- Faster processing, but data leaves your network

### Compliance Considerations

- **GDPR**: Local LLM mode supports data minimization and purpose limitation principles
- **CCPA**: No sale or sharing of personal information
- **SOC 2**: Local processing eliminates third-party data processor concerns

> **Recommendation**: For maximum privacy and regulatory compliance, use the local LLM option with Ollama. Your candidates' personal data never leaves your infrastructure.

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

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r Code/requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your preferred LLM backend:

**Option A: Local LLM (Recommended — Private & Free)**
```bash
USE_LOCAL_LLM=true
LOCAL_LLM_BACKEND=ollama
LOCAL_LLM_MODEL=qwen2.5:3b
```
> Requires [Ollama](https://ollama.ai) running locally (`ollama serve`)
>
> **Why local?** CVs contain sensitive personal data. Local processing ensures candidate information never leaves your computer.

**Option B: Cloud LLM (Groq)**
```bash
USE_LOCAL_LLM=false
GROQ_API_KEY=your_api_key_here
```
> Get your free API key at [console.groq.com](https://console.groq.com/keys)
>
> **Privacy note:** CV text is sent to Groq's API. Review their [privacy policy](https://groq.com/privacy-policy/) before use with real candidate data.

### 3. Add CVs

Place PDF files in the candidates directory (default: `Data Analyst/`)

### 4. Run Evaluation

```bash
python main.py
```

### 5. View Results

- **Console**: Real-time progress and final ranking
- **Finalists/**: Top N candidates with renamed files (`Rank_1_Score_85_Name.pdf`)
- **Report**: `Finalists/REPORTE_FINALISTAS.txt` with detailed justifications

---

## How It Works

```
                          ┌─────────────────────┐
                          │   PDF CVs (Input)   │
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                          │    cv_parser.py     │
                          │  Text Extraction    │
                          │  (pdfplumber/PyPDF2)│
                          └──────────┬──────────┘
                                     │
                 ┌───────────────────┼───────────────────┐
                 │                   │                   │
      ┌──────────▼──────────┐        │        ┌──────────▼──────────┐
      │   llm_analyzer.py   │        │        │ local_llm_analyzer  │
      │    (Groq Cloud)     │        │        │ (Ollama/LM Studio)  │
      └──────────┬──────────┘        │        └──────────┬──────────┘
                 │                   │                   │
                 └───────────────────┼───────────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │     scorer.py       │
                          │  Weighted Scoring   │
                          └──────────┬──────────┘
                                     │
                          ┌──────────▼──────────┐
                          │  Ranked Finalists   │
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

## Configuration

### Directory Structure

```
Recruitment/
├── main.py                    # Entry point
├── test_local_llm.py          # Test local LLM setup
│
├── Code/                      # Core modules
│   ├── cv_parser.py           # PDF text extraction
│   ├── llm_analyzer.py        # Cloud LLM (Groq)
│   ├── local_llm_analyzer.py  # Local LLM (Ollama)
│   ├── scorer.py              # Weighted scoring
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
| `ASPECT_MODIFIERS` | Score boosts (+40% NGO) and penalties |

### System Settings (`Parameters/config.py`)

| Variable | Default | Purpose |
|----------|---------|---------|
| `NUM_FINALISTS` | 15 | How many top candidates to select |
| `CANDIDATES_DIR` | "Data Analyst" | Input directory with CVs |
| `FINALISTS_DIR` | "Finalists" | Output directory for results |
| `CACHE_EXPIRY_DAYS` | 30 | How long to cache LLM responses |

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
    # ...
}
```

### 2. Define Required Skills

```python
REQUIRED_SKILLS = {
    'skill_name': {
        'keywords': ['keyword1', 'keyword2', 'tool_name'],
        'weight': 15,  # Relative importance (sum doesn't need to equal 100)
        'description': 'What this skill represents'
    },
    # Add more skills...
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
    # Add more...
}
```

### 4. Set Education Criteria

```python
EDUCATION_KEYWORDS = {
    'masters': {
        'keywords': ['master', 'msc', 'ma in', 'graduate'],
        'weight': 25,
        'description': "Master's degree (preferred)"
    },
    # Add degree levels and relevant fields...
}
```

### 5. Define Experience Criteria

```python
EXPERIENCE_KEYWORDS = {
    'domain_experience': {
        'keywords': ['relevant_industry', 'specific_role', 'organization_type'],
        'weight': 20,
        'description': 'Domain-specific experience'
    },
    # Add more experience types...
}
```

### 6. Adjust Score Boosts/Penalties

```python
ASPECT_MODIFIERS = {
    'boosts': {
        'ideal_background': 1.30,      # +30% for ideal candidates
        'key_certification': 1.20,     # +20% for specific certs
    },
    'penalties': {
        'missing_core_skill': 0.85,    # -15% for missing basics
    }
}
```

### 7. Update LLM Instructions

Modify `CUSTOM_INSTRUCTIONS` to guide the LLM on what to prioritize for your specific role.

### 8. Set Input Directory

In `Parameters/config.py`:

```python
CANDIDATES_DIR = "Your Position Name"  # Directory with CVs
```

---

## LLM Options

### Local LLM (Ollama) — Recommended for Privacy

> **Best choice for handling sensitive CV data**

| Aspect | Detail |
|--------|--------|
| **Privacy** | 100% offline — data never leaves your machine |
| **Cost** | Free, no API fees |
| **Speed** | ~3-5 seconds per CV |
| **Requirements** | 8-16 GB RAM |
| **Network** | No internet required during analysis |

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (choose based on your RAM)
ollama pull qwen2.5:3b      # For 8GB RAM (recommended)
ollama pull llama3.1:8b     # For 16GB+ RAM (higher quality)

# Start server
ollama serve

# Test connection
python test_local_llm.py
```

**Configuration (.env):**
```bash
USE_LOCAL_LLM=true
LOCAL_LLM_BACKEND=ollama
LOCAL_LLM_MODEL=qwen2.5:3b
```

### Cloud LLM (Groq)

> **Note**: CV data is sent to Groq's servers for processing

| Aspect | Detail |
|--------|--------|
| **Privacy** | Data transmitted to Groq API |
| **Cost** | Free tier available, then usage-based |
| **Speed** | ~2 seconds per CV |
| **Requirements** | Internet connection, API key |

```bash
# Get API key at https://console.groq.com/keys
# Add to .env:
USE_LOCAL_LLM=false
GROQ_API_KEY=gsk_your_key_here
```

**When to use Cloud LLM:**
- Processing non-sensitive test data
- When local hardware is insufficient
- Speed is priority over privacy

### Model Comparison

| Option | Model | RAM | Speed | Privacy |
|--------|-------|-----|-------|---------|
| **Local (light)** | `qwen2.5:3b` | 8GB | ~3s/CV | Full |
| **Local (quality)** | `llama3.1:8b` | 16GB | ~5s/CV | Full |
| **Cloud** | `llama-3.1-8b-instant` | — | ~2s/CV | Groq servers |

---

## Testing

```bash
# Test local LLM connection
python test_local_llm.py

# Test individual modules
python Code/test_cv_parser.py
python Code/test_llm_analyzer.py
python Code/test_scorer.py
```

---

## Troubleshooting

### Local LLM Not Responding

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve

# Verify model is installed
ollama list
```

### Groq API Errors

- Verify `GROQ_API_KEY` in `.env`
- Check API quota at [console.groq.com](https://console.groq.com)
- Try reducing `LLM_MAX_TOKENS` if hitting limits

### PDF Parsing Issues

- Ensure PDFs are not password-protected
- Check for scanned images (OCR not supported)
- Try opening the PDF to verify it's not corrupted

### Memory Issues with Local LLM

- Use a smaller model (`qwen2.5:3b` instead of `llama3.1:8b`)
- Close other applications
- Reduce `MAX_CV_LENGTH` in `model_parameters.py`

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

## Current Configuration

**Position**: WJP Data Analyst – Consultant (World Justice Project)

The current configuration evaluates candidates for a data analyst role at an international NGO focused on rule of law research. Key criteria include:

- Python/R proficiency with real project evidence
- Git/GitHub for reproducible workflows
- Experience with NGOs, research institutions, or policy organizations
- Survey data experience (WJP's primary methodology)
- Bilingual English-Spanish (bonus)

---

## License

MIT License - See [LICENSE](LICENSE) for details.
