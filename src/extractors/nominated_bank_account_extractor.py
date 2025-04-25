"""
Nominated Bank Account extractor module.
Specialized extractor for nominated bank account details.
"""

from typing import Dict, Any, Optional
import re

from ..schemas.base import DocumentSection
from .llm_extractor import LLMExtractor


class NominatedBankAccountExtractor(LLMExtractor):
    """Extract nominated bank account details from text."""
    
    def __init__(
        self,
        llm_provider: str = "local",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.0
    ):
        """Initialize the nominated bank account extractor.
        
        Args:
            llm_provider: LLM provider to use (local, openai, google)
            model_name: Model name for the chosen provider
            api_key: API key for the chosen provider
            temperature: Temperature setting for the LLM
        """
        super().__init__(
            document_section=DocumentSection.NOMINATED_BANK_ACCOUNT,
            llm_provider=llm_provider,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature
        )
    
    def extract(self, text: str) -> Dict[str, Any]:
        """Extract nominated bank account details from text.
        
        Args:
            text: Text to extract information from
            
        Returns:
            Dictionary with extracted bank account details
        """
        # Call the parent class implementation
        result = super().extract(text)
        
        # Additional post-processing specific to bank account details
        self._clean_account_number(result)
        self._clean_sort_code(result)
        
        return result
    
    def _clean_account_number(self, result: Dict[str, Any]) -> None:
        """Clean up the account number format.
        
        Args:
            result: Extracted result dictionary to modify in-place
        """
        if not result.get("account_number"):
            return
            
        # Remove spaces and other non-numeric characters
        account_number = result["account_number"]
        account_number = re.sub(r'[^0-9]', '', account_number)
        
        result["account_number"] = account_number
    
    def _clean_sort_code(self, result: Dict[str, Any]) -> None:
        """Clean up the sort code format.
        
        Args:
            result: Extracted result dictionary to modify in-place
        """
        if not result.get("sort_code"):
            return
            
        # Extract digits only, then format as XX-XX-XX
        sort_code = result["sort_code"]
        digits = re.sub(r'[^0-9]', '', sort_code)
        
        # Format as XX-XX-XX if 6 digits
        if len(digits) == 6:
            formatted_sort_code = f"{digits[0:2]}-{digits[2:4]}-{digits[4:6]}"
            result["sort_code"] = formatted_sort_code
        else:
            # Keep original if not 6 digits
            result["sort_code"] = digits