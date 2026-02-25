"""
=============================================================================
                    SCORER MODULE - Sistema de Puntuación
             Calcula puntajes finales y rankea candidatos
=============================================================================

PROPÓSITO:
    Convierte análisis multi-dimensional de CVs en un puntaje final único
    (0-100) que permite rankear y comparar candidatos objetivamente.

SISTEMA DE PUNTUACIÓN PONDERADA:
    El puntaje final es una suma ponderada de 4 categorías:

    ┌─────────────────────────────────────────────────────────┐
    │  PUNTAJE FINAL = Σ (Category_Score × Category_Weight)  │
    └─────────────────────────────────────────────────────────┘

    CATEGORÍAS Y PESOS (config.CATEGORY_WEIGHTS):
        1. Required Skills:   40% - Habilidades técnicas críticas
           (Python, R, Git, WJP domain, Statistics, Data Cleaning)

        2. Education:         30% - Formación académica
           (Master's preferido, PhD valorado, fields relevantes)

        3. Preferred Skills:  20% - Habilidades valoradas
           (AI/ML, SQL, Stata, Bilingual, Visualization)

        4. Experience:        10% - Experiencia laboral
           (WJP domain experience, Data analyst, Research)

    EJEMPLO DE CÁLCULO:
        Candidato con:
            - Required Skills: 85% → 85 × 0.40 = 34.0 puntos
            - Education: 90% → 90 × 0.30 = 27.0 puntos
            - Preferred Skills: 60% → 60 × 0.20 = 12.0 puntos
            - Experience: 70% → 70 × 0.10 = 7.0 puntos
            ──────────────────────────────────────────
            PUNTAJE FINAL: 80.0 / 100

FUNCIONES PRINCIPALES:
    1. calculate_weighted_score():
       - Calcula puntaje final ponderado

    2. score_candidate():
       - Crea registro completo con breakdown detallado

    3. rank_candidates():
       - Ordena candidatos por puntaje final

    4. get_top_candidates():
       - Selecciona top N finalistas

    5. print_ranking_report():
       - Genera reporte visual de ranking

USO:
    scorer = CandidateScorer()
    candidate_score = scorer.score_candidate(cv_path, analysis)
    top_n = scorer.get_top_candidates(all_scores, n=10)

INTERPRETACIÓN DE PUNTAJES:
    90-100: Candidato excepcional (match casi perfecto)
    80-89:  Candidato excelente (muy bien calificado)
    70-79:  Candidato sólido (cumple bien los requisitos)
    60-69:  Candidato aceptable (cumple requisitos básicos)
    <60:    Candidato insuficiente (faltan skills críticas)

=============================================================================
"""

from typing import Dict, List, Tuple
from config import CATEGORY_WEIGHTS


class CandidateScorer:
    """Scores and ranks candidates based on job requirements match."""

    def __init__(self):
        """Initialize the candidate scorer."""
        self.category_weights = CATEGORY_WEIGHTS

    def calculate_weighted_score(self, analysis: Dict) -> float:
        """
        Calcula el puntaje final ponderado de un candidato.

        FÓRMULA:
            Final_Score = Σ (Category_Percentage × Category_Weight)

        PROCESO:
            1. Extrae percentage de cada categoría del análisis
            2. Multiplica cada percentage por su peso correspondiente
            3. Suma todos los productos
            4. Redondea a 2 decimales

        EJEMPLO DETALLADO:
            analysis = {
                'required_skills': {'percentage': 85.0},
                'preferred_skills': {'percentage': 60.0},
                'education': {'percentage': 90.0},
                'experience': {'percentage': 70.0}
            }

            Cálculo:
                required:  85.0 × 0.40 = 34.0
                preferred: 60.0 × 0.20 = 12.0
                education: 90.0 × 0.30 = 27.0
                experience: 70.0 × 0.10 = 7.0
                                Total = 80.0

        AJUSTE DE PESOS:
            Los pesos se configuran en config.CATEGORY_WEIGHTS
            Deben sumar 1.0 (100%)
            Ejemplo para puesto técnico senior:
                required_skills: 0.50 (más énfasis en técnico)
                education: 0.20
                preferred_skills: 0.20
                experience: 0.10

        Args:
            analysis: Dict con análisis de RequirementsAnalyzer o LLMAnalyzer
                     Debe contener keys: required_skills, preferred_skills,
                     education, experience, cada uno con 'percentage'

        Returns:
            float: Puntaje final ponderado (0.00 - 100.00)
                  Redondeado a 2 decimales

        Raises:
            KeyError: Si analysis no tiene las categorías requeridas
        """
        required_score = analysis['required_skills']['percentage']
        preferred_score = analysis['preferred_skills']['percentage']
        education_score = analysis['education']['percentage']
        experience_score = analysis['experience']['percentage']

        weighted_score = (
            required_score * self.category_weights['required_skills'] +
            preferred_score * self.category_weights['preferred_skills'] +
            education_score * self.category_weights['education'] +
            experience_score * self.category_weights['experience']
        )

        return round(weighted_score, 2)

    def score_candidate(self, cv_path: str, analysis: Dict) -> Dict[str, any]:
        """
        Create a complete candidate score record.

        Args:
            cv_path: Path to candidate's CV
            analysis: Analysis results from RequirementsAnalyzer

        Returns:
            Dictionary with candidate scoring information
        """
        final_score = self.calculate_weighted_score(analysis)

        return {
            'cv_path': cv_path,
            'final_score': final_score,
            'analysis': analysis,
            'breakdown': {
                'required_skills': {
                    'score': analysis['required_skills']['percentage'],
                    'weight': self.category_weights['required_skills'],
                    'weighted_contribution': analysis['required_skills']['percentage'] * self.category_weights['required_skills']
                },
                'preferred_skills': {
                    'score': analysis['preferred_skills']['percentage'],
                    'weight': self.category_weights['preferred_skills'],
                    'weighted_contribution': analysis['preferred_skills']['percentage'] * self.category_weights['preferred_skills']
                },
                'education': {
                    'score': analysis['education']['percentage'],
                    'weight': self.category_weights['education'],
                    'weighted_contribution': analysis['education']['percentage'] * self.category_weights['education']
                },
                'experience': {
                    'score': analysis['experience']['percentage'],
                    'weight': self.category_weights['experience'],
                    'weighted_contribution': analysis['experience']['percentage'] * self.category_weights['experience']
                }
            }
        }

    def rank_candidates(self, scored_candidates: List[Dict]) -> List[Dict]:
        """
        Rank candidates by their final scores.

        Args:
            scored_candidates: List of candidate score records

        Returns:
            Sorted list of candidates (highest score first)
        """
        return sorted(scored_candidates, key=lambda x: x['final_score'], reverse=True)

    def get_top_candidates(self, scored_candidates: List[Dict], n: int = 3) -> List[Dict]:
        """
        Get top N candidates.

        Args:
            scored_candidates: List of candidate score records
            n: Number of top candidates to return

        Returns:
            List of top N candidates
        """
        ranked = self.rank_candidates(scored_candidates)
        return ranked[:n]

    def print_candidate_summary(self, candidate: Dict, rank: int = None):
        """
        Print a formatted summary of a candidate's evaluation.

        Args:
            candidate: Candidate score record
            rank: Optional rank number
        """
        import os
        filename = os.path.basename(candidate['cv_path'])

        if rank:
            print(f"\n{'='*70}")
            print(f"RANK #{rank}: {filename}")
            print(f"{'='*70}")
        else:
            print(f"\n{'='*70}")
            print(f"CANDIDATE: {filename}")
            print(f"{'='*70}")

        print(f"FINAL SCORE: {candidate['final_score']:.2f}/100")
        print(f"\nScore Breakdown:")
        print(f"  Required Skills:   {candidate['breakdown']['required_skills']['score']:.1f}% "
              f"(weight: {candidate['breakdown']['required_skills']['weight']*100:.0f}%) "
              f"→ {candidate['breakdown']['required_skills']['weighted_contribution']:.2f} points")
        print(f"  Preferred Skills:  {candidate['breakdown']['preferred_skills']['score']:.1f}% "
              f"(weight: {candidate['breakdown']['preferred_skills']['weight']*100:.0f}%) "
              f"→ {candidate['breakdown']['preferred_skills']['weighted_contribution']:.2f} points")
        print(f"  Education:         {candidate['breakdown']['education']['score']:.1f}% "
              f"(weight: {candidate['breakdown']['education']['weight']*100:.0f}%) "
              f"→ {candidate['breakdown']['education']['weighted_contribution']:.2f} points")
        print(f"  Experience:        {candidate['breakdown']['experience']['score']:.1f}% "
              f"(weight: {candidate['breakdown']['experience']['weight']*100:.0f}%) "
              f"→ {candidate['breakdown']['experience']['weighted_contribution']:.2f} points")

        summary = candidate['analysis']['summary']
        print(f"\nOverall Match: {summary['total_skills_matched']}/{summary['total_skills_possible']} "
              f"criteria matched ({summary['match_rate']:.1f}%)")

    def print_ranking_report(self, ranked_candidates: List[Dict], top_n: int = 3):
        """
        Print a complete ranking report.

        Args:
            ranked_candidates: Sorted list of candidates
            top_n: Number of top candidates to highlight
        """
        print("\n" + "="*70)
        print("CANDIDATE RANKING REPORT")
        print("="*70)
        print(f"\nTotal Candidates Evaluated: {len(ranked_candidates)}")
        print(f"Top {top_n} Finalists Selected\n")

        for i, candidate in enumerate(ranked_candidates, 1):
            if i <= top_n:
                self.print_candidate_summary(candidate, rank=i)
