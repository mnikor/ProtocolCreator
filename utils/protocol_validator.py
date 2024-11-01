from enum import Enum
from typing import Dict, List
import logging
import re

logger = logging.getLogger(__name__)

class IssueSeverity(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"

class ValidationDimension(Enum):
    SCIENTIFIC_RIGOR = "scientific_rigor"
    METHODOLOGY = "methodology" 
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    OPERATIONAL_FEASIBILITY = "operational_feasibility"
    ETHICAL_CONSIDERATIONS = "ethical_considerations"
    REPORTING_STANDARDS = "reporting_standards"

class ProtocolValidator:
    def __init__(self):
        self.validation_criteria = {
            ValidationDimension.SCIENTIFIC_RIGOR: {
                "items": [
                    "hypothesis_clarity",
                    "endpoint_justification",
                    "sample_size_rationale",
                    "bias_control_measures",
                    "analysis_plan_robustness"
                ],
                "weight": 0.25
            },
            ValidationDimension.METHODOLOGY: {
                "items": [
                    "design_appropriateness",
                    "methods_completeness",
                    "outcome_measures",
                    "data_collection_plan",
                    "quality_control_measures"
                ],
                "weight": 0.25
            },
            ValidationDimension.REGULATORY_COMPLIANCE: {
                "items": [
                    "ich_gcp_adherence",
                    "safety_reporting",
                    "protocol_structure",
                    "essential_documents",
                    "oversight_mechanisms"
                ],
                "weight": 0.15
            },
            ValidationDimension.OPERATIONAL_FEASIBILITY: {
                "items": [
                    "timeline_feasibility",
                    "resource_requirements",
                    "procedure_practicality",
                    "data_management_plan",
                    "site_requirements"
                ],
                "weight": 0.1
            },
            ValidationDimension.ETHICAL_CONSIDERATIONS: {
                "items": [
                    "risk_benefit_assessment",
                    "vulnerable_populations",
                    "informed_consent",
                    "confidentiality_measures",
                    "ethical_oversight"
                ],
                "weight": 0.15
            },
            ValidationDimension.REPORTING_STANDARDS: {
                "items": [
                    "guideline_adherence",
                    "complete_documentation",
                    "clarity_and_structure",
                    "consistency_internal",
                    "terminology_standard"
                ],
                "weight": 0.1
            }
        }

    def _check_item_presence(self, content: Dict[str, str], item: str) -> float:
        """Check if an item is adequately addressed in protocol content with weighted scoring"""
        if not content or not isinstance(content, dict):
            return 0.0
            
        # Convert item name to search terms
        search_terms = item.replace('_', ' ').lower().split()
        
        # Track presence and quality score
        max_section_score = 0.0
        
        for section_content in content.values():
            if not isinstance(section_content, str):
                continue
                
            content_lower = section_content.lower()
            
            # Calculate section score based on term presence and context
            section_score = 0.0
            if all(term in content_lower for term in search_terms):
                # Base score for having all terms
                section_score = 0.6
                
                # Additional score for proper context
                context_patterns = [
                    r"will be",
                    r"must be",
                    r"is required",
                    r"shall be",
                    r"has been",
                    r"is defined"
                ]
                
                for pattern in context_patterns:
                    if re.search(pattern, content_lower):
                        section_score += 0.1
                        
                # Cap at 1.0
                section_score = min(1.0, section_score)
                
            max_section_score = max(max_section_score, section_score)
                
        return max_section_score

    def validate_protocol(self, content: Dict[str, str], study_type: str) -> Dict:
        """Validate protocol across all dimensions"""
        validation_results = {
            "issues": [],
            "suggestions": [],
            "quality_score": 0.0
        }
        
        # Initialize overall metrics
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for dimension in ValidationDimension:
            dimension_results = self._validate_dimension(
                content, 
                study_type,
                dimension
            )
            validation_results[dimension.value] = dimension_results
            
            # Add to weighted total
            weight = self.validation_criteria[dimension].get("weight", 0.0)
            total_weighted_score += dimension_results["score"] * weight
            total_weight += weight
            
        # Add overall score if weights are valid
        if total_weight > 0:
            validation_results["quality_score"] = (total_weighted_score / total_weight) * 100
            
        return validation_results

    def _validate_dimension(self, content: Dict[str, str], study_type: str, 
                          dimension: ValidationDimension) -> Dict:
        """Validate specific dimension with improved scoring"""
        criteria = self.validation_criteria.get(dimension, {})
        results = {
            "missing_items": [],
            "recommendations": [],
            "score": 0.0,
            "item_scores": {}
        }

        # Check items with detailed scoring
        items = criteria.get("items", [])
        total_score = 0.0
        
        for item in items:
            item_score = self._check_item_presence(content, item)
            results["item_scores"][item] = item_score
            total_score += item_score
            
            if item_score < 0.6:  # Threshold for considering an item as missing
                results["missing_items"].append(item)
                results["recommendations"].append(
                    f"Improve {item.replace('_', ' ')} coverage and clarity"
                )

        # Calculate dimension score
        if items:
            results["score"] = total_score / len(items)
        
        # Add dimension-specific recommendations
        self._add_dimension_recommendations(results, dimension)

        return results

    def _add_dimension_recommendations(self, results: Dict, dimension: ValidationDimension):
        """Add specific recommendations based on dimension and scores"""
        score = results["score"]
        
        if score < 0.6:
            if dimension == ValidationDimension.SCIENTIFIC_RIGOR:
                results["recommendations"].append(
                    "Strengthen scientific rationale and methodology"
                )
            elif dimension == ValidationDimension.METHODOLOGY:
                results["recommendations"].append(
                    "Provide more detailed methods and procedures"
                )
            elif dimension == ValidationDimension.REGULATORY_COMPLIANCE:
                results["recommendations"].append(
                    "Ensure compliance with all regulatory requirements"
                )
            elif dimension == ValidationDimension.OPERATIONAL_FEASIBILITY:
                results["recommendations"].append(
                    "Add more details on implementation and resources"
                )
            elif dimension == ValidationDimension.ETHICAL_CONSIDERATIONS:
                results["recommendations"].append(
                    "Strengthen ethical considerations and protections"
                )
            elif dimension == ValidationDimension.REPORTING_STANDARDS:
                results["recommendations"].append(
                    "Improve adherence to reporting guidelines"
                )

    def generate_validation_report(self, validation_results: Dict) -> str:
        '''Generate human-readable validation report'''
        report = ["Protocol Validation Report\n"]
        
        # Add quality score
        report.append(f"Overall Quality Score: {validation_results['quality_score']:.2f}%\n")
        
        # Critical issues
        critical_issues = [i for i in validation_results.get("issues", []) 
                         if i.get("severity") == IssueSeverity.CRITICAL]
        if critical_issues:
            report.append("\n🚫 Critical Issues:")
            for issue in critical_issues:
                report.append(f"- {issue['message']}")
                if "suggestion" in issue:
                    report.append(f"  Suggestion: {issue['suggestion']}")
        
        # Major issues
        major_issues = [i for i in validation_results.get("issues", []) 
                       if i.get("severity") == IssueSeverity.MAJOR]
        if major_issues:
            report.append("\n⚠️ Major Issues:")
            for issue in major_issues:
                report.append(f"- {issue['message']}")
                if "suggestion" in issue:
                    report.append(f"  Suggestion: {issue['suggestion']}")
        
        # Minor issues and suggestions
        if validation_results.get("suggestions"):
            report.append("\n💡 Suggestions for Improvement:")
            for suggestion in validation_results["suggestions"]:
                report.append(f"- {suggestion}")
                
        return "\n".join(report)

    def validate_against_guidelines(self, content: str, section_name: str, guideline: str) -> Dict:
        '''Validate content against specific guideline requirements'''
        validation_results = {
            "missing_elements": [],
            "recommendations": []
        }
        
        # Basic guideline validation
        if not content:
            validation_results["missing_elements"].append(f"{section_name} content is empty")
            return validation_results
            
        # Check for guideline-specific elements
        guideline_elements = {
            "SPIRIT": ["objectives", "background", "methods", "population"],
            "PRISMA": ["search_strategy", "inclusion_criteria", "data_extraction"],
            "STROBE": ["study_design", "setting", "participants", "variables"],
            "RECORD": ["data_sources", "population", "variables", "statistical_methods"]
        }
        
        required_elements = guideline_elements.get(guideline, [])
        for element in required_elements:
            if element.lower() not in content.lower():
                validation_results["missing_elements"].append(
                    f"Missing {guideline} element: {element}"
                )
                validation_results["recommendations"].append(
                    f"Add section addressing {element}"
                )
        
        return validation_results
