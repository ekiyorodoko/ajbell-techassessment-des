"""
Base PDF processor module.
Handles PDF loading, type detection, and orchestrates text extraction.
"""

import os
import fitz  # PyMuPDF
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from abc import ABC, abstractmethod

from src.schemas.base import DocumentSection


class PDFProcessor:
    """Base class for processing PDF documents."""
    
    def __init__(self, min_text_threshold: int = 100):
        """Initialize the PDF processor.
        Args:
            min_text_threshold: Minimum text length to consider a PDF text-based
        """
        self.min_text_threshold = min_text_threshold
    
    def process_pdf(self, pdf_path: str) -> Dict[str, str]:
        """Process a PDF file and extract text from all pages.
        Args:
            pdf_path: Path to the PDF file   
        Returns:
            Dictionary mapping page numbers to extracted text
        """
        if not os.path.isfile(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        pdf_document = fitz.open(pdf_path)
        is_scanned = self._is_scanned_pdf(pdf_document)
        
        result = {}
        
        # Process each page
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            if is_scanned:
                from .ocr_processor import OCRProcessor
                processor = OCRProcessor()
                text = processor.process_page(page)
            else:
                from .text_processor import TextProcessor
                processor = TextProcessor()
                text = processor.process_page(page)
                
            result[page_num] = text
        
        pdf_document.close()
        return result
    
    def _is_scanned_pdf(self, pdf_document: fitz.Document) -> bool:
        """Determine if a PDF is scanned (image-based) or text-based.
        Args:
            pdf_document: A PyMuPDF document object
        Returns:
            True if the document appears to be scanned, False otherwise
        """
        # Check the first few pages
        pages_to_check = min(3, len(pdf_document))
        total_text = 0
        
        for page_num in range(pages_to_check):
            page = pdf_document[page_num]
            text = page.get_text()
            total_text += len(text)
            
            # If page has reasonable amount of text, likely not scanned
            if len(text) > self.min_text_threshold:
                return False
                
        # If very little text across checked pages, likely scanned
        return total_text < self.min_text_threshold
    
    def identify_sections(self, extracted_text: Dict[str, str]) -> Dict[DocumentSection, List[int]]:
        """Identify which pages contain which document sections.
        
        Args:
            extracted_text: Dictionary mapping page numbers to extracted text
            
        Returns:
            Dictionary mapping document sections to lists of page numbers
        """
        result = {section: [] for section in DocumentSection}
        
        # Look for section markers in each page
        for page_num, text in extracted_text.items():
            text_lower = text.lower()
            
            # Trust registration section
            if any(marker in text_lower for marker in [
                "trust registration", "hmrc unique reference", "urn", "proof of registration"
            ]):
                result[DocumentSection.TRUST_REGISTRATION].append(page_num)
            
            # Check for donor details section
            if any(marker in text_lower for marker in [
                "details of donor", "donor details", "person who made the gift",
                "national insurance number", "permanent residential address"
            ]):
                result[DocumentSection.DONOR_DETAILS].append(page_num)
            
            # Check for trustee details section
            if any(marker in text_lower for marker in [
                "details of trustees", "trustee details", "individual trustee", 
                "first individual trustee", "section c", "nominated contact"
            ]):
                result[DocumentSection.TRUSTEE_DETAILS].append(page_num)
            
            # Beneficiary details section
            if any(marker in text_lower for marker in [
                "beneficiary details", "details of beneficiary", "section e", 
                "named beneficiary", "bare trust"
            ]):
                result[DocumentSection.BENEFICIARY_DETAILS].append(page_num)
            
            # Nominated bank account section
            if any(marker in text_lower for marker in [
                "nominated bank account", "section f", "bank account", 
                "building society account", "cash withdrawals"
            ]):
                result[DocumentSection.NOMINATED_BANK_ACCOUNT].append(page_num)
            
            # Security information section
            if any(marker in text_lower for marker in [
                "username and security", "section g", "security question", 
                "online account", "mother's maiden name", "first school"
            ]):
                result[DocumentSection.SECURITY_INFORMATION].append(page_num)
                
            # Data privacy statement section
            if any(marker in text_lower for marker in [
                "data privacy statement", "privacy policy", "identity verification",
                "fraud prevention", "communication preference", "trustee signature"
            ]):
                result[DocumentSection.DATA_PRIVACY_STATEMENT].append(page_num)
        
        return result