#!/usr/bin/env python3
"""
=============================================================================
                    SISTEMA DE EVALUACIÓN DE CVs CON IA
                    Main CV Evaluation System
=============================================================================

DESCRIPCIÓN:
    Sistema automatizado de evaluación de CVs usando análisis semántico
    profundo por IA (LLM) para seleccionar los mejores candidatos.

ARQUITECTURA:
    Análisis con LLM:
        - Usa IA (Groq Llama 3.1 8B o LLM local) para comprensión semántica
        - Puntajes granulares 0-100 por cada skill
        - Extrae evidencias y justificaciones
        - Tiempo: ~2-3 segundos por CV
        - Costo: ~$0.001 por CV (Groq) o $0 (local)

FLUJO DE EJECUCIÓN:
    1. Parseo de PDFs → Extracción de texto (cv_parser.py)
    2. Análisis con LLM (llm_analyzer.py o local_llm_analyzer.py)
    3. Scoring → Cálculo de puntajes finales (scorer.py)
    4. Ranking → Selección de top N finalistas
    5. Exportación → Copia de CVs de finalistas a directorio

CONFIGURACIÓN:
    - config.py: Parámetros del sistema (directorios, API)
    - model_parameters.py: Criterios de evaluación y prompts LLM
    - .env: GROQ_API_KEY o USE_LOCAL_LLM=true

MODO DE USO:
    python main.py

SALIDA:
    - Ranking en consola con puntajes detallados
    - Directorio "Finalists/" con PDFs de top N candidatos
    - Nombres de archivo: Rank_1_Score_85_NombreOriginal.pdf

REQUISITOS:
    - Python 3.8+
    - pdfplumber (parsing robusto de PDFs)
    - groq (API de LLM) o ollama (LLM local)
    - python-dotenv (variables de entorno)

    Instalación: pip install -r Code/requirements.txt

AUTOR: Sistema de Reclutamiento Automatizado
VERSIÓN: 3.0 (LLM-Only Architecture)
=============================================================================
"""

import os
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add Code and Parameters directories to path
code_dir = Path(__file__).parent / "Code"
parameters_dir = Path(__file__).parent / "Parameters"
sys.path.insert(0, str(code_dir))
sys.path.insert(0, str(parameters_dir))

from cv_parser import CVParser
from scorer import CandidateScorer
from config import (
    CANDIDATES_DIR,
    FINALISTS_DIR,
    NUM_FINALISTS,
    LLM_ENABLED
)

# Conditional import of LLM analyzer
LLMAnalyzer = None
if LLM_ENABLED:
    # Choose between Groq (cloud) or Local LLM based on environment variable
    use_local_llm = os.environ.get('USE_LOCAL_LLM', 'false').lower() == 'true'

    if use_local_llm:
        try:
            from local_llm_analyzer import LocalLLMAnalyzer as LLMAnalyzer
            backend = os.environ.get('LOCAL_LLM_BACKEND', 'ollama')
            model = os.environ.get('LOCAL_LLM_MODEL', 'llama3.1:8b')
            print(f"✓ Using LOCAL LLM (100% private - data stays on your computer)")
            print(f"  - Backend: {backend}")
            print(f"  - Model: {model}")
            print(f"  - Enhanced with: Chain-of-Thought, Evidence Validation, Recency Analysis")
        except ImportError as e:
            print(f"⚠ Warning: Could not import LocalLLMAnalyzer: {e}")
            print("  Will try Groq LLM or fall back to keyword-based analyzer")
            use_local_llm = False

    if not use_local_llm:
        try:
            from llm_analyzer import LLMAnalyzer
            print("✓ Using Groq LLM (cloud-based)")
        except ImportError as e:
            print(f"Warning: Could not import LLMAnalyzer: {e}")
            print("Will use keyword-based analyzer only")
            LLM_ENABLED = False


def get_project_root() -> Path:
    """
    Obtiene el directorio raíz del proyecto.

    El directorio raíz es donde está ubicado main.py y contiene:
        - Code/: Módulos Python del sistema
        - Data Analyst/: CVs de candidatos (PDFs)
        - Finalists/: Finalistas seleccionados (salida)
        - .env: Variables de entorno (GROQ_API_KEY)
        - config.py: Configuración de evaluación

    Returns:
        Path: Ruta absoluta al directorio raíz del proyecto
    """
    return Path(__file__).parent


def ensure_directories(project_root: Path):
    """
    Asegura que existan los directorios necesarios para el sistema.

    Crea el directorio de finalistas si no existe. El directorio de
    candidatos debe existir previamente y contener los CVs en PDF.

    DIRECTORIOS VERIFICADOS:
        - Finalists/: Donde se copian los CVs de top N candidatos
                     Se crea automáticamente si no existe

    DIRECTORIOS REQUERIDOS (deben existir):
        - Data Analyst/: CVs de candidatos en PDF
                        Si no existe, el parseo fallará

    Args:
        project_root: Path to project root directory

    Side Effects:
        - Crea directorio Finalists/ si no existe
        - Imprime confirmación en consola
    """
    finalists_dir = project_root / FINALISTS_DIR
    finalists_dir.mkdir(exist_ok=True)
    print(f"✓ Finalists directory ready: {finalists_dir}")


def copy_finalist_cvs(top_candidates, project_root: Path):
    """
    Copia los CVs de los finalistas al directorio de salida con nombres descriptivos.

    PROCESO:
        1. Limpia archivos previos del directorio Finalists/
        2. Para cada finalista, crea un nombre de archivo descriptivo:
           Formato: Rank_{N}_Score_{XX}_{NombreOriginal}.pdf
           Ejemplo: Rank_1_Score_87_JuanPerez_CV.pdf

        3. Copia el PDF del candidato al directorio Finalists/

    NOMBRES DE ARCHIVO:
        - Rank_N: Posición en el ranking (1 = mejor)
        - Score_XX: Puntaje final redondeado (0-100)
        - NombreOriginal: Nombre del archivo PDF original

    BENEFICIOS:
        - Fácil identificación del ranking y puntaje
        - Mantiene nombre original para referencia
        - Facilita revisión manual de finalistas

    Args:
        top_candidates: Lista de candidatos top (dict con cv_path y final_score)
        project_root: Path al directorio raíz del proyecto

    Side Effects:
        - Elimina archivos previos en Finalists/
        - Copia nuevos PDFs con nombres descriptivos
        - Imprime progreso en consola
    """
    finalists_dir = project_root / FINALISTS_DIR

    # Clear existing finalists
    for file in finalists_dir.glob("*"):
        if file.is_file():
            file.unlink()

    print(f"\n{'='*70}")
    print("COPYING FINALISTS TO FINALISTS DIRECTORY")
    print(f"{'='*70}")

    for i, candidate in enumerate(top_candidates, 1):
        src_path = Path(candidate['cv_path'])
        # Create a meaningful filename with rank and score
        filename = f"Rank_{i}_Score_{candidate['final_score']:.0f}_{src_path.name}"
        dst_path = finalists_dir / filename

        shutil.copy2(src_path, dst_path)
        print(f"✓ Copied: {src_path.name} → {filename}")

    print(f"\n✓ All finalists copied to: {finalists_dir}")


def generate_finalists_report(top_candidates, project_root: Path):
    """
    Genera un archivo de texto con la explicación de por qué se eligió cada finalista.

    Args:
        top_candidates: Lista de candidatos top con análisis completo
        project_root: Path al directorio raíz del proyecto
    """
    from datetime import datetime

    report_path = project_root / FINALISTS_DIR / "REPORTE_FINALISTAS.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        # Header
        f.write("=" * 80 + "\n")
        f.write("REPORTE DE FINALISTAS - WJP Data Analyst - Consultant\n")
        f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("=" * 80 + "\n\n")

        for i, candidate in enumerate(top_candidates, 1):
            filename = os.path.basename(candidate['cv_path'])
            score = candidate['final_score']
            breakdown = candidate['breakdown']
            analysis = candidate['analysis']

            # Candidate header
            f.write(f"RANK #{i}: {filename}\n")
            f.write(f"Score Final: {score:.1f}/100\n")
            f.write("-" * 60 + "\n")

            # Score breakdown
            f.write(f"Desglose: Required={breakdown['required_skills']['score']:.0f}% | ")
            f.write(f"Education={breakdown['education']['score']:.0f}% | ")
            f.write(f"Preferred={breakdown['preferred_skills']['score']:.0f}% | ")
            f.write(f"Experience={breakdown['experience']['score']:.0f}%\n\n")

            # Key skills justification
            f.write("Justificación por categoría:\n\n")

            for category_name, category_key in [
                ("REQUIRED SKILLS", "required_skills"),
                ("EDUCATION", "education"),
                ("PREFERRED SKILLS", "preferred_skills"),
                ("EXPERIENCE", "experience")
            ]:
                category_data = analysis.get(category_key, {})
                details = category_data.get('details', {})

                if details:
                    f.write(f"  {category_name}:\n")
                    # Show top skills with evidence
                    sorted_skills = sorted(
                        details.items(),
                        key=lambda x: x[1].get('llm_raw_score', x[1].get('score', 0)),
                        reverse=True
                    )
                    for skill_name, skill_data in sorted_skills[:5]:  # Top 5 per category
                        raw_score = skill_data.get('llm_raw_score', skill_data.get('score', 0))
                        evidence = skill_data.get('evidence', 'N/A')
                        if raw_score > 0:
                            f.write(f"    - {skill_name}: {raw_score:.0f}/100\n")
                            if evidence and evidence != 'N/A':
                                f.write(f"      \"{evidence[:80]}{'...' if len(evidence) > 80 else ''}\"\n")
                    f.write("\n")

            f.write("\n" + "=" * 80 + "\n\n")

    print(f"✓ Report generated: {report_path}")


def main():
    """
    Función principal de ejecución del sistema de evaluación de CVs.

    FLUJO DETALLADO:
        1. INICIALIZACIÓN:
            - Crea directorios necesarios (Finalists/)
            - Inicializa componentes: parser, scorer, analyzer
            - Carga configuración del LLM

        2. PARSEO DE CVs (cv_parser.py):
            - Lee todos los PDFs del directorio de candidatos
            - Extrae texto usando pdfplumber (con fallback a PyPDF2)
            - Retorna dict {cv_path: cv_text}

        3. ANÁLISIS CON LLM (llm_analyzer.py / local_llm_analyzer.py):
            - Analiza todos los CVs con LLM
            - Usa IA para análisis semántico profundo
            - Genera puntajes 0-100 por cada criterio
            - Extrae evidencias del CV

        4. SCORING Y RANKING (scorer.py):
            - Calcula puntaje final ponderado para cada candidato
            - Aplica pesos por categoría (config.CATEGORY_WEIGHTS)
            - Ordena candidatos por puntaje final
            - Selecciona top N finalistas

        5. EXPORTACIÓN:
            - Copia PDFs de finalistas a directorio "Finalists/"
            - Renombra archivos con: Rank_N_Score_XX_Original.pdf
            - Muestra reporte final en consola

    CONFIGURACIÓN RELEVANTE:
        - LLM_ENABLED: Activa/desactiva análisis con LLM
        - NUM_FINALISTS: Número de candidatos a seleccionar
        - CANDIDATES_DIR: Directorio con CVs de candidatos
        - FINALISTS_DIR: Directorio de salida con finalistas

    MANEJO DE ERRORES:
        - Si no hay CVs: muestra mensaje y termina
        - Si LLM falla: muestra error y termina
        - Cada componente maneja sus errores internamente

    Returns:
        None (salida por consola y archivos en disco)
    """
    print("\n" + "="*70)
    print("WJP DATA ANALYST - CONSULTANT - CV EVALUATION SYSTEM")
    print("="*70 + "\n")

    # Initialize components
    project_root = get_project_root()
    ensure_directories(project_root)

    parser = CVParser()
    scorer = CandidateScorer()

    # Initialize LLM analyzer
    analyzer = None
    if LLM_ENABLED and LLMAnalyzer is not None:
        try:
            analyzer = LLMAnalyzer()

            # Check which type of LLM was initialized
            use_local_llm = os.environ.get('USE_LOCAL_LLM', 'false').lower() == 'true'
            if use_local_llm:
                print("✓ LLM analyzer initialized successfully (LOCAL)")
                print("  🔒 100% Private - All CV data stays on your computer")
                print("  💰 $0 cost per analysis")
                print("  🧠 Enhanced precision with Chain-of-Thought reasoning\n")
            else:
                print("✓ LLM analyzer initialized successfully (Groq Cloud)")
                print("  ☁️ Cloud-based analysis")
                print("  💰 ~$0.001 per CV\n")
        except Exception as e:
            print(f"❌ Error: LLM analyzer failed to initialize: {e}")
            print("  Please check your API key or local LLM setup.")
            return
    else:
        print("❌ Error: LLM is required but not available.")
        print("  Please set GROQ_API_KEY in .env or USE_LOCAL_LLM=true")
        return

    # Parse CVs
    candidates_path = project_root / CANDIDATES_DIR
    print(f"Scanning for CVs in: {candidates_path}\n")

    cv_texts = parser.parse_cv_directory(str(candidates_path))

    if not cv_texts:
        print("\n❌ No CV files found. Please add PDF files to the candidates directory.")
        return

    print(f"\n{'='*70}")
    print(f"ANALYZING {len(cv_texts)} CANDIDATES")
    print(f"{'='*70}\n")

    # Analyze all candidates using LLM
    analyses = {}
    total = len(cv_texts)
    for i, (cv_path, cv_text) in enumerate(cv_texts.items(), 1):
        filename = os.path.basename(cv_path)
        print(f"[{i}/{total}] Analyzing: {filename}")
        try:
            analysis = analyzer.analyze_cv(cv_text)
            analyses[cv_path] = analysis
        except Exception as e:
            print(f"  ⚠ Error analyzing {filename}: {e}")
            continue

    if not analyses:
        print("\n❌ No candidates could be analyzed.")
        return

    # Score all analyzed candidates
    print(f"\n{'='*70}")
    print(f"SCORING {len(analyses)} QUALIFIED CANDIDATES")
    print(f"{'='*70}\n")

    scored_candidates = []
    for cv_path, analysis in analyses.items():
        filename = os.path.basename(cv_path)
        candidate_score = scorer.score_candidate(cv_path, analysis)
        scored_candidates.append(candidate_score)
        print(f"✓ {filename}: {candidate_score['final_score']:.2f}/100")

    # Rank candidates
    print(f"\n{'='*70}")
    print("RANKING CANDIDATES")
    print(f"{'='*70}")

    top_candidates = scorer.get_top_candidates(scored_candidates, n=NUM_FINALISTS)

    # Print detailed report
    scorer.print_ranking_report(top_candidates, top_n=NUM_FINALISTS)

    # Copy finalist CVs
    copy_finalist_cvs(top_candidates, project_root)

    # Generate explanation report
    generate_finalists_report(top_candidates, project_root)

    print(f"\n{'='*70}")
    print("EVALUATION COMPLETE")
    print(f"{'='*70}")
    print(f"✓ Top {NUM_FINALISTS} candidates selected")
    print(f"✓ Files copied to: {project_root / FINALISTS_DIR}")
    print(f"✓ Report: {project_root / FINALISTS_DIR / 'REPORTE_FINALISTAS.txt'}")
    print()


if __name__ == "__main__":
    main()
