from typing import Dict, Optional, List
from utils.missing_information_handler import MissingInformationHandler
from utils.gpt_handler import GPTHandler
import logging

logger = logging.getLogger(__name__)

class ProtocolImprover:
    def __init__(self):
        """Initialize improver with handlers"""
        self.missing_info_handler = MissingInformationHandler()
        self.gpt_handler = GPTHandler()
    
    def _validate_section_requirements(self, section_name: str, content: str, study_type: str, results: Dict):
        """Check section-specific requirements"""
        section_requirements = {
            "objectives": {
                "required_elements": ["primary_objective", "secondary_objectives"],
                "forbidden_terms": ["tbd", "to be determined", "placeholder"],
                "min_length": 200
            },
            "study_design": {
                "required_elements": ["design_type", "duration", "population"],
                "study_type_specific": {
                    "phase1": ["dose_escalation", "safety_monitoring"],
                    "phase2": ["endpoints", "sample_size"],
                    "phase3": ["randomization", "blinding", "interim_analysis"],
                    "phase4": ["real_world_setting", "comparator"]
                }
            }
        }

        # Add study type-specific validation rules
        invalid_elements = {
            'secondary_rwe': {
                'forbidden_terms': ['unblinding', 'dsmb', 'interim analysis', 'stopping rules'],
                'message': 'Contains elements not applicable to secondary RWE studies'
            },
            'systematic_review': {
                'forbidden_terms': ['randomization', 'blinding', 'dose escalation'],
                'message': 'Contains elements not applicable to systematic reviews'
            },
            'observational': {
                'forbidden_terms': ['randomization', 'blinding', 'placebo'],
                'message': 'Contains elements not applicable to observational studies'
            }
        }
        
        # Check study type-specific invalid elements
        if study_type in invalid_elements:
            rules = invalid_elements[study_type]
            for term in rules['forbidden_terms']:
                if term.lower() in content.lower():
                    results["issues"].append({
                        "type": "inappropriate_content",
                        "severity": "critical",
                        "message": f"{rules['message']}: '{term}'",
                        "suggestion": f"Remove or replace content about {term} as it's not applicable for {study_type} studies"
                    })
        
        if section_name in section_requirements:
            reqs = section_requirements[section_name]
            
            # Check required elements
            for element in reqs["required_elements"]:
                if element.lower() not in content.lower():
                    results["issues"].append({
                        "type": element,
                        "severity": "critical",
                        "message": f"Missing required element '{element}' in {section_name}",
                        "suggestion": f"Add {element} to section"
                    })
            
            # Check study type specific requirements
            if "study_type_specific" in reqs and study_type in reqs["study_type_specific"]:
                for element in reqs["study_type_specific"][study_type]:
                    if element.lower() not in content.lower():
                        results["issues"].append({
                            "type": element,
                            "severity": "major",
                            "message": f"Missing {study_type}-specific element '{element}' in {section_name}",
                            "suggestion": f"Add {element} as required for {study_type} studies"
                        })

    def validate_section(self, section_name: str, content: str, study_type: str) -> Dict:
        """Validate individual protocol section"""
        results = {
            "issues": [],
            "severity_counts": {
                "critical": 0,
                "major": 0,
                "minor": 0
            }
        }

        # Validate section requirements
        self._validate_section_requirements(section_name, content, study_type, results)

        # Count issues by severity
        for issue in results["issues"]:
            severity = issue.get("severity", "minor")
            results["severity_counts"][severity] += 1

        return results
