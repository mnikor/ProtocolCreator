from enum import Enum
from typing import Dict, List
import logging
import re

logger = logging.getLogger(__name__)

# Guideline-specific validation rules
GUIDELINE_REQUIREMENTS = {
    'SPIRIT': {
        'background': [
            'scientific_background',
            'study_rationale',
            'risk_benefit_assessment'
        ],
        'objectives': [
            'primary_objective',
            'secondary_objectives',
            'trial_design'
        ],
        'methods': [
            'study_setting',
            'eligibility_criteria',
            'interventions',
            'outcomes',
            'sample_size',
            'recruitment'
        ]
    },
    'PRISMA': {
        'background': [
            'rationale',
            'objectives',
            'research_question'
        ],
        'methods': [
            'eligibility_criteria',
            'information_sources',
            'search_strategy',
            'study_selection',
            'data_extraction',
            'quality_assessment'
        ]
    },
    'STROBE': {
        'background': [
            'scientific_background',
            'study_objectives',
            'pre_existing_hypotheses'
        ],
        'methods': [
            'study_design',
            'setting',
            'participants',
            'variables',
            'data_sources',
            'bias_assessment'
        ]
    }
}

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
                ]
            },
            ValidationDimension.METHODOLOGY: {
                "items": [
                    "design_appropriateness",
                    "methods_completeness",
                    "outcome_measures",
                    "data_collection_plan",
                    "quality_control_measures"
                ]
            },
            ValidationDimension.REGULATORY_COMPLIANCE: {
                "items": [
                    "ich_gcp_adherence",
                    "safety_reporting",
                    "protocol_structure",
                    "essential_documents",
                    "oversight_mechanisms"
                ]
            }
        }

    def _check_item_presence(self, content: Dict[str, str], item: str) -> bool:
        '''Check if an item is adequately addressed in protocol content'''
        if not content or not isinstance(content, dict):
            return False
            
        # Convert item name to search terms
        search_terms = item.replace('_', ' ').lower().split()
        
        # Check each section's content
        for section_content in content.values():
            if not isinstance(section_content, str):
                continue
                
            content_lower = section_content.lower()
            if all(term in content_lower for term in search_terms):
                return True
                
        return False

    def validate_protocol(self, content: Dict, study_type: str) -> Dict:
        """Validate protocol across all dimensions"""
        validation_results = {}
        
        for dimension in ValidationDimension:
            dimension_results = self._validate_dimension(
                content, 
                study_type,
                dimension
            )
            validation_results[dimension.value] = dimension_results
            
        return validation_results

    def _validate_dimension(self, content: Dict, study_type: str, 
                          dimension: ValidationDimension) -> Dict:
        """Validate specific dimension"""
        criteria = self.validation_criteria.get(dimension, {})
        results = {
            "missing_items": [],
            "recommendations": [],
            "score": 0.0
        }

        # Check common items
        items = criteria.get("items", [])
        for item in items:
            if not self._check_item_presence(content, item):
                results["missing_items"].append(item)

        # Calculate dimension score
        total_items = len(items)
        missing_items = len(results["missing_items"])
        results["score"] = (total_items - missing_items) / total_items if total_items > 0 else 0.0

        # Generate recommendations
        results["recommendations"] = [
            f"Add {item.replace('_', ' ')}" for item in results["missing_items"]
        ]

        return results

    def generate_validation_report(self, validation_results: Dict) -> str:
        """Generate readable validation report"""
        report = ["Protocol Validation Report\n"]
        
        # Overall score
        overall_score = self._calculate_overall_score(validation_results)
        report.append(f"Overall Quality Score: {overall_score:.2%}\n")
        
        # Dimension-specific results
        for dimension, results in validation_results.items():
            report.append(f"\n{dimension.replace('_', ' ').title()} (Score: {results['score']:.2%})")
            
            if results.get("missing_items"):
                report.append("\nMissing Items:")
                for item in results["missing_items"]:
                    report.append(f"- {item}")
                    
            if results.get("recommendations"):
                report.append("\nRecommendations:")
                for rec in results["recommendations"]:
                    report.append(f"- {rec}")
                    
        return "\n".join(report)

    def _calculate_overall_score(self, validation_results: Dict) -> float:
        """Calculate overall protocol quality score"""
        scores = [results.get("score", 0.0) for results in validation_results.values()]
        return sum(scores) / len(scores) if scores else 0.0

    def validate_against_guidelines(self, content: str, section_name: str, guideline: str) -> Dict:
        """Validate section content against specific guideline requirements"""
        try:
            validation_results = {
                "missing_elements": [],
                "recommendations": [],
                "guideline": guideline,
                "compliance_score": 0.0
            }

            # Get guideline-specific requirements for the section
            requirements = GUIDELINE_REQUIREMENTS.get(guideline, {}).get(section_name, [])
            if not requirements:
                logger.info(f"No specific {guideline} requirements for {section_name}")
                return validation_results

            # Check each required element
            found_elements = 0
            for element in requirements:
                if not self._check_element_presence(content, element):
                    validation_results["missing_elements"].append(element)
                    validation_results["recommendations"].append(
                        f"Add {element.replace('_', ' ')} to comply with {guideline} guidelines"
                    )
                else:
                    found_elements += 1

            # Calculate compliance score
            validation_results["compliance_score"] = found_elements / len(requirements)
            logger.info(f"{guideline} compliance score for {section_name}: {validation_results['compliance_score']:.2%}")

            return validation_results

        except Exception as e:
            logger.error(f"Error in guideline validation: {str(e)}")
            return {
                "missing_elements": [],
                "recommendations": [f"Error in validation: {str(e)}"],
                "guideline": guideline,
                "compliance_score": 0.0
            }

    def _check_element_presence(self, content: str, element: str) -> bool:
        """Check if an element is present in the content"""
        if not content or not isinstance(content, str):
            return False

        # Convert element name to search terms
        search_terms = element.replace('_', ' ').lower().split()
        content_lower = content.lower()

        # Check for presence of all search terms
        return all(term in content_lower for term in search_terms)
