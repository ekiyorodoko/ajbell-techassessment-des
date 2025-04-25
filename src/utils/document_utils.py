"""
Document utilities module.
Provides utility functions for working with documents.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Union, Optional, List


def save_json(data: Dict[str, Any], output_path: str, indent: int = 2) -> None:
    """Save data to a JSON file.
    
    Args:
        data: Data to save
        output_path: Path to save the JSON file
        indent: Indentation level for the JSON file
    """
    # Create parent directories if they don't exist
    parent_dir = os.path.dirname(output_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir)
    
    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def generate_output_path(input_path: str, suffix: str = 'json', output_dir: Optional[str] = None) -> str:
    """Generate an output path based on an input path.
    
    Args:
        input_path: Path to the input file
        suffix: File extension for the output file (without dot)
        output_dir: Optional output directory
        
    Returns:
        Generated output path
    """
    input_file = Path(input_path)
    
    if output_dir:
        output_path = Path(output_dir) / f"{input_file.stem}.{suffix}"
    else:
        output_path = input_file.with_suffix(f".{suffix}")
    
    return str(output_path)
