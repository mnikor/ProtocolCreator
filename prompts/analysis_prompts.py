SYNOPSIS_ANALYSIS_PROMPT = '''
Analyze the following synopsis and return a JSON object following these rules:
1. Response must be a single valid JSON object
2. Do not include any text before or after the JSON
3. Follow this exact structure:
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

Synopsis to analyze:
{synopsis_text}
'''
