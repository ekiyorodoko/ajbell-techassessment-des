"""
Regex-based extractor module.
Uses regular expressions to extract information from text.
"""

import re
from typing import Dict, Any, List, Tuple, Pattern

from ..schemas.base import DocumentSection
from .base_extractor import BaseExtractor


class RegexExtractor(BaseExtractor):
    """Extract information using regular expressions."""
    
    def __init__(self, document_section: DocumentSection):
        """Initialize the regex extractor.
        
        Args:
            document_section: The document section this extractor is responsible for
        """
        super().__init__(document_section)
        self.patterns = self._configure_patterns()
    
    def _configure_patterns(self) -> Dict[str, List[Tuple[Pattern, int]]]:
        """Configure regex patterns based on the document section.
        
        Returns:
            Dictionary mapping field names to lists of (pattern, group) tuples
        """
        if self.document_section == DocumentSection.TRUST_REGISTRATION:
            return {
                "HMRC_unique_reference_number": [
                    (re.compile(r'URN[=:\s-]*([A-Za-z0-9-]+)', re.IGNORECASE), 1),
                    (re.compile(r'HMRC\s+unique\s+reference\s+(?:number|URN)[=:\s-]*([A-Za-z0-9-]+)', re.IGNORECASE), 1),
                    (re.compile(r'(?:reference|URN)[=:\s-]*([A-Za-z0-9-]+)', re.IGNORECASE), 1),
                ],
                "proof_of_registration_attached": [
                    (re.compile(r'proof\s+of\s+registration\s+(?:is\s+)?attached', re.IGNORECASE), 0),
                    (re.compile(r'attached\s+proof\s+of\s+registration', re.IGNORECASE), 0),
                    (re.compile(r'(?:have|has)\s+(?:included|attached)\s+(?:the\s+)?proof', re.IGNORECASE), 0),
                ],
            }
        elif self.document_section == DocumentSection.DONOR_DETAILS:
            return {
                "title": [
                    (re.compile(r'Title[:\s]*([A-Za-z]+\.*(?:\s*/\s*[A-Za-z]+\.*)*)', re.IGNORECASE), 1),
                ],
                "surname": [
                    (re.compile(r'Surname[:\s]*([A-Za-z-]+)', re.IGNORECASE), 1),
                ],
                "forenames": [
                    (re.compile(r'Forename(?:\(s\))?[:\s]*([A-Za-z\s-]+)', re.IGNORECASE), 1),
                ],
                "date_of_birth": [
                    (re.compile(r'Date\s+of\s+birth[:\s]*(\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4})', re.IGNORECASE), 1),
                    (re.compile(r'DOB[:\s]*(\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4})', re.IGNORECASE), 1),
                ],
                "national_insurance_number": [
                    (re.compile(r'National\s+[Ii]nsurance\s+[Nn]umber[:\s]*([A-Za-z0-9\s]+)', re.IGNORECASE), 1),
                    (re.compile(r'NI(?:NO)?[:\s]*([A-Za-z0-9\s]+)', re.IGNORECASE), 1),
                ],
                "permanent_residential_address": [
                    (re.compile(r'(?:Permanent\s+)?[Rr]esidential\s+[Aa]ddress[:\s]*([A-Za-z0-9\s,.-]+)', re.IGNORECASE), 1),
                ],
                "postcode": [
                    (re.compile(r'[Pp]ostcode[:\s]*([A-Za-z0-9\s]+)', re.IGNORECASE), 1),
                ],
                "country_of_residence": [
                    (re.compile(r'[Cc]ountry\s+of\s+[Rr]esidence[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "country_of_nationality": [
                    (re.compile(r'[Cc]ountry\s+of\s+[Nn]ationality[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "deceased": [
                    (re.compile(r'donor\s+has\s+passed\s+away', re.IGNORECASE), 0),
                    (re.compile(r'deceased', re.IGNORECASE), 0),
                ],
            }
        elif self.document_section == DocumentSection.TRUSTEE_DETAILS:
            return {
                "title": [
                    (re.compile(r'Title[:\s]*([A-Za-z]+\.*(?:\s*/\s*[A-Za-z]+\.*)*)', re.IGNORECASE), 1),
                ],
                "surname": [
                    (re.compile(r'Surname[:\s]*([A-Za-z-]+)', re.IGNORECASE), 1),
                ],
                "forenames": [
                    (re.compile(r'Forename(?:\(s\))?[:\s]*([A-Za-z\s-]+)', re.IGNORECASE), 1),
                ],
                "date_of_birth": [
                    (re.compile(r'Date\s+of\s+birth[:\s]*(\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4})', re.IGNORECASE), 1),
                    (re.compile(r'DOB[:\s]*(\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4})', re.IGNORECASE), 1),
                ],
                "national_insurance_number": [
                    (re.compile(r'National\s+[Ii]nsurance\s+[Nn]umber[:\s]*([A-Za-z0-9\s]+)', re.IGNORECASE), 1),
                    (re.compile(r'NI(?:NO)?[:\s]*([A-Za-z0-9\s]+)', re.IGNORECASE), 1),
                ],
                "permanent_residential_address": [
                    (re.compile(r'(?:Permanent\s+)?[Rr]esidential\s+[Aa]ddress[:\s]*([A-Za-z0-9\s,.-]+)', re.IGNORECASE), 1),
                ],
                "postcode": [
                    (re.compile(r'[Pp]ostcode[:\s]*([A-Za-z0-9\s]+)', re.IGNORECASE), 1),
                ],
                "country": [
                    (re.compile(r'^Country[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "telephone_number": [
                    (re.compile(r'(?:[Dd]aytime\s+)?[Tt]elephone\s+[Nn]umber[:\s]*([0-9\s]+)', re.IGNORECASE), 1),
                ],
                "email_address": [
                    (re.compile(r'[Ee]mail\s+[Aa]ddress[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', re.IGNORECASE), 1),
                ],
                "existing_aj_bell_account": [
                    (re.compile(r'existing\s+AJ\s+Bell\s+Account\?[:\s]*Yes', re.IGNORECASE), 0),
                ],
                "existing_account_number": [
                    (re.compile(r'existing\s+account\s+number[:\s]*([A-Za-z0-9\s]+)', re.IGNORECASE), 1),
                ],
                "born_in_uk": [
                    (re.compile(r'born\s+in\s+the\s+UK\?.*Yes', re.IGNORECASE), 0),
                ],
                "solely_uk_citizen": [
                    (re.compile(r'solely\s+a\s+UK\s+citizen.*Yes', re.IGNORECASE), 0),
                ],
                "country_of_birth": [
                    (re.compile(r'Country\s+of\s+birth[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "nationality": [
                    (re.compile(r'Nationality[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "id_number": [
                    (re.compile(r'Identification\s+number[:\s]*([A-Za-z0-9\s-]+)', re.IGNORECASE), 1),
                ],
                "type_of_number": [
                    (re.compile(r'Type\s+of\s+number[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "passport_number": [
                    (re.compile(r'Passport\s+number[:\s]*([A-Za-z0-9\s-]+)', re.IGNORECASE), 1),
                ],
                "primary_residence": [
                    (re.compile(r'Country\s+of\s+residence\s+for\s+tax\s+purposes[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "secondary_residence": [
                    (re.compile(r'Second\s+country\s+of\s+residence\s+for\s+tax\s+purposes[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "primary_citizenship": [
                    (re.compile(r'Country\s+of\s+citizenship[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "secondary_citizenship": [
                    (re.compile(r'Second\s+country\s+of\s+citizenship[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
            }
        elif self.document_section == DocumentSection.BENEFICIARY_DETAILS:
            return {
                "title": [
                    (re.compile(r'Title[:\s]*(Dr|Mr|Mrs|Miss|Ms|Other)', re.IGNORECASE), 1),
                    (re.compile(r'(?:Dr|Mr|Mrs|Miss|Ms)(?:/(?:Dr|Mr|Mrs|Miss|Ms))*', re.IGNORECASE), 0),
                ],
                "surname": [
                    (re.compile(r'Surname[:\s]*([A-Za-z\s.-]+)', re.IGNORECASE), 1),
                    (re.compile(r'Last\s+name[:\s]*([A-Za-z\s.-]+)', re.IGNORECASE), 1),
                ],
                "forenames": [
                    (re.compile(r'Forename\(s\)[:\s]*([A-Za-z\s.-]+)', re.IGNORECASE), 1),
                    (re.compile(r'First\s+name[:\s]*([A-Za-z\s.-]+)', re.IGNORECASE), 1),
                ],
                "date_of_birth": [
                    (re.compile(r'Date\s+of\s+birth[:\s]*(\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4})', re.IGNORECASE), 1),
                    (re.compile(r'DOB[:\s]*(\d{1,2}[\/-]\d{1,2}[\/-]\d{2,4})', re.IGNORECASE), 1),
                ],
                "national_insurance_number": [
                    (re.compile(r'National\s+Insurance\s+number[:\s]*([A-Z0-9\s]+)', re.IGNORECASE), 1),
                    (re.compile(r'NI\s+number[:\s]*([A-Z0-9\s]+)', re.IGNORECASE), 1),
                ],
                "permanent_residential_address": [
                    (re.compile(r'Permanent\s+residential\s+address[:\s]*([A-Za-z0-9\s,.-]+)', re.IGNORECASE), 1),
                    (re.compile(r'Address[:\s]*([A-Za-z0-9\s,.-]+)', re.IGNORECASE), 1),
                ],
                "postcode": [
                    (re.compile(r'Postcode[:\s]*([A-Z0-9\s]+)', re.IGNORECASE), 1),
                ],
                "country": [
                    (re.compile(r'Country[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "telephone_number": [
                    (re.compile(r'(?:Daytime\s+)?[Tt]elephone\s+number[:\s]*([0-9+\s]+)', re.IGNORECASE), 1),
                    (re.compile(r'Phone[:\s]*([0-9+\s]+)', re.IGNORECASE), 1),
                ],
                "email_address": [
                    (re.compile(r'Email\s+address[:\s]*([A-Za-z0-9@._-]+)', re.IGNORECASE), 1),
                    (re.compile(r'Email[:\s]*([A-Za-z0-9@._-]+)', re.IGNORECASE), 1),
                ],
                "born_in_uk": [
                    (re.compile(r'born\s+in\s+the\s+UK\?.*Yes', re.IGNORECASE), 0),
                ],
                "solely_uk_citizen": [
                    (re.compile(r'solely\s+a\s+UK\s+citizen.*Yes', re.IGNORECASE), 0),
                ],
                "country_of_birth": [
                    (re.compile(r'Country\s+of\s+birth[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "nationality": [
                    (re.compile(r'Nationality[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "primary_residence": [
                    (re.compile(r'Country\s+of\s+residence\s+for\s+tax\s+purposes[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "secondary_residence": [
                    (re.compile(r'Second\s+country\s+of\s+residence\s+for\s+tax\s+purposes[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "primary_citizenship": [
                    (re.compile(r'Country\s+of\s+citizenship[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
                "secondary_citizenship": [
                    (re.compile(r'Second\s+country\s+of\s+citizenship[:\s]*([A-Za-z\s]+)', re.IGNORECASE), 1),
                ],
            }
        elif self.document_section == DocumentSection.NOMINATED_BANK_ACCOUNT:
            return {
                "account_holder_name": [
                    (re.compile(r'Account\s+holder(?:\'s)?\s+name[:\s]*([A-Za-z\s.-]+)', re.IGNORECASE), 1),
                    (re.compile(r'Name\s+of\s+account\s+holder[:\s]*([A-Za-z\s.-]+)', re.IGNORECASE), 1),
                ],
                "account_number": [
                    (re.compile(r'(?:Bank|Building\s+society)\s+account\s+number[:\s]*([0-9\s]+)', re.IGNORECASE), 1),
                    (re.compile(r'Account\s+number[:\s]*([0-9\s]+)', re.IGNORECASE), 1),
                ],
                "sort_code": [
                    (re.compile(r'Sort\s+code[:\s]*([0-9-\s]+)', re.IGNORECASE), 1),
                ],
            }
        elif self.document_section == DocumentSection.SECURITY_INFORMATION:
            return {
                "username": [
                    (re.compile(r'Username[:\s]*([A-Za-z0-9\s]+)', re.IGNORECASE), 1),
                    (re.compile(r'Create\s+(?:the\s+)?username[^:]*?[:\s]*([A-Za-z0-9\s]+)', re.IGNORECASE), 1),
                ],
                "mother_maiden_name": [
                    (re.compile(r'mother(?:\'s)?\s+maiden\s+name[:\s]*([A-Za-z\s.-]+)', re.IGNORECASE), 1),
                ],
                "first_school_name": [
                    (re.compile(r'(?:name\s+of\s+(?:your\s+)?first\s+school|first\s+school\s+name)[:\s]*([A-Za-z0-9\s,.-]+)', re.IGNORECASE), 1),
                ],
            }
        elif self.document_section == DocumentSection.DATA_PRIVACY_STATEMENT:
            return {
                "identity_verification_consent": [
                    (re.compile(r'identity\s+verification.*?Yes', re.IGNORECASE), 0),
                    (re.compile(r'identity\s+verification.*?No', re.IGNORECASE), 0),
                ],
                "fraud_prevention_checks_consent": [
                    (re.compile(r'fraud\s+prevention.*?Yes', re.IGNORECASE), 0),
                    (re.compile(r'fraud\s+prevention.*?No', re.IGNORECASE), 0),
                ],
                "communication_preference_consent": [
                    (re.compile(r'would\s+like\s+to\s+receive\s+communications.*?Yes', re.IGNORECASE), 0),
                    (re.compile(r'would\s+like\s+to\s+receive\s+communications.*?No', re.IGNORECASE), 0),
                ],
                # Trustee 1 signature
                "trustee1_name": [
                    (re.compile(r'Trustee\s+1.*?Name[:\s]*([A-Za-z\s.-]+)', re.IGNORECASE), 1),
                ],
                "trustee1_date": [
                    (re.compile(r'Trustee\s+1.*?Date[:\s]*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})', re.IGNORECASE), 1),
                ],
                "trustee1_signature": [
                    (re.compile(r'Trustee\s+1.*?Signature', re.IGNORECASE), 0),
                ],
                # Trustee 2 signature
                "trustee2_name": [
                    (re.compile(r'Trustee\s+2.*?Name[:\s]*([A-Za-z\s.-]+)', re.IGNORECASE), 1),
                ],
                "trustee2_date": [
                    (re.compile(r'Trustee\s+2.*?Date[:\s]*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})', re.IGNORECASE), 1),
                ],
                "trustee2_signature": [
                    (re.compile(r'Trustee\s+2.*?Signature', re.IGNORECASE), 0),
                ],
            }
        else:
            return {}
    
    def extract(self, text: str) -> Dict[str, Any]:
        """Extract information from text using regex patterns.
        
        Args:
            text: Text to extract information from
            
        Returns:
            Dictionary with extracted information
        """
        result = {}
        
        for field, patterns in self.patterns.items():
            # Try each pattern for the field until one matches
            for pattern_tuple in patterns:
                # Unpack pattern tuple with appropriate handling for lambda functions
                if len(pattern_tuple) >= 3:  # Has a transform function
                    pattern, group, transform_func = pattern_tuple
                else:
                    pattern, group = pattern_tuple
                    transform_func = None
                
                match = pattern.search(text)
                if match:
                    # For boolean fields (where group=0), just check for existence
                    if group == 0:
                        if transform_func:
                            # Apply transformation function if provided
                            result[field] = transform_func(match)
                        else:
                            result[field] = True
                    else:
                        # Extract the value from the capturing group
                        extracted_value = match.group(group).strip()
                        if transform_func:
                            # Apply transformation function if provided
                            result[field] = transform_func(extracted_value)
                        else:
                            result[field] = extracted_value
                    break
            
            # If no pattern matched, set a default value
            if field not in result:
                if field in ["proof_of_registration_attached", "deceased", "born_in_uk"]:
                    result[field] = False
                elif field in ["not_born_in_uk", "security_questions"]:
                    result[field] = None
                else:
                    result[field] = ""
        
        return result