"""
Donor details schema for document extraction.
"""

from typing import Optional
from pydantic import BaseModel
from .base import register_schema


@register_schema("donor_details")
class DonorDetails(BaseModel):
    """Details about a donor of the trust."""
    
    title: Optional[str] = None
    surname: Optional[str] = None
    forenames: Optional[str] = None
    date_of_birth: Optional[str] = None
    national_insurance_number: Optional[str] = None
    permanent_residential_address: Optional[str] = None
    postcode: Optional[str] = None
    country_of_residence: Optional[str] = None
    country_of_nationality: Optional[str] = None
    deceased: Optional[bool] = None
    
    model_config = {
        "json_schema_extra": {
            "title": "DonorDetails",
            "$schema": "http://json-schema.org/draft-07/schema#"
        }
    }