"""
Base extractor module.
Defines the interface for information extractors.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional
from pydantic import BaseModel
from src.schemas.base import DocumentSection, SchemaRegistry


class BaseExtractor(ABC):
    """Base class for information extractors."""
    
    def __init__(self, document_section: DocumentSection):
        """Initialize the extractor.
        Args:
            document_section: The document section this extractor is responsible for
        """
        self.document_section = document_section
        self.schema_id = DocumentSection.get_schema_id(document_section)
        self.schema_class = SchemaRegistry.get_schema(self.schema_id)
        
        if not self.schema_class:
            raise ValueError(f"No schema registered for section: {self.schema_id}")
    
    @abstractmethod
    def extract(self, text: str) -> Dict[str, Any]:
        """Extract information from text.
        Args:
            text: Text to extract information from
        Returns:
            Dictionary with extracted information
        """
        pass
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted data against the schema.
        Args:
            data: Extracted data
        Returns:
            Validated data as a dictionary
        """
        try:
            # Create an instance of the schema class with the extracted data
            instance = self.schema_class(**data)
            # Convert back to dict
            return instance.model_dump()
        except Exception as e:
            raise ValueError(f"Validation failed for {self.schema_id}: {str(e)}")