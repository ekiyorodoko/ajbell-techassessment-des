"""
LLM-based extractor module.
Uses language models to extract information from text.
"""

import os
from typing import Dict, Any, Optional, Union

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models.chat_models import BaseChatModel

from ..schemas.base import DocumentSection
from .base_extractor import BaseExtractor
from ..utils.llm_utils import get_llm


class LLMExtractor(BaseExtractor):
    """Extract information using a language model."""
    
    def __init__(
        self, 
        document_section: DocumentSection,
        llm_provider: str = "local",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.0
    ):
        """Initialize the LLM extractor.
        
        Args:
            document_section: The document section this extractor is responsible for
            llm_provider: LLM provider to use (local, openai, google)
            model_name: Model name for the chosen provider
            api_key: API key for the chosen provider
            temperature: Temperature setting for the LLM
        """
        super().__init__(document_section)
        
        self.llm_provider = llm_provider
        self.model_name = model_name
        self.api_key = api_key
        self.temperature = temperature
        
        # Set up LLM
        self.llm = get_llm(llm_provider, model_name, api_key, temperature)
        
        # Set up output parser
        self.parser = JsonOutputParser(pydantic_object=self.schema_class)
        
        # Configure prompt based on document section
        self.prompt = self._configure_prompt()
    
    def _configure_prompt(self) -> ChatPromptTemplate:
        """Configure the prompt based on the document section.
        
        Returns:
            ChatPromptTemplate for the extractor
        """
        base_prompt = """
        You are an expert document analyzer specialized in extracting specific information from {document_type} documents.
        
        Below is text extracted from a document. Please extract the following information:
        
        {extraction_instructions}
        
        Text from document:
        {text}
        
        Based on the text, extract the requested information. If you cannot find certain information, do not estimate information.
        
        {format_instructions}
        """
        
        # Section-specific configurations
        if self.document_section == DocumentSection.TRUST_REGISTRATION:
            document_type = "trust registration"
            extraction_instructions = """
            1. HMRC unique reference number (URN) for the trust
            2. Whether proof of registration is attached or not
            """
        elif self.document_section == DocumentSection.DONOR_DETAILS:
            document_type = "donor details"
            extraction_instructions = """
            1. Title of the donor (Dr, Mr, Mrs, Miss, Ms, or Other)
            2. Surname of the donor
            3. Forenames of the donor
            4. Date of birth of the donor (format: DD/MM/YYYY)
            5. National insurance number of the donor
            6. Permanent residential address of the donor
            7. Postcode of the donor's address
            8. Country of residence of the donor
            9. Country of nationality of the donor
            10. Whether the donor is deceased (if mentioned that "the donor has passed away" or similar)
            """
        elif self.document_section == DocumentSection.TRUSTEE_DETAILS:
            document_type = "trustee details"
            extraction_instructions = """
            1. Title of the trustee (Dr, Mr, Mrs, Miss, Ms, or Other)
            2. Surname of the trustee
            3. Forenames of the trustee
            4. Date of birth of the trustee (format: DD/MM/YYYY)
            5. National insurance number of the trustee
            6. Permanent residential address of the trustee
            7. Postcode of the trustee's address
            8. Country of the trustee
            9. Daytime telephone number of the trustee
            10. Email address of the trustee
            11. Whether the trustee has an existing AJ Bell Account (yes/no)
            12. The AJ Bell account number if it exists
            13. Whether the trustee was born in the UK (yes/no)
            14. Whether the trustee is solely a UK citizen, solely a UK national, and solely resident in the UK for tax purposes (yes/no)
            15. For non-UK details (if applicable):
                a. Country of birth for non-UK born trustees
                b. Nationality of the trustee
                c. Identification number for non-UK trustees
                d. Type of identification number provided
                e. Passport number if no other identification is provided
                f. Primary country of residence for tax purposes
                g. Secondary country of residence for tax purposes
                h. Primary country of citizenship
                i. Secondary country of citizenship
            """
        elif self.document_section == DocumentSection.BENEFICIARY_DETAILS:
            document_type = "beneficiary details"
            extraction_instructions = """
            1. Title of the beneficiary (Dr, Mr, Mrs, Miss, Ms, Other)
            2. Surname of the beneficiary
            3. Forenames of the beneficiary
            4. Date of birth
            5. National Insurance number (if available)
            6. Permanent residential address
            7. Postcode
            8. Country
            9. Telephone number (may be labeled as "Daytime telephone number")
            10. Email address
            11. Whether the beneficiary was born in the UK (born_in_uk)
            12. If not born in the UK, extract these additional details as "not_born_in_uk":
               a. Country of birth
               b. Nationality
               c. ID number
               d. Type of number
               e. Passport number
               f. Primary country of residence for tax purposes
               g. Secondary country of residence for tax purposes (if applicable)
               h. Country of citizenship
               i. Second country of citizenship (if applicable)
            """
        elif self.document_section == DocumentSection.NOMINATED_BANK_ACCOUNT:
            document_type = "nominated bank account"
            extraction_instructions = """
            1. Account holder's name
            2. Bank/building society account number
            3. Sort code
            """
        elif self.document_section == DocumentSection.SECURITY_INFORMATION:
            document_type = "security information"
            extraction_instructions = """
            1. Username for online account access
            2. Security questions:
               a. Mother's maiden name
               b. First school name (name of first school attended)
            """
        elif self.document_section == DocumentSection.DATA_PRIVACY_STATEMENT:
            document_type = "data privacy statement"
            extraction_instructions = """
            1. Identity verification consent (boolean: true/false)
            2. Fraud prevention checks consent (boolean: true/false)
            3. Communication preference consent - whether they would like to receive communications (boolean: true/false)
            4. Trustee signatures (a list of signatures):
               For each trustee signature, extract:
               a. Name of the trustee
               b. Date of signature
               c. Whether the signature is present (can just be "Present" if a signature exists)
            """
        else:
            raise ValueError(f"Unsupported document section: {self.document_section}")
        
        return ChatPromptTemplate.from_template(base_prompt).partial(
            document_type=document_type,
            extraction_instructions=extraction_instructions,
            format_instructions=self.parser.get_format_instructions()
        )
    
    def extract(self, text: str) -> Dict[str, Any]:
        """Extract information from text using LLM.
        
        Args:
            text: Text to extract information from
            
        Returns:
            Dictionary with extracted information
        """
        # Set up the chain
        chain = self.prompt | self.llm | self.parser
        
        # Run the chain
        try:
            result = chain.invoke({"text": text})
            
            # Special handling for trustee details to ensure proper nested structure
            if self.document_section == DocumentSection.TRUSTEE_DETAILS:
                # Process non-UK details
                self._process_non_uk_details_structure(result)
                
            return result
        except Exception as e:
            # Fall back to regex extractor in case of failure
            from .regex_extractor import RegexExtractor
            print(f"LLM extraction failed: {str(e)}. Falling back to regex extraction.")
            fallback = RegexExtractor(self.document_section)
            return fallback.extract(text)
            
    def _process_non_uk_details_structure(self, result: Dict[str, Any]) -> None:
        """Process non-UK details to ensure proper nested structure.
        
        Args:
            result: Extraction result to be modified in-place
        """
        # Only process if this is trustee details
        if self.document_section != DocumentSection.TRUSTEE_DETAILS:
            return
            
        # If the user is a UK citizen, non_uk_details should be None
        if result.get("solely_uk_citizen") == True:
            result["not_uk_details"] = None
            return
            
        # Check for flat structure non-UK fields that should be nested
        non_uk_fields = [
            "country_of_birth", "nationality", "id_number", "type_of_number",
            "passport_number", "primary_residence", "secondary_residence",
            "primary_citizenship", "secondary_citizenship"
        ]
        
        # Collect non-UK fields
        non_uk_details = {}
        for field in non_uk_fields:
            if field in result:
                non_uk_details[field] = result.pop(field)
        
        # Create or update not_uk_details
        if non_uk_details:
            if "not_uk_details" in result and isinstance(result["not_uk_details"], dict):
                result["not_uk_details"].update(non_uk_details)
            else:
                result["not_uk_details"] = non_uk_details
        elif not result.get("not_uk_details"):
            result["not_uk_details"] = None