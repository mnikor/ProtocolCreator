# study_type_definitions.py

COMPREHENSIVE_STUDY_CONFIGS = {
    "phase1": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",
            "safety"
        ],
        "subsections": {
            "background": [
                "disease_background",
                "compound_background",
                "preclinical_data",
                "clinical_data",
                "dose_rationale",
                "risk_benefit_assessment"
            ],
            "objectives": [
                "primary_objectives",
                "secondary_objectives",
                "exploratory_objectives",
                "primary_endpoints",
                "secondary_endpoints",
                "exploratory_endpoints"
            ],
            "study_design": [
                "overall_design",
                "dose_escalation_strategy",
                "mtd_determination",
                "cohort_definitions",
                "study_duration",
                "treatment_schedule"
            ],
            "population": [
                "inclusion_criteria",
                "exclusion_criteria",
                "withdrawal_criteria",
                "dose_limiting_toxicity_criteria",
                "replacement_procedures"
            ],
            "procedures": [
                "screening_procedures",
                "treatment_procedures",
                "safety_monitoring",
                "pharmacokinetic_procedures",
                "biomarker_procedures",
                "follow_up_procedures"
            ],
            "statistical_analysis": [
                "sample_size_rationale",
                "safety_analysis",
                "pk_analysis",
                "biomarker_analysis",
                "interim_analyses",
                "dose_escalation_rules"
            ],
            "safety": [
                "safety_parameters",
                "adverse_event_reporting",
                "dose_modifications",
                "stopping_rules",
                "safety_review_committee"
            ]
        }
    },

    "phase2": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",
            "safety"
        ],
        "subsections": {
            "background": [
                "disease_background",
                "treatment_landscape",
                "compound_background",
                "phase1_results",
                "study_rationale",
                "risk_benefit_assessment"
            ],
            "objectives": [
                "primary_objectives",
                "secondary_objectives",
                "exploratory_objectives",
                "primary_endpoints",
                "secondary_endpoints",
                "exploratory_endpoints"
            ],
            "study_design": [
                "overall_design",
                "treatment_groups",
                "randomization",
                "blinding",
                "study_duration",
                "treatment_schedule"
            ],
            "population": [
                "target_population",
                "inclusion_criteria",
                "exclusion_criteria",
                "withdrawal_criteria",
                "stratification_factors",
                "replacement_procedures"
            ],
            "procedures": [
                "screening_procedures",
                "treatment_procedures",
                "efficacy_assessments",
                "safety_assessments",
                "biomarker_procedures",
                "follow_up_procedures"
            ],
            "statistical_analysis": [
                "sample_size_calculation",
                "analysis_populations",
                "efficacy_analysis",
                "safety_analysis",
                "interim_analyses",
                "multiplicity_adjustments"
            ],
            "safety": [
                "safety_parameters",
                "adverse_event_reporting",
                "dose_modifications",
                "risk_mitigation",
                "data_monitoring_committee"
            ]
        }
    },

    "phase3": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",
            "safety"
        ],
        "subsections": {
            "background": [
                "disease_background",
                "treatment_landscape",
                "unmet_medical_need",
                "compound_background",
                "clinical_evidence",
                "study_rationale"
            ],
            "objectives": [
                "primary_objectives",
                "secondary_objectives",
                "exploratory_objectives",
                "primary_endpoints",
                "secondary_endpoints",
                "exploratory_endpoints",
                "substudy_objectives"
            ],
            "study_design": [
                "overall_design",
                "randomization",
                "blinding",
                "treatment_groups",
                "stratification",
                "study_schema",
                "study_duration"
            ],
            "population": [
                "target_population",
                "inclusion_criteria",
                "exclusion_criteria",
                "lifestyle_restrictions",
                "withdrawal_criteria",
                "rescue_medication",
                "concomitant_medications"
            ],
            "procedures": [
                "screening_procedures",
                "treatment_procedures",
                "efficacy_assessments",
                "safety_assessments",
                "quality_of_life_assessments",
                "pharmacoeconomic_assessments",
                "follow_up_procedures"
            ],
            "statistical_analysis": [
                "sample_size_calculation",
                "analysis_populations",
                "primary_analysis",
                "secondary_analyses",
                "safety_analysis",
                "interim_analyses",
                "multiplicity_adjustments",
                "missing_data_handling",
                "subgroup_analyses"
            ],
            "safety": [
                "safety_parameters",
                "adverse_event_definitions",
                "adverse_event_reporting",
                "serious_adverse_events",
                "adverse_events_of_special_interest",
                "pregnancy_reporting",
                "data_monitoring_committee",
                "stopping_rules"
            ]
        }
    },

    "phase4": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",
            "safety",
            "pharmacoeconomics"
        ],
        "subsections": {
            "background": [
                "disease_background",
                "treatment_landscape",
                "product_experience",
                "real_world_evidence",
                "study_rationale"
            ],
            "objectives": [
                "primary_objectives",
                "secondary_objectives",
                "exploratory_objectives",
                "pharmacoeconomic_objectives",
                "quality_of_life_objectives"
            ],
            "study_design": [
                "overall_design",
                "treatment_setting",
                "prescribing_patterns",
                "study_duration",
                "follow_up_schedule"
            ],
            "population": [
                "target_population",
                "inclusion_criteria",
                "exclusion_criteria",
                "special_populations",
                "withdrawal_criteria"
            ],
            "procedures": [
                "prescribing_procedures",
                "safety_monitoring",
                "effectiveness_assessments",
                "quality_of_life_assessments",
                "resource_utilization_assessments"
            ],
            "statistical_analysis": [
                "sample_size_rationale",
                "effectiveness_analysis",
                "safety_analysis",
                "pharmacoeconomic_analysis",
                "subgroup_analyses"
            ],
            "safety": [
                "pharmacovigilance_plan",
                "adverse_event_reporting",
                "periodic_safety_updates",
                "risk_management"
            ],
            "pharmacoeconomics": [
                "cost_effectiveness_analysis",
                "resource_utilization",
                "quality_of_life_analysis",
                "healthcare_costs"
            ]
        }
    },

    "observational": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "population",
            "variables",
            "data_collection",
            "statistical_analysis",
            "limitations",
            "ethics"
        ],
        "subsections": {
            "background": [
                "research_context",
                "current_evidence",
                "knowledge_gaps",
                "study_rationale"
            ],
            "objectives": [
                "primary_objectives",
                "secondary_objectives",
                "exploratory_objectives"
            ],
            "study_design": [
                "study_type",
                "setting",
                "timeline",
                "exposure_definition",
                "outcome_definition",
                "bias_assessment"
            ],
            "population": [
                "source_population",
                "eligibility_criteria",
                "sampling_strategy",
                "sample_size_justification"
            ],
            "variables": [
                "exposure_variables",
                "outcome_variables",
                "confounding_variables",
                "effect_modifiers"
            ],
            "data_collection": [
                "data_sources",
                "measurement_methods",
                "quality_control",
                "validation_procedures"
            ],
            "statistical_analysis": [
                "descriptive_analysis",
                "main_analysis",
                "confounding_control",
                "sensitivity_analyses",
                "missing_data"
            ],
            "limitations": [
                "potential_biases",
                "confounding_factors",
                "generalizability",
                "data_quality"
            ],
            "ethics": [
                "ethical_considerations",
                "data_privacy",
                "informed_consent",
                "regulatory_compliance"
            ]
        }
    },

    "rwe": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "data_sources",
            "population",
            "variables",
            "statistical_analysis",
            "limitations",
            "data_management"
        ],
        "subsections": {
            "background": [
                "clinical_context",
                "evidence_gaps",
                "regulatory_context",
                "study_rationale"
            ],
            "objectives": [
                "primary_objectives",
                "secondary_objectives",
                "exploratory_objectives"
            ],
            "study_design": [
                "study_type",
                "data_linkage",
                "study_period",
                "index_date_definition"
            ],
            "data_sources": [
                "database_descriptions",
                "data_quality_assessment",
                "validation_status",
                "coding_systems"
            ],
            "population": [
                "target_population",
                "eligibility_criteria",
                "cohort_definitions",
                "sample_size_considerations"
            ],
            "variables": [
                "exposure_definitions",
                "outcome_definitions",
                "covariates",
                "operational_definitions"
            ],
            "statistical_analysis": [
                "primary_analysis",
                "secondary_analyses",
                "sensitivity_analyses",
                "missing_data_handling",
                "subgroup_analyses"
            ],
            "limitations": [
                "data_limitations",
                "measurement_bias",
                "confounding",
                "generalizability"
            ],
            "data_management": [
                "data_quality_control",
                "data_cleaning",
                "documentation",
                "data_security"
            ]
        }
    }
}

# Additional configurations for prompts, validation rules, etc. would follow...
