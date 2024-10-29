SYNOPSIS_ANALYSIS_PROMPT = """
As a medical writer, analyze the following clinical study synopsis and provide a structured JSON output:

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
}"""
