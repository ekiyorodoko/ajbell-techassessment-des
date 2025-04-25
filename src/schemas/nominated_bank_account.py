"""
Nominated Bank Account schema for document extraction.
"""

from typing import Optional
from pydantic import BaseModel
from .base import register_schema


@register_schema("nominated_bank_account")
class NominatedBankAccount(BaseModel):
    """Details about a nominated bank account for withdrawals."""
    
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    sort_code: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "title": "NominatedBankAccount",
            "$schema": "http://json-schema.org/draft-07/schema#"
        } 
    } 