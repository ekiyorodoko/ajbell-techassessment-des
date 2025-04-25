"""
Trust registration schema for document extraction.
"""

from typing import Optional
from pydantic import BaseModel
from .base import register_schema


@register_schema("trust_registration")
class TrustRegistrationDetails(BaseModel):
    """Details about trust registration with HMRC."""
    
    HMRC_unique_reference_number: Optional[str] = None
    proof_of_registration_attached: Optional[bool] = None
    
    model_config = {
        "json_schema_extra": {
            "title": "TrustRegistrationDetails",
            "$schema": "http://json-schema.org/draft-07/schema#"
        }
    }