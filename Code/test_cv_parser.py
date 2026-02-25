"""
Unit Tests for CV Parser Module
Tests PDF parsing and text extraction functionality.
"""

import unittest
import os
from pathlib import Path
from cv_parser import CVParser


class TestCVParser(unittest.TestCase):
    """Test cases for CVParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CVParser()

    def test_parser_initialization(self):
        """Test that parser initializes correctly."""
        self.assertIsInstance(self.parser, CVParser)

    def test_both_backends_available(self):
        """Verify at least one PDF backend (pdfplumber or PyPDF2) is available."""
        import importlib
        pdfplumber_ok = importlib.util.find_spec("pdfplumber") is not None
        pypdf2_ok = importlib.util.find_spec("PyPDF2") is not None
        self.assertTrue(pdfplumber_ok or pypdf2_ok,
                        "Neither pdfplumber nor PyPDF2 is installed. Run: pip install pdfplumber")

    def test_extract_text_from_nonexistent_file(self):
        """Test handling of non-existent PDF file."""
        result = self.parser.extract_text_from_pdf("nonexistent_file.pdf")
        self.assertEqual(result, "")

    def test_parse_cv_directory_nonexistent(self):
        """Test parsing non-existent directory."""
        result = self.parser.parse_cv_directory("nonexistent_directory")
        self.assertEqual(result, {})

    def test_get_cv_metadata_nonexistent(self):
        """Test metadata extraction for non-existent file."""
        metadata = self.parser.get_cv_metadata("nonexistent.pdf")
        self.assertEqual(metadata['size'], 0)
        self.assertEqual(metadata['filename'], "nonexistent.pdf")

    def test_get_cv_metadata_structure(self):
        """Test that metadata has correct structure."""
        metadata = self.parser.get_cv_metadata("test.pdf")
        self.assertIn('filename', metadata)
        self.assertIn('path', metadata)
        self.assertIn('size', metadata)


class TestCVParserWithRealFiles(unittest.TestCase):
    """Test cases for CVParser with real PDF files."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CVParser()
        self.project_root = Path(__file__).parent.parent
        self.candidates_dir = self.project_root / "Data Analyst"

    def test_parse_existing_directory(self):
        """Test parsing actual candidates directory — verifies count and non-empty results."""
        if not self.candidates_dir.exists():
            self.skipTest("Candidates directory not found — skipping real-file tests")
        result = self.parser.parse_cv_directory(str(self.candidates_dir))
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0, "No PDFs were parsed — check the Data Analyst/ directory")
        empty_files = [path for path, text in result.items() if not text.strip()]
        if empty_files:
            print(f"\n  ⚠️  WARNING: {len(empty_files)} PDF(s) returned empty text:")
            for f in empty_files:
                print(f"     - {f}")
        print(f"\n  ✓ Parsed {len(result)} PDFs ({len(empty_files)} empty)")

    def test_extract_text_from_actual_pdf(self):
        """Test text quality from real PDFs: length, readability, and no garbled encoding."""
        if not self.candidates_dir.exists():
            self.skipTest("Candidates directory not found — skipping real-file tests")
        pdf_files = list(self.candidates_dir.glob("*.pdf"))
        if not pdf_files:
            self.skipTest("No PDF files found in candidates directory")

        failures = []
        for pdf_file in pdf_files:
            text = self.parser.extract_text_from_pdf(str(pdf_file))

            # Must extract some text
            if not text or len(text.strip()) < 100:
                failures.append(f"{pdf_file.name}: too short ({len(text)} chars) — possible scan/image PDF")
                continue

            # Must contain common Latin characters (catches garbled encoding)
            ascii_ratio = sum(c.isascii() for c in text) / len(text)
            if ascii_ratio < 0.70:
                failures.append(f"{pdf_file.name}: {ascii_ratio:.0%} ASCII — possible encoding issue")
                continue

            print(f"\n  ✓ {pdf_file.name}: {len(text)} chars, {ascii_ratio:.0%} ASCII")

        if failures:
            print("\n  ⚠️  EXTRACTION ISSUES DETECTED:")
            for f in failures:
                print(f"     - {f}")
            self.fail(f"{len(failures)} PDF(s) failed quality checks (see output above)")


def run_tests():
    """Run all CV parser tests."""
    print("\n" + "="*70)
    print("RUNNING CV PARSER TESTS")
    print("="*70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestCVParser))
    suite.addTests(loader.loadTestsFromTestCase(TestCVParserWithRealFiles))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    run_tests()
