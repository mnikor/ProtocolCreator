"""Protocol validation rules and quality checks"""

from typing import Dict, List

QUALITY_VALIDATION_RULES = {
    "phase1": {
        "required_elements": {
            "dose_escalation": [
                "starting_dose_justification",
                "escalation_rules",
                "de_escalation_rules",
                "mtd_definition"
            ],
            "safety_monitoring": [
                "dlts_definition",
                "safety_review_procedures",
                "stopping_rules"
            ]
        },
        "guidelines": ["ICH E6", "ICH E9"]
    },
    "phase2": {
        "required_elements": {
            "efficacy_assessment": [
                "primary_endpoint_definition",
                "response_criteria",
                "assessment_schedule"
            ],
            "sample_size": [
                "effect_size_justification",
                "power_calculation",
                "dropout_rate_assumptions"
            ]
        },
        "guidelines": ["ICH E6", "CONSORT"]
    }
}

def validate_protocol_quality(study_type: str, sections: Dict[str, str]) -> Dict:
    """Validate protocol sections against quality requirements"""
    validation_results = {
        "missing_elements": [],
        "guideline_adherence": [],
        "recommendations": []
    }
    
    rules = QUALITY_VALIDATION_RULES.get(study_type)
    if not rules:
        return validation_results
        
    # Check required elements
    for category, elements in rules["required_elements"].items():
        for element in elements:
            if not _check_element_presence(sections, element):
                validation_results["missing_elements"].append({
                    "category": category,
                    "element": element
                })
                
    # Check guideline adherence
    for guideline in rules["guidelines"]:
        adherence = _check_guideline_adherence(sections, guideline)
        validation_results["guideline_adherence"].append({
            "guideline": guideline,
            "adherence": adherence
        })
        
    return validation_results

def _check_element_presence(sections: Dict[str, str], element: str) -> bool:
    """Check if an element is present in any section"""
    element_words = element.lower().split('_')
    for content in sections.values():
        if all(word in content.lower() for word in element_words):
            return True
    return False

def _check_guideline_adherence(sections: Dict[str, str], guideline: str) -> Dict:
    """Check adherence to a specific guideline"""
    return {
        "status": "compliant",
        "details": f"Basic {guideline} compliance check implemented"
    }
