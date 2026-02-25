"""
Unit Tests for Scorer Module
Tests candidate scoring and ranking functionality.
"""

import unittest
import sys
from pathlib import Path

# Add Code and Parameters directories to path
code_dir = Path(__file__).parent
parameters_dir = Path(__file__).parent.parent / "Parameters"
sys.path.insert(0, str(code_dir))
sys.path.insert(0, str(parameters_dir))

from scorer import CandidateScorer


def create_mock_analysis(required_pct=80.0, preferred_pct=60.0, education_pct=100.0, experience_pct=50.0):
    """Create a mock analysis result for testing."""
    return {
        'required_skills': {
            'percentage': required_pct,
            'details': {},
            'total_score': required_pct,
            'max_possible_score': 100.0
        },
        'preferred_skills': {
            'percentage': preferred_pct,
            'details': {},
            'total_score': preferred_pct,
            'max_possible_score': 100.0
        },
        'education': {
            'percentage': education_pct,
            'details': {},
            'total_score': education_pct,
            'max_possible_score': 100.0
        },
        'experience': {
            'percentage': experience_pct,
            'details': {},
            'total_score': experience_pct,
            'max_possible_score': 100.0
        },
        'summary': {
            'total_skills_matched': 8,
            'total_skills_possible': 10,
            'match_rate': 80.0
        }
    }


class TestCandidateScorer(unittest.TestCase):
    """Test cases for CandidateScorer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.scorer = CandidateScorer()

    def test_scorer_initialization(self):
        """Test that scorer initializes correctly."""
        self.assertIsInstance(self.scorer, CandidateScorer)
        self.assertIsNotNone(self.scorer.category_weights)

    def test_category_weights_sum(self):
        """Test that category weights sum to 1.0."""
        total_weight = sum(self.scorer.category_weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=2)
        print(f"\n  ✓ Category weights sum to {total_weight:.2f}")

    def test_calculate_weighted_score(self):
        """Test weighted score calculation."""
        # Create mock analysis with known percentages
        mock_analysis = {
            'required_skills': {'percentage': 80.0},
            'preferred_skills': {'percentage': 60.0},
            'education': {'percentage': 100.0},
            'experience': {'percentage': 50.0}
        }

        score = self.scorer.calculate_weighted_score(mock_analysis)

        # Calculate expected score using actual CATEGORY_WEIGHTS from config
        expected = (
            80.0 * 0.40 +  # required_skills (0.40)
            60.0 * 0.20 +  # preferred_skills (0.20)
            100.0 * 0.30 + # education (0.30)
            50.0 * 0.10    # experience (0.10)
        )

        self.assertEqual(score, expected)
        print(f"\n  ✓ Weighted score: {score:.2f}/100 (expected: {expected:.2f})")

    def test_score_candidate(self):
        """Test complete candidate scoring."""
        # Create a mock analysis with known values
        analysis = create_mock_analysis(
            required_pct=85.0,
            preferred_pct=70.0,
            education_pct=90.0,
            experience_pct=60.0
        )

        candidate_score = self.scorer.score_candidate("test_cv.pdf", analysis)

        # Check structure
        self.assertIn('cv_path', candidate_score)
        self.assertIn('final_score', candidate_score)
        self.assertIn('analysis', candidate_score)
        self.assertIn('breakdown', candidate_score)

        # Check breakdown structure
        breakdown = candidate_score['breakdown']
        self.assertIn('required_skills', breakdown)
        self.assertIn('preferred_skills', breakdown)
        self.assertIn('education', breakdown)
        self.assertIn('experience', breakdown)

        # Check that each category has correct fields
        for category in ['required_skills', 'preferred_skills', 'education', 'experience']:
            self.assertIn('score', breakdown[category])
            self.assertIn('weight', breakdown[category])
            self.assertIn('weighted_contribution', breakdown[category])

        print(f"\n  ✓ Candidate scored: {candidate_score['final_score']:.2f}/100")
        print(f"    Breakdown:")
        for category, data in breakdown.items():
            print(f"      {category}: {data['weighted_contribution']:.2f} points")

    def test_rank_candidates(self):
        """Test candidate ranking."""
        # Create mock candidates with different scores
        candidates = [
            {'cv_path': 'candidate1.pdf', 'final_score': 75.0},
            {'cv_path': 'candidate2.pdf', 'final_score': 90.0},
            {'cv_path': 'candidate3.pdf', 'final_score': 60.0},
            {'cv_path': 'candidate4.pdf', 'final_score': 85.0},
        ]

        ranked = self.scorer.rank_candidates(candidates)

        # Check that candidates are sorted in descending order
        self.assertEqual(ranked[0]['final_score'], 90.0)
        self.assertEqual(ranked[1]['final_score'], 85.0)
        self.assertEqual(ranked[2]['final_score'], 75.0)
        self.assertEqual(ranked[3]['final_score'], 60.0)

        print(f"\n  ✓ Ranked {len(ranked)} candidates:")
        for i, candidate in enumerate(ranked, 1):
            print(f"    {i}. {candidate['cv_path']}: {candidate['final_score']:.2f}")

    def test_get_top_candidates(self):
        """Test getting top N candidates."""
        candidates = [
            {'cv_path': 'candidate1.pdf', 'final_score': 75.0},
            {'cv_path': 'candidate2.pdf', 'final_score': 90.0},
            {'cv_path': 'candidate3.pdf', 'final_score': 60.0},
            {'cv_path': 'candidate4.pdf', 'final_score': 85.0},
            {'cv_path': 'candidate5.pdf', 'final_score': 70.0},
        ]

        top_3 = self.scorer.get_top_candidates(candidates, n=3)

        # Check that we got exactly 3 candidates
        self.assertEqual(len(top_3), 3)

        # Check that they are the top 3
        self.assertEqual(top_3[0]['final_score'], 90.0)
        self.assertEqual(top_3[1]['final_score'], 85.0)
        self.assertEqual(top_3[2]['final_score'], 75.0)

        print(f"\n  ✓ Top 3 candidates selected:")
        for i, candidate in enumerate(top_3, 1):
            print(f"    {i}. {candidate['cv_path']}: {candidate['final_score']:.2f}")

    def test_edge_case_empty_list(self):
        """Test handling of empty candidate list."""
        top = self.scorer.get_top_candidates([], n=3)
        self.assertEqual(len(top), 0)

    def test_edge_case_fewer_than_n(self):
        """Test when there are fewer candidates than requested."""
        candidates = [
            {'cv_path': 'candidate1.pdf', 'final_score': 75.0},
            {'cv_path': 'candidate2.pdf', 'final_score': 90.0},
        ]

        top_3 = self.scorer.get_top_candidates(candidates, n=3)

        # Should return all available candidates
        self.assertEqual(len(top_3), 2)


class TestScorerIntegration(unittest.TestCase):
    """Integration tests for scorer functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.scorer = CandidateScorer()

    def test_complete_workflow(self):
        """Test complete scoring workflow with mock analyses."""
        # Mock analyses with different qualification levels
        mock_analyses = {
            'high_qualified.pdf': create_mock_analysis(
                required_pct=90.0,
                preferred_pct=85.0,
                education_pct=95.0,
                experience_pct=80.0
            ),
            'medium_qualified.pdf': create_mock_analysis(
                required_pct=70.0,
                preferred_pct=60.0,
                education_pct=80.0,
                experience_pct=50.0
            ),
            'low_qualified.pdf': create_mock_analysis(
                required_pct=40.0,
                preferred_pct=30.0,
                education_pct=50.0,
                experience_pct=20.0
            )
        }

        scored_candidates = []

        for cv_path, analysis in mock_analyses.items():
            candidate = self.scorer.score_candidate(cv_path, analysis)
            scored_candidates.append(candidate)

        # Rank candidates
        ranked = self.scorer.rank_candidates(scored_candidates)

        # Verify ranking order makes sense
        self.assertEqual(ranked[0]['cv_path'], 'high_qualified.pdf')
        self.assertEqual(ranked[2]['cv_path'], 'low_qualified.pdf')

        print(f"\n  ✓ Complete workflow test - Rankings:")
        for i, candidate in enumerate(ranked, 1):
            print(f"    {i}. {candidate['cv_path']}: {candidate['final_score']:.2f}/100")

        # High qualified should have significantly higher score
        self.assertGreater(ranked[0]['final_score'], ranked[1]['final_score'])
        self.assertGreater(ranked[1]['final_score'], ranked[2]['final_score'])


def run_tests():
    """Run all scorer tests."""
    print("\n" + "="*70)
    print("RUNNING SCORER TESTS")
    print("="*70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestCandidateScorer))
    suite.addTests(loader.loadTestsFromTestCase(TestScorerIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    run_tests()
