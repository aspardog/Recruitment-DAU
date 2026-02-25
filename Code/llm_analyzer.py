"""
LLM Analyzer Module
Analyzes CVs using Groq's Llama 3.3 70B for deep semantic understanding.
Drop-in replacement for RequirementsAnalyzer with enhanced granular scoring.
"""

import os
import json
import hashlib
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv

from groq import Groq

# Load environment variables from .env file
load_dotenv()

from config import (
    REQUIRED_SKILLS,
    PREFERRED_SKILLS,
    EDUCATION_KEYWORDS,
    EXPERIENCE_KEYWORDS,
    GROQ_MODEL
)

from model_parameters import (
    SYSTEM_MESSAGE,
    ANALYSIS_PROMPT_TEMPLATE,
    LLM_TEMPERATURE as DEFAULT_TEMPERATURE,
    LLM_MAX_TOKENS as DEFAULT_MAX_TOKENS,
    LLM_MAX_RETRIES as DEFAULT_MAX_RETRIES,
    MAX_CV_LENGTH,
    CUSTOM_INSTRUCTIONS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """
    LLM-based CV analyzer using Groq's Llama 3.3 70B.
    Provides semantic understanding, granular 0-100 scoring, and evidence extraction.
    """

    def __init__(self,
                 api_key: Optional[str] = None,
                 cache_enabled: bool = True,
                 max_retries: Optional[int] = None,
                 model: Optional[str] = None,
                 temperature: Optional[float] = None):
        """
        Initialize LLM analyzer.

        Args:
            api_key: Groq API key (reads from GROQ_API_KEY env var if None)
            cache_enabled: Enable CV analysis caching
            max_retries: Max retry attempts for API calls
            model: Groq model to use
            temperature: LLM temperature (lower = more consistent)
        """
        self.api_key = api_key or os.environ.get('GROQ_API_KEY', '')
        if not self.api_key:
            raise ValueError(
                "Groq API key required. Set GROQ_API_KEY environment variable or pass api_key parameter.\n"
                "Get your API key at: https://console.groq.com/keys"
            )

        self.client = Groq(api_key=self.api_key)
        self.model = model if model is not None else GROQ_MODEL
        self.temperature = temperature if temperature is not None else DEFAULT_TEMPERATURE
        self.max_retries = max_retries if max_retries is not None else DEFAULT_MAX_RETRIES
        self.cache_enabled = cache_enabled

        # Load config
        self.required_skills = REQUIRED_SKILLS
        self.preferred_skills = PREFERRED_SKILLS
        self.education_keywords = EDUCATION_KEYWORDS
        self.experience_keywords = EXPERIENCE_KEYWORDS

        # Setup cache directory
        self.cache_dir = Path(".cache/cv_analyses")
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Cache enabled at: {self.cache_dir}")

    def analyze_cv(self, cv_text: str) -> Dict[str, Any]:
        """
        Perform complete LLM-based analysis of a CV.
        Maintains same interface as RequirementsAnalyzer.

        Args:
            cv_text: CV text to analyze

        Returns:
            Dictionary with complete analysis results (same structure as RequirementsAnalyzer)
        """
        # Check cache first
        if self.cache_enabled:
            cache_key = self._get_cache_key(cv_text)
            cached_result = self._load_from_cache(cache_key)
            if cached_result:
                logger.info("Using cached analysis")
                return cached_result

        logger.info("Performing LLM analysis...")

        # Analyze each category
        analysis = {
            'required_skills': self.analyze_skill_category(cv_text, self.required_skills, 'Required Skills'),
            'preferred_skills': self.analyze_skill_category(cv_text, self.preferred_skills, 'Preferred Skills'),
            'education': self.analyze_skill_category(cv_text, self.education_keywords, 'Education'),
            'experience': self.analyze_skill_category(cv_text, self.experience_keywords, 'Experience')
        }

        # Calculate overall statistics
        analysis['summary'] = self._calculate_summary(analysis)

        # Save to cache
        if self.cache_enabled:
            self._save_to_cache(cache_key, analysis)

        return analysis

    def analyze_skill_category(self,
                               cv_text: str,
                               skill_dict: Dict,
                               category_name: str) -> Dict[str, Any]:
        """
        Analyze a category of skills using LLM.

        Args:
            cv_text: CV text to analyze
            skill_dict: Dictionary of skills to check
            category_name: Name of category (for prompt context)

        Returns:
            Dictionary with analysis results (compatible with RequirementsAnalyzer)
        """
        # Build prompt for this category
        prompt = self._build_analysis_prompt(cv_text, skill_dict, category_name)

        # Call Groq API with retry logic
        llm_response = self._call_groq_api(prompt)

        # Parse LLM response into analysis structure with validation
        results = self._parse_llm_response(llm_response, skill_dict, cv_text)

        return results

    def _build_analysis_prompt(self,
                               cv_text: str,
                               skill_dict: Dict,
                               category_name: str) -> str:
        """
        Build structured prompt for LLM analysis using template from model_parameters.

        Args:
            cv_text: CV text
            skill_dict: Skills to evaluate
            category_name: Category name

        Returns:
            Formatted prompt string
        """
        # Truncate CV if too long
        truncated_cv = cv_text[:MAX_CV_LENGTH] if len(cv_text) > MAX_CV_LENGTH else cv_text

        # Build criteria list
        criteria_items = []
        for skill_name, skill_info in skill_dict.items():
            keywords_str = ', '.join(skill_info['keywords'][:5])  # Show first 5 keywords
            description = skill_info.get('description', f"Look for: {keywords_str}")
            criteria_items.append(f"- **{skill_name}** (Weight: {skill_info['weight']}): {description}")

        criteria_text = '\n'.join(criteria_items)

        # Map category name to custom instructions key
        category_key_map = {
            'Required Skills': 'required_skills',
            'Preferred Skills': 'preferred_skills',
            'Education': 'education',
            'Experience': 'experience'
        }
        category_key = category_key_map.get(category_name, 'general')

        # Get custom instructions for this category
        custom_instructions = CUSTOM_INSTRUCTIONS.get(category_key, '')
        if not custom_instructions:
            custom_instructions = CUSTOM_INSTRUCTIONS.get('general', '')

        # Use template from model_parameters
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            category_name=category_name,
            criteria_text=criteria_text,
            truncated_cv=truncated_cv,
            custom_instructions=custom_instructions
        )

        return prompt

    def _call_groq_api(self, prompt: str) -> Dict:
        """
        Make API call to Groq with retry logic.

        Args:
            prompt: Prompt to send

        Returns:
            Parsed JSON response from LLM

        Raises:
            Exception: If API call fails after retries
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_MESSAGE
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=self.temperature,
                    max_tokens=DEFAULT_MAX_TOKENS,
                    response_format={"type": "json_object"}  # Force JSON output
                )

                # Parse JSON response
                content = response.choices[0].message.content
                parsed = json.loads(content)

                return parsed

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to parse LLM response as JSON after {self.max_retries} attempts")
                time.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                logger.error(f"API call error (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff

    def _validate_and_adjust_score(self,
                                   skill_name: str,
                                   skill_info: Dict,
                                   llm_skill_data: Dict,
                                   cv_text: str) -> Dict:
        """
        Validate LLM response quality and adjust score based on evidence strength and recency.

        VALIDATION CHECKS:
        1. Evidence Quality: Score must be supported by evidence
        2. Recency Penalty: Adjust score based on years since last use
        3. Keyword Presence: High scores require keyword mentions

        Args:
            skill_name: Name of the skill being evaluated
            skill_info: Skill configuration from config.py
            llm_skill_data: LLM's evaluation for this skill
            cv_text: Full CV text for cross-validation

        Returns:
            Dict with validated and adjusted score data
        """
        original_score = llm_skill_data.get('score', 0)
        evidence = llm_skill_data.get('evidence', '')
        justification = llm_skill_data.get('justification', '')
        recency_years = llm_skill_data.get('recency_years', None)

        adjusted_score = original_score
        validation_notes = []

        # CHECK 1: Evidence Quality Validation
        # Very high scores (85+) require skill keyword in evidence or CV
        if adjusted_score >= 85:
            skill_keywords = skill_info.get('keywords', [])
            evidence_lower = evidence.lower()
            cv_lower = cv_text.lower()

            # Check if ANY keyword appears in evidence
            keyword_in_evidence = any(kw.lower() in evidence_lower for kw in skill_keywords[:5])
            keyword_in_cv = any(kw.lower() in cv_lower for kw in skill_keywords[:3])

            if not keyword_in_evidence and not keyword_in_cv:
                # No evidence found - light penalty
                adjusted_score = max(adjusted_score - 10, 50)
                validation_notes.append("No keyword evidence found - score reduced")
                logger.warning(f"  ⚠ {skill_name}: Score {original_score}→{adjusted_score} (no evidence)")
            elif not keyword_in_evidence and keyword_in_cv:
                # Keyword in CV but not in evidence - minimal penalty
                adjusted_score = max(adjusted_score - 5, 60)
                validation_notes.append("Weak evidence - score reduced")
                logger.debug(f"  ⚠ {skill_name}: Score {original_score}→{adjusted_score} (weak evidence)")

        # CHECK 2: Recency-Based Adjustment
        # Apply minimal time decay to scores based on recency_years
        if recency_years is not None and recency_years > 0:
            if recency_years <= 5:
                # Recent (0-5 years): no penalty
                recency_multiplier = 1.0
            elif recency_years <= 8:
                # Moderate age (5-8 years): 10% penalty
                recency_multiplier = 0.90
                validation_notes.append(f"Moderate age ({recency_years:.1f}y)")
            else:
                # Old (8+ years): 20% penalty
                recency_multiplier = 0.80
                validation_notes.append(f"Older experience ({recency_years:.1f}y)")

            if recency_multiplier < 1.0:
                before_recency = adjusted_score
                adjusted_score = adjusted_score * recency_multiplier
                logger.info(f"  ⏱ {skill_name}: Score {before_recency:.0f}→{adjusted_score:.0f} "
                          f"(recency: {recency_years:.1f} years old, {recency_multiplier:.0%} weight)")

        # CHECK 3: Vague Evidence Detection
        # Very minimal penalty for vague evidence
        vague_phrases = ['familiar with', 'exposure to', 'basic knowledge',
                        'some experience', 'aware of', 'introduced to']
        evidence_lower = evidence.lower()

        if adjusted_score >= 75 and any(phrase in evidence_lower for phrase in vague_phrases):
            adjusted_score = max(adjusted_score - 5, 50)
            validation_notes.append("Vague evidence detected")
            logger.debug(f"  ⚠ {skill_name}: Vague evidence - score reduced to {adjusted_score}")

        # CHECK 4: Score-Evidence Consistency
        # Only apply to very high scores (90+) with no evidence
        if adjusted_score >= 90 and len(evidence) < 10:
            adjusted_score = max(adjusted_score - 5, 80)
            validation_notes.append("Insufficient evidence for very high score")
            logger.debug(f"  ⚠ {skill_name}: Insufficient evidence for score 90+ - reduced to {adjusted_score}")

        return {
            'original_score': original_score,
            'adjusted_score': round(adjusted_score, 1),
            'evidence': evidence,
            'justification': justification,
            'recency_years': recency_years,
            'validation_notes': validation_notes
        }

    def _parse_llm_response(self, llm_response: Dict, skill_dict: Dict, cv_text: str = "") -> Dict[str, Any]:
        """
        Parse LLM JSON response into analysis dict structure with validation.
        Enhanced with quality validation and recency adjustments.

        Args:
            llm_response: JSON response from LLM
            skill_dict: Original skill dictionary with weights
            cv_text: Full CV text for validation

        Returns:
            Analysis dict compatible with RequirementsAnalyzer
        """
        skill_scores = llm_response.get('skill_scores', {})

        results = {}
        total_achieved_score = 0
        total_possible_score = 0

        for skill_name, skill_info in skill_dict.items():
            weight = skill_info['weight']
            total_possible_score += weight

            # Get LLM score (0-100) for this skill
            llm_skill_data = skill_scores.get(skill_name, {})

            # VALIDATE AND ADJUST SCORE (NEW)
            validated_data = self._validate_and_adjust_score(
                skill_name, skill_info, llm_skill_data, cv_text
            )

            llm_raw_score = validated_data['adjusted_score']

            # Clamp score to 0-100 range
            llm_raw_score = max(0, min(100, llm_raw_score))

            # Convert 0-100 score to weighted score
            weighted_score = (llm_raw_score / 100) * weight
            total_achieved_score += weighted_score

            # Extract evidence and justification
            evidence = validated_data['evidence']
            justification = validated_data['justification']

            # Approximate matched keywords from evidence (for compatibility)
            matched_keywords = self._extract_keywords_from_evidence(
                evidence,
                skill_info['keywords']
            )

            results[skill_name] = {
                'matched': llm_raw_score > 0,
                'score': weighted_score,
                'weight': weight,
                'llm_raw_score': llm_raw_score,
                'llm_original_score': validated_data['original_score'],  # NEW: track original
                'evidence': evidence,
                'justification': justification,
                'recency_years': validated_data.get('recency_years'),  # NEW
                'validation_notes': validated_data.get('validation_notes', []),  # NEW
                'matched_keywords': matched_keywords,
                'category': skill_info['category']
            }

        # Calculate percentage
        percentage = (total_achieved_score / total_possible_score * 100) if total_possible_score > 0 else 0

        return {
            'details': results,
            'total_score': total_achieved_score,
            'max_possible_score': total_possible_score,
            'percentage': percentage
        }

    def _extract_keywords_from_evidence(self, evidence: str, keywords: List[str]) -> List[str]:
        """
        Extract matched keywords from evidence text (for compatibility).

        Args:
            evidence: Evidence text from LLM
            keywords: List of possible keywords

        Returns:
            List of keywords found in evidence
        """
        evidence_lower = evidence.lower()
        matched = []

        for keyword in keywords[:5]:  # Check first 5 keywords
            if keyword.lower() in evidence_lower:
                matched.append(keyword)

        return matched

    def _calculate_summary(self, analysis: Dict) -> Dict[str, Any]:
        """
        Calculate summary statistics from analysis.
        Same logic as RequirementsAnalyzer for compatibility.

        Args:
            analysis: Analysis results

        Returns:
            Summary statistics
        """
        total_matched_skills = 0
        total_possible_skills = 0

        for category in ['required_skills', 'preferred_skills', 'education', 'experience']:
            category_data = analysis[category]
            matched = sum(1 for skill in category_data['details'].values() if skill['matched'])
            total = len(category_data['details'])
            total_matched_skills += matched
            total_possible_skills += total

        return {
            'total_skills_matched': total_matched_skills,
            'total_skills_possible': total_possible_skills,
            'match_rate': (total_matched_skills / total_possible_skills * 100) if total_possible_skills > 0 else 0,
            'required_skills_percentage': analysis['required_skills']['percentage'],
            'preferred_skills_percentage': analysis['preferred_skills']['percentage'],
            'education_percentage': analysis['education']['percentage'],
            'experience_percentage': analysis['experience']['percentage']
        }

    def _get_cache_key(self, cv_text: str) -> str:
        """
        Generate cache key from CV text hash.

        Args:
            cv_text: CV text

        Returns:
            SHA256 hash of CV text
        """
        return hashlib.sha256(cv_text.encode('utf-8')).hexdigest()

    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """
        Load cached analysis if available and not expired.

        Args:
            cache_key: Cache key (hash)

        Returns:
            Cached analysis or None
        """
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)

            # Check expiry (30 days default)
            cached_time = datetime.fromisoformat(cached_data.get('timestamp', '2000-01-01'))
            if datetime.now() - cached_time > timedelta(days=30):
                logger.info("Cache expired, will re-analyze")
                return None

            return cached_data.get('analysis')

        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None

    def _save_to_cache(self, cache_key: str, analysis: Dict):
        """
        Save analysis to cache.

        Args:
            cache_key: Cache key (hash)
            analysis: Analysis results
        """
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'analysis': analysis
            }

            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            logger.debug(f"Saved analysis to cache: {cache_key}")

        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
