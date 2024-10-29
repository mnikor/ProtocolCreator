SYNOPSIS_ANALYSIS_PROMPT = '''
Analyze the following synopsis and output a JSON object with this exact structure. 
Do not include any additional text, only the JSON object:

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
