"""
PDF Document Extractor Application.
Extracts structured information from PDF documents.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

from src.extractors.trustee_extractor import TrusteeExtractor
from src.extractors.beneficiary_extractor import BeneficiaryExtractor
from src.extractors.nominated_bank_account_extractor import NominatedBankAccountExtractor
from src.extractors.security_information_extractor import SecurityInformationExtractor
from src.extractors.data_privacy_statement_extractor import DataPrivacyStatementExtractor
from src.schemas import DocumentSection, SchemaRegistry
from src.processors import PDFProcessor
from src.extractors import TrustExtractor, DonorExtractor
from src.utils import (
    save_json, 
    generate_output_path, 
    get_available_providers
)


def process_document(
    pdf_path: str,
    sections: Optional[List[str]] = None,
    llm_provider: str = "local",
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.0
) -> Dict[str, Any]:
    """Process a PDF document and extract information.
    
    Args:
        pdf_path: Path to the PDF file
        sections: List of section names to extract (None for all)
        llm_provider: LLM provider to use (local, openai, google)
        model_name: Model name for the chosen provider
        api_key: API key for the chosen provider
        temperature: Temperature setting for the LLM
        
    Returns:
        Dictionary with extracted information
    """
    # Check if the file exists
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Process the PDF to extract text
    pdf_processor = PDFProcessor()
    extracted_text = pdf_processor.process_pdf(pdf_path)
    
    # Identify sections in the document
    identified_sections = pdf_processor.identify_sections(extracted_text)
    
    # Determine which sections to process
    if sections:
        # Convert string section names to DocumentSection enum
        sections_to_process = [
            section for section in DocumentSection 
            if section.value in sections
        ]
    else:
        # Process all sections found in the document
        sections_to_process = [
            section for section, pages in identified_sections.items() 
            if pages
        ]
    
    if not sections_to_process:
        print(f"No relevant sections found in {pdf_path}")
        return {}
    
    # Extract information from each section
    results = {}
    
    for section in sections_to_process:
        # Get pages for this section
        pages = identified_sections.get(section, [])
        if not pages:
            continue
            
        # Combine text from all pages for this section
        section_text = " ".join(extracted_text[page] for page in pages)
        
        # Select appropriate extractor for the section
        if section == DocumentSection.TRUST_REGISTRATION:
            extractor = TrustExtractor(
                llm_provider=llm_provider,
                model_name=model_name,
                api_key=api_key,
                temperature=temperature
            )
        elif section == DocumentSection.DONOR_DETAILS:
            extractor = DonorExtractor(
                llm_provider=llm_provider,
                model_name=model_name,
                api_key=api_key,
                temperature=temperature
            )
        elif section == DocumentSection.TRUSTEE_DETAILS:
            extractor = TrusteeExtractor(
                llm_provider=llm_provider,
                model_name=model_name,
                api_key=api_key,
                temperature=temperature
            )
        elif section == DocumentSection.BENEFICIARY_DETAILS:
            extractor = BeneficiaryExtractor(
                llm_provider=llm_provider,
                model_name=model_name,
                api_key=api_key,
                temperature=temperature
            )
        elif section == DocumentSection.NOMINATED_BANK_ACCOUNT:
            extractor = NominatedBankAccountExtractor(
                llm_provider=llm_provider,
                model_name=model_name,
                api_key=api_key,
                temperature=temperature
            )
        elif section == DocumentSection.SECURITY_INFORMATION:
            extractor = SecurityInformationExtractor(
                llm_provider=llm_provider,
                model_name=model_name,
                api_key=api_key,
                temperature=temperature
            )
        elif section == DocumentSection.DATA_PRIVACY_STATEMENT:
            extractor = DataPrivacyStatementExtractor(
                llm_provider=llm_provider,
                model_name=model_name,
                api_key=api_key,
                temperature=temperature
            )
        else:
            print(f"No extractor available for section: {section}")
            continue
        
        # Extract information from the section
        print(f"Extracting {section.value} information...")
        section_result = extractor.extract(section_text)
        
        # Store the result
        results[section.value] = section_result
    
    return results


def main():
    """Main entry point for the application."""
    load_dotenv()
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Extract structured information from PDF documents",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Input file arguments
    parser.add_argument(
        "pdf_path", 
        help="Path to the PDF document or directory containing PDF documents"
    )
    
    # Output arguments
    parser.add_argument(
        "--output", "-o", 
        help="Output JSON file path (default: same as input with .json extension)"
    )
    
    # Processing options
    parser.add_argument(
        "--sections", "-s",
        nargs="+",
        choices=[section.value for section in DocumentSection],
        help="Specific sections to extract (default: all detected sections)"
    )
    
    # LLM options
    providers = get_available_providers()
    parser.add_argument(
        "--llm",
        choices=list(providers.keys()),
        default="local", 
        help="LLM provider to use"
    )
    
    parser.add_argument(
        "--model",
        help="Model name for the chosen provider"
    )
    
    parser.add_argument(
        "--api-key",
        help="API key for the chosen provider"
    )
    
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Temperature setting for the LLM (0.0-1.0)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        result = process_document(
            pdf_path=args.pdf_path,
            sections=args.sections,
            llm_provider=args.llm,
            model_name=args.model,
            api_key=args.api_key,
            temperature=args.temperature
        )
        
        # Determine output path
        if args.output:
            output_path = args.output
        else:
            output_path = generate_output_path(args.pdf_path)
        
        # Save result
        save_json(result, output_path)
        print(f"Results saved to {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())