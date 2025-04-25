"""
Data Privacy Statement schema for document extraction.
"""

from typing import Optional, List
from pydantic import BaseModel
from .base import register_schema


class TrusteeSignature(BaseModel):
    """Trustee signature details."""
    
    name: Optional[str] = None
    date: Optional[str] = None
    signature: Optional[str] = None


@register_schema("data_privacy_statement")
class DataPrivacyStatement(BaseModel):
    """Data privacy statement and consent details."""
    
    identity_verification_consent: Optional[bool] = None
    fraud_prevention_checks_consent: Optional[bool] = None
    communication_preference_consent: Optional[bool] = None
    trustee_signatures: Optional[List[TrusteeSignature]] = None
    
    model_config = {
        "json_schema_extra": {
            "title": "DataPrivacyStatement",
            "$schema": "http://json-schema.org/draft-07/schema#"
        } 
    } 