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
            # Basic guideline validation
            if not content:
                validation_results["missing_elements"].append(
                    f"{section_name} content is empty"
                )
                return validation_results
                
            # Get guideline-specific elements
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
        """Main validation method"""
        try:
            # Normalize study type
            study_type = study_type.lower()
            study_enum = self._get_study_type(study_type)
            
            validation_results = {
                "dimensions": {},
                "overall_score": 0.0
            }

            # Validate scientific rigor
            scientific_score = self._validate_scientific_rigor(content)
            validation_results["dimensions"]["scientific_rigor"] = {
                "score": scientific_score,
                "weight": 0.4
            }

            # Validate methodology
            methodology_score = self._validate_methodology(content)
            validation_results["dimensions"]["methodology"] = {
                "score": methodology_score,
                "weight": 0.3
            }

            # Validate regulatory compliance
            compliance_score = self._validate_compliance(content)
            validation_results["dimensions"]["regulatory_compliance"] = {
                "score": compliance_score,
                "weight": 0.3
            }

            # Calculate overall score
            total_score = (
                scientific_score * 0.4 +
                methodology_score * 0.3 +
                compliance_score * 0.3
            )
            validation_results["overall_score"] = total_score * 100

            return validation_results

        except Exception as e:
            logger.error(f"Error in protocol validation: {str(e)}")
            return {"overall_score": 0.0, "dimensions": {}}

    def generate_validation_report(self, validation_results: Dict) -> str:
        """Generate human-readable validation report"""
        report = ["Protocol Validation Report\n"]
        
        # Add overall score
        overall_score = validation_results.get("overall_score", 0.0)
        report.append(f"Overall Quality Score: {overall_score:.2f}%\n")
        
        # Add dimension results
        if "dimensions" in validation_results:
            for dim_name, dim_results in validation_results["dimensions"].items():
                report.append(f"\n{dim_name.replace('_', ' ').title()} Assessment:")
                report.append(f"Score: {dim_results.get('score', 0.0):.2%}")
                
                if dim_results.get("missing_elements"):
                    report.append("\nMissing Elements:")
                    for elem in dim_results["missing_elements"]:
                        report.append(f"- {elem}")
                
                if dim_results.get("recommendations"):
                    report.append("\nRecommendations:")
                    for rec in dim_results["recommendations"]:
                        report.append(f"- {rec}")
        
        return "\n".join(report)

    def _validate_scientific_rigor(self, content: Dict[str, str]) -> float:
        """Validate scientific rigor of the protocol"""
        required_elements = [
            "objectives", "hypothesis", "endpoints", "sample_size",
            "analysis", "methods", "design"
        ]
        return self._calculate_dimension_score(content, required_elements)

    def _validate_methodology(self, content: Dict[str, str]) -> float:
        """Validate methodology of the protocol"""
        required_elements = [
            "population", "criteria", "procedures", "assessments",
            "statistical", "data_collection"
        ]
        return self._calculate_dimension_score(content, required_elements)

    def _validate_compliance(self, content: Dict[str, str]) -> float:
        """Validate regulatory compliance"""
        required_elements = [
            "ethical", "safety", "monitoring", "reporting",
            "consent", "privacy"
        ]
        return self._calculate_dimension_score(content, required_elements)

    def _calculate_dimension_score(self, content: Dict[str, str], required_elements: List[str]) -> float:
        """Calculate score for a validation dimension"""
        if not content:
            return 0.0

        found_elements = 0
        for element in required_elements:
            for section_content in content.values():
                if isinstance(section_content, str) and element.lower() in section_content.lower():
                    found_elements += 1
                    break

        return found_elements / len(required_elements)

    def _get_study_type(self, study_type: str) -> StudyType:
        """Get study type enum from string"""
        try:
            return next(st for st in StudyType 
                       if st.type_name == study_type.lower())
        except StopIteration:
            raise ValueError(f"Unknown study type: {study_type}")
