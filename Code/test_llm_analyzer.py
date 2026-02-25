"""
Unit tests for LLM Analyzer Module
Tests the LLM-based CV analysis functionality.
"""

import unittest
import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add Parameters directory to path for imports
parameters_dir = Path(__file__).parent.parent / "Parameters"
sys.path.insert(0, str(parameters_dir))

from llm_analyzer import LLMAnalyzer


class TestLLMAnalyzer(unittest.TestCase):
    """Test cases for LLM Analyzer."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock API key to avoid requiring real credentials in tests
        os.environ['GROQ_API_KEY'] = 'test_api_key_12345'
        self.analyzer = LLMAnalyzer(cache_enabled=False)  # Disable cache for tests

        # Sample CV text for testing
        self.sample_cv = """
        John Doe
        Data Analyst

        EXPERIENCE:
        Senior Data Analyst at TechCorp (2020-Present)
        - 5 years of experience in data analysis
        - Expert in SQL (PostgreSQL, MySQL) with complex query optimization
        - Proficient in Python (pandas, numpy) for data manipulation
        - Created Tableau dashboards for executive reporting
        - Performed statistical analysis and hypothesis testing

        EDUCATION:
        Master of Science in Statistics - MIT (2018)
        Bachelor of Science in Mathematics - UCLA (2016)

        SKILLS:
        - SQL, Python, R, Excel
        - Tableau, Power BI
        - Git, version control
        """

        # Sample skill dict for testing
        self.sample_skills = {
            'sql': {
                'keywords': ['sql', 'postgresql', 'mysql'],
                'weight': 12,
                'category': 'data',
                'description': 'SQL database querying'
            },
            'python': {
                'keywords': ['python', 'pandas', 'numpy'],
                'weight': 10,
                'category': 'programming',
                'description': 'Python programming'
            }
        }

    def test_analyzer_initialization(self):
        """Test that analyzer initializes correctly."""
        from config import GROQ_MODEL
        from model_parameters import LLM_TEMPERATURE, LLM_MAX_RETRIES

        self.assertIsNotNone(self.analyzer.client)
        self.assertEqual(self.analyzer.model, GROQ_MODEL)
        self.assertEqual(self.analyzer.temperature, LLM_TEMPERATURE)
        self.assertEqual(self.analyzer.max_retries, LLM_MAX_RETRIES)

    def test_analyzer_initialization_without_api_key(self):
        """Test that analyzer raises error without API key."""
        del os.environ['GROQ_API_KEY']
        with self.assertRaises(ValueError):
            LLMAnalyzer()

    def test_prompt_building(self):
        """Test that prompts are built correctly."""
        prompt = self.analyzer._build_analysis_prompt(
            self.sample_cv,
            self.sample_skills,
            'Required Skills'
        )

        # Check that prompt contains key elements
        self.assertIn('Required Skills', prompt)
        self.assertIn('sql', prompt.lower())
        self.assertIn('python', prompt.lower())
        self.assertIn('0-100', prompt)
        self.assertIn('JSON', prompt)
        self.assertIn('John Doe', prompt)  # CV content

    def test_score_conversion(self):
        """Test conversion of 0-100 scores to weighted percentages."""
        # Mock LLM response
        llm_response = {
            'skill_scores': {
                'sql': {
                    'score': 90,
                    'evidence': '5 years of SQL experience with PostgreSQL',
                    'justification': 'Strong SQL skills with quantified experience'
                },
                'python': {
                    'score': 75,
                    'evidence': 'Proficient in Python (pandas, numpy)',
                    'justification': 'Good Python skills with relevant libraries'
                }
            },
            'category_summary': 'Strong technical skills'
        }

        result = self.analyzer._parse_llm_response(llm_response, self.sample_skills)

        # Check structure
        self.assertIn('details', result)
        self.assertIn('total_score', result)
        self.assertIn('max_possible_score', result)
        self.assertIn('percentage', result)

        # Check SQL scores
        sql_data = result['details']['sql']
        self.assertTrue(sql_data['matched'])
        self.assertEqual(sql_data['llm_raw_score'], 90)
        self.assertAlmostEqual(sql_data['score'], 10.8)  # (90/100) * 12 weight
        self.assertEqual(sql_data['weight'], 12)

        # Check Python scores
        python_data = result['details']['python']
        self.assertTrue(python_data['matched'])
        self.assertEqual(python_data['llm_raw_score'], 75)
        self.assertAlmostEqual(python_data['score'], 7.5)  # (75/100) * 10 weight

        # Check totals
        self.assertAlmostEqual(result['total_score'], 18.3)  # 10.8 + 7.5
        self.assertEqual(result['max_possible_score'], 22)  # 12 + 10
        self.assertAlmostEqual(result['percentage'], 83.18, places=1)  # (18.3/22)*100

    def test_score_clamping(self):
        """Test that scores are clamped to 0-100 range."""
        # Mock LLM response with out-of-range scores
        llm_response = {
            'skill_scores': {
                'sql': {'score': 150, 'evidence': 'test', 'justification': 'test'},  # Too high
                'python': {'score': -10, 'evidence': 'test', 'justification': 'test'}  # Too low
            },
            'category_summary': 'test'
        }

        result = self.analyzer._parse_llm_response(llm_response, self.sample_skills)

        # Check that scores are clamped
        self.assertEqual(result['details']['sql']['llm_raw_score'], 100)
        self.assertEqual(result['details']['python']['llm_raw_score'], 0)

    def test_cache_key_generation(self):
        """Test that cache keys are generated consistently."""
        key1 = self.analyzer._get_cache_key(self.sample_cv)
        key2 = self.analyzer._get_cache_key(self.sample_cv)
        key3 = self.analyzer._get_cache_key("Different CV text")

        # Same CV should generate same key
        self.assertEqual(key1, key2)
        # Different CV should generate different key
        self.assertNotEqual(key1, key3)
        # Keys should be hex strings (SHA256)
        self.assertEqual(len(key1), 64)

    def test_extract_keywords_from_evidence(self):
        """Test keyword extraction from evidence text."""
        evidence = "Candidate has 5 years of SQL experience with PostgreSQL"
        keywords = ['sql', 'postgresql', 'mysql', 'database']

        matched = self.analyzer._extract_keywords_from_evidence(evidence, keywords)

        self.assertIn('sql', matched)
        self.assertIn('postgresql', matched)
        self.assertNotIn('mysql', matched)

    @patch('llm_analyzer.Groq')
    def test_api_call_success(self, mock_groq_class):
        """Test successful API call."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            'skill_scores': {
                'sql': {'score': 85, 'evidence': 'test', 'justification': 'test'}
            },
            'category_summary': 'test'
        })

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        # Create analyzer with mocked client
        analyzer = LLMAnalyzer(api_key='test_key', cache_enabled=False)

        # Make API call
        result = analyzer._call_groq_api("Test prompt")

        # Verify result
        self.assertIn('skill_scores', result)
        self.assertIn('category_summary', result)

    @patch('llm_analyzer.Groq')
    def test_api_call_retry_on_error(self, mock_groq_class):
        """Test that API calls retry on error."""
        mock_client = Mock()

        # First call fails, second succeeds
        mock_success = Mock()
        mock_success.choices = [Mock()]
        mock_success.choices[0].message.content = json.dumps({
            'skill_scores': {},
            'category_summary': 'test'
        })

        mock_client.chat.completions.create.side_effect = [
            Exception("API Error"),
            mock_success
        ]

        mock_groq_class.return_value = mock_client

        analyzer = LLMAnalyzer(api_key='test_key', cache_enabled=False, max_retries=3)

        # Should succeed on second attempt
        result = analyzer._call_groq_api("Test prompt")
        self.assertIn('skill_scores', result)

    def test_calculate_summary(self):
        """Test summary calculation matches RequirementsAnalyzer format."""
        # Create mock analysis with multiple categories
        analysis = {
            'required_skills': {
                'details': {
                    'sql': {'matched': True},
                    'python': {'matched': True},
                    'excel': {'matched': False}
                },
                'percentage': 85.0
            },
            'preferred_skills': {
                'details': {
                    'ml': {'matched': True},
                    'cloud': {'matched': False}
                },
                'percentage': 50.0
            },
            'education': {
                'details': {
                    'masters': {'matched': True},
                    'phd': {'matched': False}
                },
                'percentage': 75.0
            },
            'experience': {
                'details': {
                    'data_analyst': {'matched': True}
                },
                'percentage': 100.0
            }
        }

        summary = self.analyzer._calculate_summary(analysis)

        # Check structure
        self.assertIn('total_skills_matched', summary)
        self.assertIn('total_skills_possible', summary)
        self.assertIn('match_rate', summary)
        self.assertIn('required_skills_percentage', summary)
        self.assertIn('preferred_skills_percentage', summary)
        self.assertIn('education_percentage', summary)
        self.assertIn('experience_percentage', summary)

        # Check calculations
        # required: sql(T), python(T), excel(F) = 2
        # preferred: ml(T), cloud(F) = 1
        # education: masters(T), phd(F) = 1
        # experience: data_analyst(T) = 1
        # Total = 2+1+1+1 = 5 matched
        self.assertEqual(summary['total_skills_matched'], 5)
        self.assertEqual(summary['total_skills_possible'], 8)  # 3+2+2+1
        self.assertAlmostEqual(summary['match_rate'], 62.5)  # (5/8)*100

        self.assertEqual(summary['required_skills_percentage'], 85.0)
        self.assertEqual(summary['preferred_skills_percentage'], 50.0)
        self.assertEqual(summary['education_percentage'], 75.0)
        self.assertEqual(summary['experience_percentage'], 100.0)

    def test_backward_compatibility(self):
        """Test that output structure matches RequirementsAnalyzer."""
        llm_response = {
            'skill_scores': {
                'sql': {'score': 85, 'evidence': 'test', 'justification': 'test'}
            },
            'category_summary': 'test'
        }

        result = self.analyzer._parse_llm_response(
            llm_response,
            {'sql': {'keywords': ['sql'], 'weight': 12, 'category': 'data'}}
        )

        # Check all required fields exist (same as RequirementsAnalyzer)
        self.assertIn('details', result)
        self.assertIn('total_score', result)
        self.assertIn('max_possible_score', result)
        self.assertIn('percentage', result)

        # Check skill detail structure
        sql_detail = result['details']['sql']
        self.assertIn('matched', sql_detail)
        self.assertIn('score', sql_detail)
        self.assertIn('weight', sql_detail)
        self.assertIn('matched_keywords', sql_detail)
        self.assertIn('category', sql_detail)

        # Check new fields are added
        self.assertIn('llm_raw_score', sql_detail)
        self.assertIn('evidence', sql_detail)
        self.assertIn('justification', sql_detail)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLLMAnalyzer)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED")
    else:
        print("\n✗ SOME TESTS FAILED")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
