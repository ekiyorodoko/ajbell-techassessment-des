
"""
Trust registration extractor module.
Specialized extractor for trust registration details.
"""

from typing import Dict, Any, Optional

from ..schemas.base import DocumentSection
from .llm_extractor import LLMExtractor


class TrustExtractor(LLMExtractor):
    """Extract trust registration details from text."""
    
    def __init__(
        self,
        llm_provider: str = "local",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.0
    ):
        """Initialize the trust extractor.
        
        Args:
            llm_provider: LLM provider to use (local, openai, google)
            model_name: Model name for the chosen provider
            api_key: API key for the chosen provider
            temperature: Temperature setting for the LLM
        """
        super().__init__(
            document_section=DocumentSection.TRUST_REGISTRATION,
            llm_provider=llm_provider,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature
        )
    
    def extract(self, text: str) -> Dict[str, Any]:
        """Extract trust registration details from text.
        
        This method can be extended to add trust-specific preprocessing
        or post-processing logic.
        
        Args:
            text: Text to extract information from
            
        Returns:
            Dictionary with extracted trust registration details
        """
        # Call the parent class implementation
        result = super().extract(text)
    
        return result
