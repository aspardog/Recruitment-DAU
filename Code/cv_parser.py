"""
CV Parser Module
Extracts text content from PDF resumes/CVs for analysis.
Uses pdfplumber for robust text extraction with fallback to PyPDF2.
"""

import os
from pathlib import Path
from typing import Dict, Optional
import logging

# Try to import pdfplumber (preferred)
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("Warning: pdfplumber not available, falling back to PyPDF2")

# Fallback to PyPDF2
import PyPDF2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CVParser:
    """Parser for extracting text from CV PDF files."""

    def __init__(self, use_pdfplumber: bool = True):
        """
        Initialize the CV parser.

        Args:
            use_pdfplumber: Use pdfplumber if available (more robust)
        """
        self.use_pdfplumber = use_pdfplumber and PDFPLUMBER_AVAILABLE
        if self.use_pdfplumber:
            logger.info("Using pdfplumber for PDF extraction (robust mode)")
        else:
            logger.info("Using PyPDF2 for PDF extraction (fallback mode)")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        Tries pdfplumber first (if available), falls back to PyPDF2.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text as a string
        """
        # Try pdfplumber first (more robust)
        if self.use_pdfplumber:
            try:
                text = self._extract_with_pdfplumber(pdf_path)
                if text and len(text.strip()) > 50:  # Valid extraction
                    return text.strip()
                else:
                    logger.warning(f"pdfplumber extracted little text from {pdf_path}, trying PyPDF2")
            except Exception as e:
                logger.warning(f"pdfplumber failed for {pdf_path}: {e}, trying PyPDF2")

        # Fallback to PyPDF2
        try:
            text = self._extract_with_pypdf2(pdf_path)
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """
        Extract text using pdfplumber (more robust, better formatting).

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """
        Extract text using PyPDF2 (fallback method).

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def parse_cv_directory(self, directory_path: str) -> Dict[str, str]:
        """
        Parse all PDF files in a directory.

        Args:
            directory_path: Path to directory containing CV PDFs

        Returns:
            Dictionary mapping filename to extracted text
        """
        cv_texts = {}
        directory = Path(directory_path)

        if not directory.exists():
            print(f"Directory {directory_path} does not exist")
            return cv_texts

        # Find all PDF files
        pdf_files = list(directory.glob("**/*.pdf"))

        if not pdf_files:
            print(f"No PDF files found in {directory_path}")
            return cv_texts

        print(f"Found {len(pdf_files)} PDF files to process")

        for pdf_file in pdf_files:
            filename = pdf_file.name
            text = self.extract_text_from_pdf(str(pdf_file))
            if text:
                cv_texts[str(pdf_file)] = text
                print(f"Successfully parsed: {filename}")
            else:
                print(f"Warning: No text extracted from {filename}")

        return cv_texts

    def get_cv_metadata(self, cv_path: str) -> Dict[str, str]:
        """
        Extract basic metadata from CV file.

        Args:
            cv_path: Path to CV PDF file

        Returns:
            Dictionary with metadata (filename, path, size)
        """
        path = Path(cv_path)
        return {
            'filename': path.name,
            'path': str(path),
            'size': path.stat().st_size if path.exists() else 0
        }
