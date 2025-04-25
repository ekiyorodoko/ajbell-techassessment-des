"""
Text processor module.
Handles text extraction from text-based PDF pages.
"""

import fitz  # PyMuPDF
import re


class TextProcessor:
    """Process text-based PDF pages."""
    
    def __init__(self, clean_text: bool = True):
        """Initialize the text processor.
        Args:
            clean_text: Whether to clean extracted text
        """
        self.clean_text = clean_text
    
    def process_page(self, page: fitz.Page) -> str:
        """Process a text-based PDF page.
        Args:
            page: A PyMuPDF page object  
        Returns:
            Extracted text from the page
        """
        # Extract text from the page
        text = page.get_text()
        
        if self.clean_text:
            text = self._clean_text(text)
        
        return text
    
    def _clean_text(self, text: str) -> str:
        """Clean extracted text to improve parsing quality.
        Args:
            text: Raw extracted text
        Returns:
            Cleaned text
        """
        # Replace multiple newlines with a single one
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Clean up common OCR/extraction artifacts
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
        
        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text