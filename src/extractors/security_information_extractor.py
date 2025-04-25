"""
Security Information extractor module.
Specialized extractor for security information details.
"""

from typing import Dict, Any, Optional
import re

from ..schemas.base import DocumentSection
from ..schemas.security_information import SecurityQuestions
from .llm_extractor import LLMExtractor


class SecurityInformationExtractor(LLMExtractor):
    """Extract security information details from text."""
    
    def __init__(
        self,
        llm_provider: str = "local",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.0
    ):
        """Initialize the security information extractor.
        
        Args:
            llm_provider: LLM provider to use (local, openai, google)
            model_name: Model name for the chosen provider
            api_key: API key for the chosen provider
            temperature: Temperature setting for the LLM
        """
        super().__init__(
            document_section=DocumentSection.SECURITY_INFORMATION,
            llm_provider=llm_provider,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature
        )
    
    def extract(self, text: str) -> Dict[str, Any]:
        """Extract security information details from text.
        
        Args:
            text: Text to extract information from
            
        Returns:
            Dictionary with extracted security information
        """
        # Call the parent class implementation
        result = super().extract(text)
        
        # Process security questions structure
        self._process_security_questions(result)
        
        return result
    
    def _process_security_questions(self, result: Dict[str, Any]) -> None:
        """Process security questions to ensure proper nested structure.
        
        Args:
            result: Extracted result dictionary to modify in-place
        """
        # Check if security_questions is already a dictionary
        if not result.get("security_questions") or not isinstance(result.get("security_questions"), dict):
            # Check for flat structure security question fields
            security_question_fields = ["mother_maiden_name", "first_school_name"]
            
            # Collect security question fields
            security_questions = {}
            for field in security_question_fields:
                if field in result:
                    security_questions[field] = result.pop(field)
            
            # Create security_questions structure if any fields were found
            if security_questions:
                result["security_questions"] = security_questions