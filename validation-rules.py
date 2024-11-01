# validation_rules.py

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
    },
    "phase3": {
        "required_elements": {
            "randomization": [
                "randomization_method",
                "stratification_factors",
                "allocation_concealment"
            ],
            "blinding": [
                "blinding_procedures",
                "unblinding_procedures",
                "emergency_unblinding"
            ]
        },
        "guidelines": ["ICH E6", "ICH E9", "CONSORT"]
    },
    "observational": {
        "required_elements": {
            "bias_assessment": [
                "selection_bias",
                "information_bias",
                "confounding_assessment"
            ],
            "data_quality": [
                "validation_methods",
                "missing_data_assessment",
                "data_completeness"
            ]
        },
        "guidelines": ["STROBE", "RECORD"]
    },
    "rwe": {
        "required_elements": {
            "data_sources": [
                "database_characteristics",
                "coding_systems",
                "data_quality_metrics"
            ],
            "operational_definitions": [
                "exposure_algorithms",
                "outcome_algorithms",
                "validation_status"
            ]
        },
        "guidelines": ["RECORD", "ENCePP"]
    }
}

def validate_protocol_quality(study_type, sections):
    """
    Validate protocol sections against quality requirements
    """
    validation_results = {
        "missing_elements": [],
        "guideline_adherence": [],
        "recommendations": []
    }
    
    # Get validation rules for study type
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
