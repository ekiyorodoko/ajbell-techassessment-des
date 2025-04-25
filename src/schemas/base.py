"""
Base schema utilities for document extraction.
This module provides base classes and functions for schema validation and handling.
"""

from typing import Dict, Any, Type, List, Optional
from enum import Enum
from pydantic import BaseModel


class SchemaRegistry:
    """Registry of available schemas for document extraction."""
    
    _schemas: Dict[str, Type[BaseModel]] = {}
    
    @classmethod
    def register(cls, schema_id: str, schema_class: Type[BaseModel]) -> None:
        """Register a schema class with an identifier.
        
        Args:
            schema_id: Unique identifier for the schema
            schema_class: Pydantic model class for the schema
        """
        cls._schemas[schema_id] = schema_class
    
    @classmethod
    def get_schema(cls, schema_id: str) -> Optional[Type[BaseModel]]:
        """Get a schema class by its identifier.
        
        Args:
            schema_id: Identifier for the schema
            
        Returns:
            The schema class if found, None otherwise
        """
        return cls._schemas.get(schema_id)
    
    @classmethod
    def list_schemas(cls) -> List[str]:
        """List all registered schema identifiers.
        
        Returns:
            List of schema identifiers
        """
        return list(cls._schemas.keys())


class DocumentSection(Enum):
    """Enum for document sections that can be extracted."""
    
    TRUST_REGISTRATION = "trust_registration"
    DONOR_DETAILS = "donor_details"
    TRUSTEE_DETAILS = "trustee_details"
    BENEFICIARY_DETAILS = "beneficiary_details"
    NOMINATED_BANK_ACCOUNT = "nominated_bank_account"
    SECURITY_INFORMATION = "security_information"
    DATA_PRIVACY_STATEMENT = "data_privacy_statement"
    
    @classmethod
    def get_schema_id(cls, section: 'DocumentSection') -> str:
        """Get the schema ID associated with a document section."""
        mapping = {
            cls.TRUST_REGISTRATION: "trust_registration",
            cls.DONOR_DETAILS: "donor_details",
            cls.TRUSTEE_DETAILS: "trustee_details",
            cls.BENEFICIARY_DETAILS: "beneficiary_details",
            cls.NOMINATED_BANK_ACCOUNT: "nominated_bank_account",
            cls.SECURITY_INFORMATION: "security_information",
            cls.DATA_PRIVACY_STATEMENT: "data_privacy_statement"
        }
        return mapping.get(section, "unknown")


def register_schema(schema_id: str):
    """Decorator to register a schema class with the SchemaRegistry.
    
    Args:
        schema_id: Unique identifier for the schema
        
    Returns:
        Decorator function that registers the class
    """
    def decorator(cls):
        SchemaRegistry.register(schema_id, cls)
        return cls
    return decorator