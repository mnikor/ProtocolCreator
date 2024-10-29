SYNOPSIS_ANALYSIS_PROMPT = """
Analyze the following synopsis and return ONLY a JSON object with no additional text:

{synopsis_text}

Format your response as a valid JSON object with the following structure:
{
    "study_type_and_design": {
        "primary_classification": "string",
        "design_type": "string",
        "phase": "string",
        "key_features": ["string"]
    },
    "critical_parameters": {
        "population": "string",
        "intervention": "string",
        "control_comparator": "string",
        "primary_endpoint": "string",
        "secondary_endpoints": ["string"]
    },
    "required_protocol_sections": ["string"],
    "missing_information": ["string"]
}

IMPORTANT: Return ONLY the JSON object without any additional text or explanation."""
