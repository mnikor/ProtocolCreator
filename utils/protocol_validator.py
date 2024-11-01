import logging
from enum import Enum
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class StudyCategory(Enum):
    INTERVENTIONAL = "interventional"
    SECONDARY_RESEARCH = "secondary_research"

class StudyType(Enum):
    PHASE1 = ("phase1", StudyCategory.INTERVENTIONAL)
    PHASE2 = ("phase2", StudyCategory.INTERVENTIONAL)
    PHASE3 = ("phase3", StudyCategory.INTERVENTIONAL)
    PHASE4 = ("phase4", StudyCategory.INTERVENTIONAL)
    RWE = ("rwe", StudyCategory.SECONDARY_RESEARCH)
    SLR = ("slr", StudyCategory.SECONDARY_RESEARCH)
    META = ("meta", StudyCategory.SECONDARY_RESEARCH)

    def __init__(self, type_name: str, category: StudyCategory):
        self.type_name = type_name
        self.category = category

class ProtocolValidator:
    def __init__(self):
        """Initialize validator with guideline requirements"""
        self.guideline_requirements = {
            "SPIRIT": {
                "required_elements": [
                    "objectives", "background", "methods", "population",
                    "intervention", "outcomes", "statistical_analysis"
                ]
            },
            "PRISMA": {
                "required_elements": [
                    "search_strategy", "inclusion_criteria", "data_extraction",
                    "quality_assessment", "synthesis_methods"
                ]
            },
            "STROBE": {
                "required_elements": [
                    "study_design", "setting", "participants", "variables",
                    "data_sources", "bias", "statistical_methods"
                ]
            },
            "RECORD": {
                "required_elements": [
                    "data_sources", "population", "variables", "statistical_methods",
                    "data_cleaning", "linkage", "sensitivity_analyses"
                ]
            }
        }

    def validate_against_guidelines(self, content: str, section_name: str, guideline: str) -> Dict:
        """Validate content against specific guideline requirements"""
        validation_results = {
            "missing_elements": [],
            "recommendations": []
        }
        
        try:
            if not content:
                validation_results["missing_elements"].append(
                    f"{section_name} content is empty"
                )
                return validation_results
                
            required_elements = self.guideline_requirements.get(guideline, {}).get("required_elements", [])
            for element in required_elements:
                if element.lower() not in content.lower():
                    validation_results["missing_elements"].append(
                        f"Missing {guideline} element: {element}"
                    )
                    validation_results["recommendations"].append(
                        f"Add section addressing {element}"
                    )
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error in guideline validation: {str(e)}")
            return validation_results

    def validate_protocol(self, content: Dict[str, str], study_type: str) -> Dict:
        try:
            # Normalize study type
            study_type = study_type.lower()
            study_enum = self._get_study_type(study_type)
            
            validation_results = {}
            total_score = 0.0
            total_weight = 0.0
            
            # Scientific Rigor validation
            scientific_results = self._validate_dimension(content, "scientific_rigor")
            validation_results["scientific_rigor"] = scientific_results
            total_score += scientific_results["score"] * 0.4
            total_weight += 0.4
            
            # Methodology validation
            methodology_results = self._validate_dimension(content, "methodology")
            validation_results["methodology"] = methodology_results
            total_score += methodology_results["score"] * 0.3
            total_weight += 0.3
            
            # Compliance validation
            compliance_results = self._validate_dimension(content, "regulatory_compliance")
            validation_results["regulatory_compliance"] = compliance_results
            total_score += compliance_results["score"] * 0.3
            total_weight += 0.3
            
            # Calculate overall score
            validation_results["overall_score"] = (total_score / total_weight) * 100 if total_weight > 0 else 0.0
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error in protocol validation: {str(e)}")
            return {"overall_score": 0.0}

    def _validate_dimension(self, content: Dict[str, str], dimension: str) -> Dict:
        '''Validate a specific dimension of the protocol'''
        dimension_scores = {
            "scientific_rigor": {
                "required_elements": [
                    "objectives", "hypothesis", "endpoints", 
                    "sample_size", "analysis", "methods"
                ],
                "weight": 0.4
            },
            "methodology": {
                "required_elements": [
                    "population", "criteria", "procedures",
                    "statistical", "data_collection"
                ],
                "weight": 0.3
            },
            "regulatory_compliance": {
                "required_elements": [
                    "ethical", "safety", "monitoring",
                    "consent", "privacy"
                ],
                "weight": 0.3
            }
        }
        
        if dimension not in dimension_scores:
            return {"score": 0.0, "missing_items": [], "recommendations": []}
        
        required_elements = dimension_scores[dimension]["required_elements"]
        missing_items = []
        recommendations = []
        
        # Check each required element
        found_elements = 0
        for element in required_elements:
            found = False
            for section_content in content.values():
                if isinstance(section_content, str) and element.lower() in section_content.lower():
                    found = True
                    found_elements += 1
                    break
            
            if not found:
                missing_items.append(f"Missing {element}")
                recommendations.append(f"Add section addressing {element}")
        
        score = found_elements / len(required_elements) if required_elements else 0.0
        
        return {
            "score": score,
            "missing_items": missing_items,
            "recommendations": recommendations
        }

    def generate_validation_report(self, validation_results: Dict) -> str:
        """Generate human-readable validation report"""
        report = ["Protocol Validation Report\n"]
        
        # Add overall score
        overall_score = validation_results.get("overall_score", 0.0)
        report.append(f"Overall Quality Score: {overall_score:.2f}%\n")
        
        # Add dimension results
        for dim_name, dim_results in validation_results.items():
            if isinstance(dim_results, dict) and dim_name != "overall_score":
                report.append(f"\n{dim_name.replace('_', ' ').title()} Assessment:")
                report.append(f"Score: {dim_results.get('score', 0.0):.2%}")
                
                if dim_results.get("missing_items"):
                    report.append("\nMissing Elements:")
                    for elem in dim_results["missing_items"]:
                        report.append(f"- {elem}")
                
                if dim_results.get("recommendations"):
                    report.append("\nRecommendations:")
                    for rec in dim_results["recommendations"]:
                        report.append(f"- {rec}")
        
        return "\n".join(report)

    def _get_study_type(self, study_type: str) -> StudyType:
        """Get study type enum from string"""
        try:
            return next(st for st in StudyType 
                       if st.type_name == study_type.lower())
        except StopIteration:
            raise ValueError(f"Unknown study type: {study_type}")
