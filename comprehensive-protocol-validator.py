# protocol_validator.py

from enum import Enum
from typing import Dict, List

class IssueType(Enum):
    # Content Issues
    MISSING_ELEMENT = "missing_element"
    INCONSISTENCY = "inconsistency"
    INCOMPLETE = "incomplete"

    # Scientific Issues
    METHODOLOGY = "methodology_issue"
    STATISTICAL = "statistical_issue"
    BIAS = "bias_issue"

    # Language Issues
    TONE = "inappropriate_tone"
    FORMALITY = "formality_issue"
    CLARITY = "clarity_issue"

    # Compliance Issues
    REGULATORY = "regulatory_issue"
    ETHICAL = "ethical_issue"
    REPORTING = "reporting_issue"

class IssueSeverity(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"

class ProtocolValidator:
    def __init__(self):
        self.validation_rules = self._load_validation_rules()

    def _load_validation_rules(self):
        return {
            # Content validation rules
            "content": {
                "required_elements": self._get_required_elements(),
                "consistency_checks": self._get_consistency_rules(),
                "completeness_checks": self._get_completeness_rules()
            },
            # Language validation rules
            "language": {
                "inappropriate_terms": [
                    "kind of", "sort of", "basically", "pretty much"
                ],
                "informal_terms": {
                    "find out": "determine",
                    "look at": "examine",
                    "check": "evaluate"
                },
                "precise_terms": {
                    "several": "specify number",
                    "many": "specify number",
                    "some": "specify amount"
                }
            },
            # Scientific validation rules by study type
            "scientific": {
                "methodology_requirements": self._get_methodology_rules(),
                "statistical_requirements": self._get_statistical_rules(),
                "bias_controls": self._get_bias_rules(),
                "study_specific": {
                    "phase1": {
                        "internal_validity": {
                            "critical": [
                                "safety_assessment_methods",
                                "dose_escalation_rules",
                                "adverse_event_monitoring"
                            ],
                            "major": [
                                "standardized_procedures",
                                "data_quality_control"
                            ]
                        },
                        "external_validity": {
                            "critical": ["population_safety_relevance"],
                            "major": ["setting_feasibility"]
                        }
                    },
                    "phase2": {
                        "internal_validity": {
                            "critical": [
                                "endpoint_measurement",
                                "bias_control_methods",
                                "data_quality_assurance"
                            ],
                            "major": [
                                "randomization_procedures",
                                "blinding_methods"
                            ]
                        },
                        "external_validity": {
                            "critical": [
                                "target_population_representation",
                                "clinical_setting_applicability"
                            ]
                        }
                    },
                    "phase3": {
                        "internal_validity": {
                            "critical": [
                                "randomization_method",
                                "blinding_procedures",
                                "primary_outcome_assessment"
                            ],
                            "major": [
                                "allocation_concealment",
                                "protocol_compliance"
                            ]
                        },
                        "external_validity": {
                            "critical": [
                                "population_generalizability",
                                "site_representation"
                            ]
                        }
                    },
                    "phase4": {
                        "internal_validity": {
                            "critical": [
                                "safety_monitoring_system",
                                "effectiveness_measures",
                                "data_quality_control",
                                "adverse_event_capture"
                            ],
                            "major": [
                                "protocol_compliance",
                                "followup_completeness"
                            ]
                        },
                        "external_validity": {
                            "critical": [
                                "real_world_population",
                                "practice_setting_diversity",
                                "treatment_pattern_relevance"
                            ]
                        }
                    },
                    "systematic_review": {
                        "internal_validity": {
                            "critical": [
                                "search_strategy_completeness",
                                "study_selection_criteria",
                                "quality_assessment_method",
                                "bias_assessment_approach"
                            ],
                            "major": [
                                "data_extraction_process",
                                "reviewer_agreement"
                            ]
                        },
                        "external_validity": {
                            "critical": [
                                "question_relevance",
                                "population_coverage",
                                "outcome_applicability"
                            ]
                        }
                    },
                    "secondary_rwe": {
                        "internal_validity": {
                            "critical": [
                                "data_source_quality",
                                "variable_definitions",
                                "missing_data_assessment",
                                "bias_control_strategy"
                            ],
                            "major": [
                                "coding_validation",
                                "temporal_relationships"
                            ]
                        },
                        "external_validity": {
                            "critical": [
                                "database_representativeness",
                                "population_coverage",
                                "healthcare_setting_relevance"
                            ]
                        }
                    }
                }
            },
            # Compliance validation rules
            "compliance": {
                "regulatory_requirements": self._get_regulatory_rules(),
                "ethical_requirements": self._get_ethical_rules(),
                "reporting_standards": self._get_reporting_rules()
            }
        }

    def _get_required_elements(self) -> Dict:
        """Get study type specific required elements"""
        return {
            "phase1": ["safety", "dose_escalation", "pharmacokinetics"],
            "phase2": ["efficacy", "safety", "statistical_analysis"],
            "phase3": ["efficacy", "safety", "statistical_analysis", "quality_of_life"],
            "phase4": ["effectiveness", "safety", "utilization"],
            "systematic_review": ["search_strategy", "selection_criteria", "quality_assessment"],
            "secondary_rwe": ["data_source", "variables", "analysis_plan"]
        }

    def validate_protocol(self, content: Dict, study_type: str) -> Dict:
        """Perform comprehensive protocol validation"""
        validation_results = {
            "issues": [],
            "warnings": [],
            "suggestions": [],
            "quality_score": 0.0
        }

        # 1. Content Validation
        self._validate_content(content, study_type, validation_results)

        # 2. Scientific Validation
        self._validate_scientific_rigor(content, study_type, validation_results)

        # 3. Language Validation
        self._validate_language(content, validation_results)

        # 4. Compliance Validation
        self._validate_compliance(content, study_type, validation_results)

        # Calculate overall quality score
        validation_results["quality_score"] = self._calculate_quality_score(validation_results)

        return validation_results

    def _validate_content(self, content: Dict, study_type: str, results: Dict):
        """Validate content completeness and consistency"""
        required = self.validation_rules["content"]["required_elements"].get(study_type, [])
        for element in required:
            if element not in content:
                results["issues"].append({
                    "type": IssueType.MISSING_ELEMENT,
                    "severity": IssueSeverity.CRITICAL,
                    "message": f"Missing required element: {element}",
                    "location": "structure",
                    "suggestion": f"Add {element} section"
                })

    def _validate_scientific_rigor(self, content: Dict, study_type: str, results: Dict):
        """Validate scientific methodology and rigor"""
        study_rules = self.validation_rules["scientific"]["study_specific"].get(study_type, {})

        # Check internal validity
        for severity in ["critical", "major"]:
            for requirement in study_rules.get("internal_validity", {}).get(severity, []):
                if not self._check_requirement(content, requirement):
                    results["issues"].append(self._create_validity_issue(
                        requirement, "internal", severity, study_type
                    ))

        # Check external validity
        for severity in ["critical", "major"]:
            for requirement in study_rules.get("external_validity", {}).get(severity, []):
                if not self._check_requirement(content, requirement):
                    results["issues"].append(self._create_validity_issue(
                        requirement, "external", severity, study_type
                    ))

    def _create_validity_issue(self, requirement: str, validity_type: str, 
                             severity: str, study_type: str) -> Dict:
        """Create a validity issue with appropriate recommendation"""
        recommendations = self._get_validity_recommendations(study_type)
        rec = recommendations.get(requirement, {})

        return {
            "type": IssueType.METHODOLOGY,
            "severity": IssueSeverity.CRITICAL if severity == "critical" else IssueSeverity.MAJOR,
            "message": rec.get("message", f"Missing {validity_type} validity requirement: {requirement}"),
            "location": "methods",
            "suggestion": rec.get("recommendation", f"Add details about {requirement}")
        }

    def _calculate_quality_score(self, results: Dict) -> float:
        """Calculate overall quality score based on validation results"""
        critical_issues = len([i for i in results["issues"] 
                             if i["severity"] == IssueSeverity.CRITICAL])
        major_issues = len([i for i in results["issues"] 
                          if i["severity"] == IssueSeverity.MAJOR])

        base_score = 100
        critical_penalty = critical_issues * 15
        major_penalty = major_issues * 5

        return max(0, min(100, base_score - critical_penalty - major_penalty))

    def generate_validation_report(self, validation_results: Dict) -> str:
        """Generate human-readable validation report"""
        report = ["Protocol Validation Report\n"]

        # Add quality score
        report.append(f"Overall Quality Score: {validation_results['quality_score']:.2f}%\n")

        # Critical issues
        critical_issues = [i for i in validation_results["issues"] 
                         if i["severity"] == IssueSeverity.CRITICAL]
        if critical_issues:
            report.append("\n🚫 Critical Issues:")
            for issue in critical_issues:
                report.append(f"- {issue['message']}")
                if "suggestion" in issue:
                    report.append(f"  Suggestion: {issue['suggestion']}")

        # Major issues
        major_issues = [i for i in validation_results["issues"] 
                       if i["severity"] == IssueSeverity.MAJOR]
        if major_issues:
            report.append("\n⚠️ Major Issues:")
            for issue in major_issues:
                report.append(f"- {issue['message']}")
                if "suggestion" in issue:
                    report.append(f"  Suggestion: {issue['suggestion']}")

        # Minor issues and suggestions
        if validation_results["suggestions"]:
            report.append("\n💡 Suggestions for Improvement:")
            for suggestion in validation_results["suggestions"]:
                report.append(f"- {suggestion}")

        return "\n".join(report)

    # Add placeholder methods that need to be implemented based on your specific needs
    def _get_consistency_rules(self) -> Dict:
        return {}

    def _get_completeness_rules(self) -> Dict:
        return {}

    def _get_methodology_rules(self) -> Dict:
        return {}

    def _get_statistical_rules(self) -> Dict:
        return {}

    def _get_bias_rules(self) -> Dict:
        return {}

    def _get_regulatory_rules(self) -> Dict:
        return {}

    def _get_ethical_rules(self) -> Dict:
        return {}

    def _get_reporting_rules(self) -> Dict:
        return {}

    def _check_requirement(self, content: Dict, requirement: str) -> bool:
        # Implement requirement checking logic
        return True

    def _get_validity_recommendations(self, study_type: str) -> Dict:
        # Implement recommendations lookup
        return {}