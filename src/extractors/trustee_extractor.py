"""
Trustee details extractor module.
Specialized extractor for trustee details.
"""

from typing import Dict, Any, Optional
import re

from ..schemas.base import DocumentSection
from .llm_extractor import LLMExtractor


class TrusteeExtractor(LLMExtractor):
    """Extract trustee details from text."""
    
    def __init__(
        self,
        llm_provider: str = "local",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.0
    ):
        """Initialize the trustee extractor.
        
        Args:
            llm_provider: LLM provider to use (local, openai, google)
            model_name: Model name for the chosen provider
            api_key: API key for the chosen provider
            temperature: Temperature setting for the LLM
        """
        super().__init__(
            document_section=DocumentSection.TRUSTEE_DETAILS,
            llm_provider=llm_provider,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature
        )
    
    def extract(self, text: str) -> Dict[str, Any]:
        """Extract trustee details from text.
        
        This method can be extended to add trustee-specific preprocessing
        or post-processing logic.
        
        Args:
            text: Text to extract information from
            
        Returns:
            Dictionary with extracted trustee details
        """
        # Call the parent class implementation
        result = super().extract(text)
        
        # Additional post-processing specific to trustee details
        self._clean_date_of_birth(result)
        self._clean_national_insurance_number(result)
        self._clean_address_fields(result)
        self._clean_boolean_fields(result)
        self._process_non_uk_details(result)
        
        return result
    
    def _clean_date_of_birth(self, result: Dict[str, Any]) -> None:
        """Clean up the date of birth format.
        
        Args:
            result: Extracted result dictionary to modify in-place
        """
        if not result.get("date_of_birth"):
            return
            
        dob = result["date_of_birth"]
        
        # Try to standardize date format to DD/MM/YYYY
        # Handle different separators (/, -, .)
        dob = re.sub(r'[-.]', '/', dob)
        
        # Check if year is in 2-digit format and convert to 4-digit
        parts = dob.split('/')
        if len(parts) == 3:
            day, month, year = parts
            
            # Convert 2-digit year to 4-digit
            if len(year) == 2:
                # Assume 20th century for years 50-99, 21st century for 00-49
                year_num = int(year)
                if year_num >= 50:
                    year = f"19{year}"
                else:
                    year = f"20{year}"
                
            result["date_of_birth"] = f"{day}/{month}/{year}"
    
    def _clean_national_insurance_number(self, result: Dict[str, Any]) -> None:
        """Clean up the national insurance number format.
        
        Args:
            result: Extracted result dictionary to modify in-place
        """
        if not result.get("national_insurance_number"):
            return
            
        ni_number = result["national_insurance_number"]
        
        # Remove spaces and convert to uppercase
        ni_number = ni_number.replace(" ", "").upper()
        
        # Check for common format (e.g., AB123456C)
        if re.match(r'^[A-Z]{2}\d{6}[A-Z]$', ni_number):
            # Already in correct format
            pass
        elif re.match(r'^[A-Z]{2}\d{6}$', ni_number):
            # Missing final letter
            pass
        else:
            # Try to extract the pattern from the text
            # Common formats: AB 12 34 56 C, AB123456C, AB-12-34-56-C
            ni_number = re.sub(r'[-\s]', '', ni_number)
        
        result["national_insurance_number"] = ni_number
    
    def _clean_address_fields(self, result: Dict[str, Any]) -> None:
        """Clean up address-related fields.
        
        Args:
            result: Extracted result dictionary to modify in-place
        """
        # Clean postcode
        if result.get("postcode"):
            postcode = result["postcode"].strip().upper()
            result["postcode"] = postcode
        
        # Clean residential address
        if result.get("permanent_residential_address"):
            address = result["permanent_residential_address"].strip()
            
            # Remove postcode from address if it's at the end
            if result.get("postcode") and address.endswith(result["postcode"]):
                address = address[:-len(result["postcode"])].strip()
                
            result["permanent_residential_address"] = address
    
    def _clean_boolean_fields(self, result: Dict[str, Any]) -> None:
        """Clean up boolean fields.
        
        Args:
            result: Extracted result dictionary to modify in-place
        """
        # Ensure boolean fields are actually booleans
        boolean_fields = ["existing_aj_bell_account", "born_in_uk", "solely_uk_citizen"]
        
        for field in boolean_fields:
            if field in result:
                if isinstance(result[field], str):
                    value = result[field].lower()
                    result[field] = value in ["yes", "true", "y", "✓", "x", "checked", "ticked"]
    
    def _process_non_uk_details(self, result: Dict[str, Any]) -> None:
        """Process non-UK details section.
        
        Args:
            result: Extracted result dictionary to modify in-place
        """
        # If "solely_uk_citizen" is True, non_uk_details should be None
        if result.get("solely_uk_citizen") == True:
            result["not_uk_details"] = None
            return
            
        # Check if non_uk_details fields exist in the flat result
        non_uk_fields = [
            "country_of_birth", "nationality", "id_number", "type_of_number",
            "passport_number", "primary_residence", "secondary_residence",
            "primary_citizenship", "secondary_citizenship"
        ]
        
        # If any of these fields exist, move them to the nested structure
        non_uk_details = {}
        for field in non_uk_fields:
            if field in result:
                non_uk_details[field] = result.pop(field)
        
        # Check if extracted object contains nested structure
        if "not_uk_details" in result and isinstance(result["not_uk_details"], dict):
            # Update with any fields found in the flat structure
            result["not_uk_details"].update(non_uk_details)
        else:
            # Create new nested structure if there are any non-UK fields
            if non_uk_details:
                result["not_uk_details"] = non_uk_details
            else:
                result["not_uk_details"] = None