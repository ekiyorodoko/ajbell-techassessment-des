"""
Data Privacy Statement extractor module.
Specialized extractor for data privacy statement details.
"""

from typing import Dict, Any, Optional, List
import re
import datetime

from ..schemas.base import DocumentSection
from ..schemas.data_privacy_statement import TrusteeSignature
from .llm_extractor import LLMExtractor


class DataPrivacyStatementExtractor(LLMExtractor):
    """Extract data privacy statement details from text."""
    
    def __init__(
        self,
        llm_provider: str = "local",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.0
    ):
        super().__init__(
            document_section=DocumentSection.DATA_PRIVACY_STATEMENT,
            llm_provider=llm_provider,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature
        )
    
    def extract(self, text: str) -> Dict[str, Any]:
        """Extract data privacy statement details from text.
        
        Args:
            text: Text to extract information from
            
        Returns:
            Dictionary with extracted data privacy statement details
        """
        # Store the original text for reference
        self._original_text = text
        
        # Call the parent class implementation
        result = super().extract(text)
        
        # Additional post-processing
        self._process_trustee_signatures_from_flat_structure(result)
        self._clean_boolean_fields(result)
        
        return result
    
    def _process_trustee_signatures_from_flat_structure(self, result: Dict[str, Any]) -> None:
 
        # Initialize trustee_signatures list if not already present
        if "trustee_signatures" not in result or not result["trustee_signatures"]:
            result["trustee_signatures"] = []
            
        # Extract and process trustees from flat structure
        trustees = {}
        
        # Identify all trustee prefixed fields using regex pattern
        trustee_fields = {}
        for key in list(result.keys()):
            match = re.match(r'trustee(\d+)_(\w+)', key)
            if match:
                trustee_num = match.group(1)
                field_name = match.group(2)
                
                if trustee_num not in trustee_fields:
                    trustee_fields[trustee_num] = {}
                    
                # Extract the value and remove the field from the flat structure
                value = result.pop(key)
                
                # Only include non-empty values
                if value or field_name == "signature":  # Include signature field even if empty
                    trustee_fields[trustee_num][field_name] = value
        
        # Convert to the proper list structure
        for trustee_num in sorted(trustee_fields.keys()):
            fields = trustee_fields[trustee_num]
            
            # Only add if there's at least a name or signature
            if fields.get("name") or fields.get("signature"):
                trustee = {
                    "name": fields.get("name"),
                    "date": fields.get("date"),
                    "signature": "Present" if fields.get("signature") else None
                }
                
                # Clean up the date format if needed
                if trustee["date"]:
                    date_match = re.search(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})', trustee["date"])
                    if date_match:
                        day, month, year = date_match.groups()
                        # Ensure 4-digit year
                        if len(year) == 2:
                            year = "20" + year if int(year) < 50 else "19" + year
                        trustee["date"] = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
                
                result["trustee_signatures"].append(trustee)
    
    def _clean_boolean_fields(self, result: Dict[str, Any]) -> None:
        """Clean up boolean fields.
        Args:
            result: Extracted result dictionary to modify in-place
        """
        # Ensure boolean fields are actually booleans
        boolean_fields = [
            "identity_verification_consent",
            "fraud_prevention_checks_consent",
            "communication_preference_consent"
        ]
        
        for field in boolean_fields:
            if field in result:
                if isinstance(result[field], str):
                    value = result[field].lower()
                    result[field] = value in ["yes", "true", "y", "✓", "x", "checked", "ticked"]
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess the text before extraction.
        
        Args:
            text: Text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Clean up the text
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('□', '')  # Remove checkbox symbols
        
        return text
    