"""
Donor details extractor module.
Specialized extractor for donor details.
"""

from typing import Dict, Any, Optional
import re

from ..schemas.base import DocumentSection
from .llm_extractor import LLMExtractor


class DonorExtractor(LLMExtractor):
    """Extract donor details from text."""
    
    def __init__(
        self,
        llm_provider: str = "local",
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.0
    ):
        """Initialize the donor extractor.
        Args:
            llm_provider: LLM provider to use (local, openai, google)
            model_name: Model name for the chosen provider
            api_key: API key for the chosen provider
            temperature: Temperature setting for the LLM
        """
        super().__init__(
            document_section=DocumentSection.DONOR_DETAILS,
            llm_provider=llm_provider,
            model_name=model_name,
            api_key=api_key,
            temperature=temperature
        )
    
    def extract(self, text: str) -> Dict[str, Any]:
        """Extract donor details from text.
        
        This method can be extended to add donor-specific preprocessing
        or post-processing logic.
        Args:
            text: Text to extract information from
        Returns:
            Dictionary with extracted donor details
        """
        # Call the parent class implementation
        result = super().extract(text)
        
        # Additional post-processing specific to donor details
        self._clean_date_of_birth(result)
        self._clean_national_insurance_number(result)
        self._clean_address_fields(result)
        self._infer_deceased_status(result, text)
        
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
    
    def _infer_deceased_status(self, result: Dict[str, Any], text: str) -> None:
        """Infer deceased status from text if not explicitly found.
        
        Args:
            result: Extracted result dictionary to modify in-place
            text: Original text
        """
        if "deceased" not in result:
            result["deceased"] = False
            
        # Look for text suggesting the donor is deceased
        deceased_indicators = [
            "has passed away",
            "deceased donor",
            "leave the residential address blank",
            "tick here if the donor has passed away"
        ]
        
        for indicator in deceased_indicators:
            if indicator in text.lower():
                result["deceased"] = True
                break
                
        # If the form has a section for indicating deceased status,
        # and any of the fields like "Tick here if..." appears checked,
        # set deceased to True
        checkbox_indicators = [
            "☑",  # Checked box
            "☒",  # Crossed box
            "[✓]",  # Check in brackets
            "(✓)",  # Check in parentheses
            "✓",  # Check mark
            "×"  # Cross
        ]
        
        # Check if any deceased indicator is near a checkbox indicator
        for deceased_indicator in deceased_indicators:
            for checkbox in checkbox_indicators:
                if f"{checkbox}.*{deceased_indicator}" in text or f"{deceased_indicator}.*{checkbox}" in text:
                    result["deceased"] = True
                    break