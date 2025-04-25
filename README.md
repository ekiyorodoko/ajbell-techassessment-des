# Data Extraction Service

A modular Python application for extracting structured information from PDF documents. The system handles both scanned (image-based) and text-based PDFs, automatically detecting the appropriate processing method.

## Features

- **Automatic PDF Type Detection**: Identifies whether a PDF is scanned or text-based
- **OCR Integration**: Uses Tesseract OCR for processing scanned documents
- **Modular Schema System**: Extensible schema system for different document types
- **Multiple Extraction Methods**:
  - LLM-powered extraction (OpenAI, Google Gemini, or local models)
  - Fallback to regex-based extraction when needed
- **Multi-Section Support**: Extracts information from different sections of a document

## Installation

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Tesseract OCR:

   - **Ubuntu/Debian**:
     ```bash
     sudo apt-get install tesseract-ocr
     ```
   
   - **macOS** (using Homebrew):
     ```bash
     brew install tesseract
     ```
   
   - **Windows**:
     Download and install from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

## Sample Project Structure

```
pdf_extractor/
├── __init__.py                    # Package initialization
├── main.py                        # Main entry point
├── requirements.txt               # Dependencies
├── README.md                      # Documentation
├── schemas/                       # Schema definitions
│   ├── __init__.py
│   ├── base.py                    # Base schema utilities
│   ├── trust_registration.py      # Trust registration schema
│   └── donor_details.py           # Donor details schema
├── processors/                    # PDF processing modules
│   ├── __init__.py
│   ├── pdf_processor.py           # Base PDF processor
│   ├── ocr_processor.py           # OCR handling
│   └── text_processor.py          # Text extraction
├── extractors/                    # Information extraction modules
│   ├── __init__.py
│   ├── base_extractor.py          # Base extractor class
│   ├── llm_extractor.py           # LLM-based extraction
│   ├── regex_extractor.py         # Regex-based extraction
│   ├── trust_extractor.py         # Trust registration extractor
│   └── donor_extractor.py         # Donor details extractor
└── utils/                         # Utility functions
    ├── __init__.py
    ├── document_utils.py          # Document handling utilities
    └── llm_utils.py               # LLM configuration utilities
```

## Usage

### Basic Usage

Process a single PDF file:

```bash
python main.py path/to/document.pdf
```

This will:
- Detect and process all sections in the document
- Save the output to a JSON file with the same name as the input PDF
- Use a local LLM provider (Ollama) by default

### Processing Specific Sections

Extract only specific sections:

```bash
python main.py path/to/document.pdf --sections trust_registration donor_details
```

### Specifying Output Location

```bash
python main.py path/to/document.pdf --output results.json
```

### Using Different LLM Providers

With OpenAI:

```bash
export OPENAI_API_KEY="your-openai-key"
python main.py path/to/document.pdf --llm openai --model gpt-4o
```

With Google Gemini:

```bash
export GOOGLE_API_KEY="your-google-key"
python main.py path/to/document.pdf --llm google --model gemini-2.0-flash
```


## Example Output

```json
{
  "trust_registration": {
    "HMRC_unique_reference_number": "ABCD-12345",
    "proof_of_registration_attached": true
  },
  "donor_details": {
    "title": "Mr",
    "surname": "Doe",
    "forenames": "John",
    "date_of_birth": "01/01/1980",
    "national_insurance_number": "AB123456C",
    "permanent_residential_address": "123 Main Rd",
    "postcode": "L12 3AB",
    "country_of_residence": "UK",
    "country_of_nationality": "UK",
    "deceased": false
  }
}
```

## Extending the System

### Adding New Document Schemas

1. Create a new schema file in the `schemas/` directory
2. Define a Pydantic model for the schema with appropriate fields
3. Register the schema using the `@register_schema` decorator
4. Import the schema in `schemas/__init__.py`

### Adding New Extractors

1. Create a new extractor class that inherits from `BaseExtractor` or `LLMExtractor`
2. Implement the `extract` method to extract information from text
3. Add any pre-processing or post-processing specific to your extractor
4. Register the extractor in `extractors/__init__.py`

## Evaluation System

The application includes a comprehensive evaluation system that compares extracted data against ground truth data. The evaluation metrics include:

### Metrics

- **Exact Matches**: Fields that match exactly between extracted and ground truth data
- **Partial Matches**: String fields that have high similarity (≥80%) but aren't exact matches
- **Mismatches**: Fields that don't match or have low similarity
- **Missing Fields**: Fields present in ground truth but missing in extracted data

### Similarity Calculation

- String similarity is calculated using Python's `SequenceMatcher`
- Threshold for partial matches is set at 80% similarity
- Non-string fields are evaluated using exact matching only

### Output Format

The evaluation results are saved in `data/evaluation_results.json` with the following structure:

```json
{
  "summary_metrics": {
    "exact_matches": 0,
    "partial_matches": 0,
    "mismatches": 0,
    "missing_fields": 0,
    "exact_match_percentage": 0.0,
    "partial_match_percentage": 0.0,
    "total_accuracy": 0.0
  },
  "evaluation_method": {
    "exact_match": "Direct equality comparison",
    "partial_match": "String similarity ratio >= 0.8 using SequenceMatcher",
    "mismatch": "String similarity ratio < 0.8 or type mismatch"
  },
  "detailed_results": {
    "field_path": {
      "expected": "expected_value",
      "actual": "actual_value",
      "status": "exact_match|partial_match|mismatch|missing"
    }
  }
}
```

### Running Evaluation

To evaluate extraction results:

```bash
python src/tests/evaluation.py
```

This will compare the extracted data (`DataExtraction.json`) with the ground truth (`EvaluationData.json`) and generate detailed evaluation results.
