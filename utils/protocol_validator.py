from enum import Enum
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class StudyCategory(Enum):
    INTERVENTIONAL = "interventional"
    SECONDARY_RESEARCH = "secondary_research"

class StudyType(Enum):
    # Interventional Studies
    PHASE1 = ("phase1", StudyCategory.INTERVENTIONAL)
    PHASE2 = ("phase2", StudyCategory.INTERVENTIONAL)
    PHASE3 = ("phase3", StudyCategory.INTERVENTIONAL)
    PHASE4 = ("phase4", StudyCategory.INTERVENTIONAL)
    
    # Secondary Research
    RWE = ("rwe", StudyCategory.SECONDARY_RESEARCH)
    SLR = ("slr", StudyCategory.SECONDARY_RESEARCH)
    META = ("meta", StudyCategory.SECONDARY_RESEARCH)

    def __init__(self, type_name: str, category: StudyCategory):
        self.type_name = type_name
        self.category = category

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
                "study_type_specific": {
                    StudyType.PHASE2.type_name: ["dose_rationale", "ph1_data_reference"],
                    StudyType.SLR.type_name: ["search_strategy_comprehensiveness", "quality_assessment_method"],
                    StudyType.RWE.type_name: ["data_source_validity", "confounding_control"]
                },
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
                "study_type_specific": {
                    StudyType.PHASE2.type_name: ["dose_modifications", "safety_monitoring"],
                    StudyType.SLR.type_name: ["data_extraction_process", "synthesis_method"],
                    StudyType.RWE.type_name: ["variable_definitions", "data_validation"]
                },
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
                "study_type_specific": {
                    StudyType.PHASE2.type_name: ["ind_requirements", "dmc_charter"],
                    StudyType.SLR.type_name: ["prospero_registration", "prisma_adherence"],
                    StudyType.RWE.type_name: ["data_privacy", "database_qualification"]
                },
                "weight": 0.15
            }
        }

    def validate_protocol(self, content: Dict[str, str], study_type: str) -> Dict:
        """Validate protocol across all dimensions with study type specific checks"""
        try:
            # Normalize study type
            study_type = study_type.lower()
            
            # Get study type enum
            try:
                study_enum = next(st for st in StudyType if st.type_name == study_type)
            except StopIteration:
                logger.warning(f"Unknown study type: {study_type}, using generic validation")
                study_enum = None

            validation_results = {
                "issues": [],
                "suggestions": [],
                "quality_score": 0.0
            }
            
            total_weighted_score = 0.0
            total_weight = 0.0
            
            for dimension in ValidationDimension:
                dimension_results = self._validate_dimension(
                    content, 
                    study_enum,
                    dimension
                )
                validation_results[dimension.value] = dimension_results
                
                weight = self.validation_criteria[dimension].get("weight", 0.0)
                total_weighted_score += dimension_results["score"] * weight
                total_weight += weight
                
            if total_weight > 0:
                validation_results["quality_score"] = (total_weighted_score / total_weight) * 100
                
            return validation_results

        except Exception as e:
            logger.error(f"Error in protocol validation: {str(e)}")
            raise

    def _validate_dimension(self, content: Dict[str, str], study_type: StudyType, 
                          dimension: ValidationDimension) -> Dict:
        """Validate specific dimension with study type specific rules"""
        try:
            criteria = self.validation_criteria.get(dimension, {})
            results = {
                "missing_items": [],
                "recommendations": [],
                "score": 0.0,
                "item_scores": {}
            }

            # Check common items
            items = criteria.get("items", [])
            total_score = 0.0
            
            for item in items:
                item_score = self._check_item_presence(content, item)
                results["item_scores"][item] = item_score
                total_score += item_score
                
                if item_score < 0.6:
                    results["missing_items"].append(item)
                    results["recommendations"].append(
                        f"Improve {item.replace('_', ' ')} coverage and clarity"
                    )

            # Check study type specific items
            if study_type:
                specific_items = criteria.get("study_type_specific", {}).get(study_type.type_name, [])
                for item in specific_items:
                    item_score = self._check_item_presence(content, item)
                    results["item_scores"][item] = item_score
                    total_score += item_score
                    
                    if item_score < 0.6:
                        results["missing_items"].append(f"{study_type.type_name}-specific: {item}")
                        results["recommendations"].append(
                            f"Add {study_type.type_name}-specific element: {item}"
                        )

            # Calculate dimension score
            total_items = len(items) + (len(specific_items) if study_type else 0)
            if total_items > 0:
                results["score"] = total_score / total_items
            
            # Add dimension-specific recommendations
            self._add_dimension_recommendations(results, dimension, study_type)
            
            return results

        except Exception as e:
            logger.error(f"Error validating dimension {dimension}: {str(e)}")
            return {
                "missing_items": [],
                "recommendations": [f"Error in validation: {str(e)}"],
                "score": 0.0,
                "item_scores": {}
            }

    def _check_item_presence(self, content: Dict[str, str], item: str) -> float:
        """Check if an item is adequately addressed in protocol content"""
        if not content or not isinstance(content, dict):
            return 0.0
            
        search_terms = item.replace('_', ' ').lower().split()
        max_section_score = 0.0
        
        for section_content in content.values():
            if not isinstance(section_content, str):
                continue
                
            content_lower = section_content.lower()
            section_score = 0.0
            
            if all(term in content_lower for term in search_terms):
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
                
                section_score += min(0.4, sum(0.1 for pattern in context_patterns 
                                            if pattern in content_lower))
                                            
            max_section_score = max(max_section_score, section_score)
                
        return max_section_score

    def _add_dimension_recommendations(self, results: Dict, dimension: ValidationDimension, 
                                    study_type: StudyType = None):
        """Add dimension and study type specific recommendations"""
        score = results["score"]
        
        if score < 0.6:
            base_rec = {
                ValidationDimension.SCIENTIFIC_RIGOR: "Strengthen scientific rationale and methodology",
                ValidationDimension.METHODOLOGY: "Provide more detailed methods and procedures",
                ValidationDimension.REGULATORY_COMPLIANCE: "Ensure compliance with all regulatory requirements"
            }.get(dimension)
            
            if base_rec:
                results["recommendations"].append(base_rec)
                
            # Add study type specific recommendations
            if study_type:
                type_specific_rec = {
                    (StudyType.PHASE2, ValidationDimension.SCIENTIFIC_RIGOR): 
                        "Include more Phase 1 data references and dose rationale",
                    (StudyType.SLR, ValidationDimension.METHODOLOGY):
                        "Strengthen search strategy and data extraction methods",
                    (StudyType.RWE, ValidationDimension.REGULATORY_COMPLIANCE):
                        "Address data privacy and database qualification requirements"
                }.get((study_type, dimension))
                
                if type_specific_rec:
                    results["recommendations"].append(type_specific_rec)

    def generate_validation_report(self, validation_results: Dict) -> str:
        """Generate detailed validation report with study type specific insights"""
        report = ["Protocol Validation Report\n"]
        
        # Overall score
        report.append(f"Overall Quality Score: {validation_results.get('quality_score', 0):.2f}%\n")
        
        # Dimension-specific results
        for dimension, results in validation_results.items():
            if isinstance(results, dict) and "score" in results:
                report.append(f"\n{dimension.replace('_', ' ').title()} "
                            f"(Score: {results['score']*100:.2f}%)")
                
                if results.get("missing_items"):
                    report.append("\nMissing Items:")
                    for item in results["missing_items"]:
                        report.append(f"- {item}")
                        
                if results.get("recommendations"):
                    report.append("\nRecommendations:")
                    for rec in results["recommendations"]:
                        report.append(f"- {rec}")
                        
        return "\n".join(report)
