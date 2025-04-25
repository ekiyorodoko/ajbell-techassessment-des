import json
from difflib import SequenceMatcher
import os
from datetime import datetime

def calculate_string_similarity(str1, str2):
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, str1, str2).ratio()

def compare_with_ground_truth(extracted_data, ground_truth_data):
    """Compare extracted data with ground truth data and calculate accuracy metrics."""
    results = {
        "exact_matches": 0,
        "partial_matches": 0,
        "mismatches": 0,
        "missing_fields": 0,
        "field_results": {}
    }
    
    total_fields = 0
    for section, section_data in ground_truth_data.items():
        if section not in extracted_data:
            results["missing_fields"] += len(section_data)
            continue
            
        for field, expected_value in section_data.items():
            total_fields += 1
            if field not in extracted_data[section]:
                results["missing_fields"] += 1
                results["field_results"][f"{section}.{field}"] = {
                    "expected": expected_value,
                    "actual": "MISSING",
                    "status": "missing"
                }
            else:
                actual_value = extracted_data[section][field]
                if actual_value == expected_value:
                    results["exact_matches"] += 1
                    status = "exact_match"
                elif isinstance(expected_value, str) and isinstance(actual_value, str):
                    # For strings, calculate similarity ratio
                    similarity = calculate_string_similarity(actual_value, expected_value)
                    if similarity >= 0.8:  # 80% similarity threshold
                        results["partial_matches"] += 1
                        status = "partial_match"
                    else:
                        results["mismatches"] += 1
                        status = "mismatch"
                else:
                    results["mismatches"] += 1
                    status = "mismatch"
                    
                results["field_results"][f"{section}.{field}"] = {
                    "expected": expected_value,
                    "actual": actual_value,
                    "status": status
                }
    
    # Calculate accuracy percentages
    results["exact_match_percentage"] = round((results["exact_matches"] / total_fields) * 100, 2)
    results["partial_match_percentage"] = round((results["partial_matches"] / total_fields) * 100, 2)
    results["total_accuracy"] = round(((results["exact_matches"] + results["partial_matches"]) / total_fields) * 100, 2)
    
    return results

# Get the absolute path to the data directory
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'data'))

# Load the extracted data
with open(os.path.join(data_dir, 'DataExtraction.json'), 'r') as f:
    extracted_data = json.load(f)

# Load the ground truth data
with open(os.path.join(data_dir, 'EvaluationData.json'), 'r') as f:
    ground_truth_data = json.load(f)

# Compare the data
results = compare_with_ground_truth(extracted_data, ground_truth_data)

# Create a formatted output dictionary
evaluation_output = {
    "summary_metrics": {
        "exact_matches": results["exact_matches"],
        "partial_matches": results["partial_matches"],
        "mismatches": results["mismatches"],
        "missing_fields": results["missing_fields"],
        "exact_match_percentage": results["exact_match_percentage"],
        "partial_match_percentage": results["partial_match_percentage"],
        "total_accuracy": results["total_accuracy"]
    },
    "evaluation_method": {
        "exact_match": "Direct equality comparison",
        "partial_match": "String similarity ratio >= 0.8 using SequenceMatcher",
        "mismatch": "String similarity ratio < 0.8 or type mismatch"
    },
    "detailed_results": results["field_results"]
}

# Write results to file
output_file = os.path.join(data_dir, 'evaluation_results.json')
with open(output_file, 'w') as f:
    json.dump(evaluation_output, f, indent=2)
