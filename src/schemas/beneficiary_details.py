"""
Beneficiary details schema for document extraction.
"""

from typing import Optional, List
from pydantic import BaseModel
from .base import register_schema


class NonUKDetails(BaseModel):
    """Details for beneficiaries not born in the UK."""
    
    country_of_birth: Optional[str] = None
    nationality: Optional[str] = None
    id_number: Optional[str] = None
    type_of_number: Optional[str] = None
    passport_number: Optional[str] = None
    primary_residence: Optional[str] = None
    secondary_residence: Optional[str] = None
    country_of_citizenship: Optional[str] = None
    second_country_of_citizenship: Optional[str] = None


@register_schema("beneficiary_details")
class BeneficiaryDetails(BaseModel):
    """Details about a beneficiary of the trust."""
    
    title: Optional[str] = None
    surname: Optional[str] = None
    forenames: Optional[str] = None
    date_of_birth: Optional[str] = None
    national_insurance_number: Optional[str] = None
    permanent_residential_address: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = None
    telephone_number: Optional[str] = None
    email_address: Optional[str] = None
    born_in_uk: Optional[bool] = None
    not_born_in_uk: Optional[NonUKDetails] = None
    
    model_config = {
        "json_schema_extra": {
            "title": "BeneficiaryDetails",
            "$schema": "http://json-schema.org/draft-07/schema#"
        }
    }