"""
Security Information schema for document extraction.
"""

from typing import Optional
from pydantic import BaseModel
from .base import register_schema


class SecurityQuestions(BaseModel):
    """Security questions for account verification."""
    
    mother_maiden_name: Optional[str] = None
    first_school_name: Optional[str] = None


@register_schema("security_information")
class SecurityInformation(BaseModel):
    """Security information for online account access."""
    
    username: Optional[str] = None
    security_questions: Optional[SecurityQuestions] = None
    
    model_config = {
        "json_schema_extra": {
            "title": "SecurityInformation",
            "$schema": "http://json-schema.org/draft-07/schema#"
        } 
    } 