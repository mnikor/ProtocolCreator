# unified_protocol_validator.py

from enum import Enum
from typing import Dict, List

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

class UnifiedProtocolValidator:
    def __init__(self):
        self.interventional_validator = InterventionalValidator()
        self.secondary_research_validator = SecondaryResearchValidator()

    def validate_protocol(self, content: Dict, study_type: str) -> Dict:
        """Main validation method that routes to appropriate validator"""
        try:
            # Determine study category
            study_enum = StudyType[study_type.upper()]
            
            if study_enum.category == StudyCategory.INTERVENTIONAL:
                return self.interventional_validator.validate_protocol(
                    content, 
                    study_enum.type_name
                )
            else:
                return self.secondary_research_validator.validate_protocol(
                    content, 
                    study_enum.type_name
                )

        except KeyError:
            raise ValueError(f"Unsupported study type: {study_type}")
        except Exception as e:
            raise Exception(f"Validation error: {str(e)}")

    def generate_report(self, validation_results: Dict, study_type: str) -> str:
        """Generate appropriate report based on study type"""
        study_enum = StudyType[study_type.upper()]
        
        if study_enum.category == StudyCategory.INTERVENTIONAL:
            return self.interventional_validator.generate_report(validation_results)
        else:
            return self.secondary_research_validator.generate_report(validation_results)

# Example usage:
def validate_study_protocol(protocol_content: Dict, study_type: str) -> Dict:
    """Main function to validate any type of protocol"""
    validator = UnifiedProtocolValidator()
    
    try:
        # Validate protocol
        validation_results = validator.validate_protocol(protocol_content, study_type)
        
        # Generate report
        report = validator.generate_report(validation_results, study_type)
        
        return {
            "validation_results": validation_results,
            "report": report
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "validation_results": None,
            "report": None
        }

# Usage example:
if __name__ == "__main__":
    # Example for Phase 3 study
    phase3_protocol = {...}
    phase3_results = validate_study_protocol(phase3_protocol, "PHASE3")
    
    # Example for RWE study
    rwe_protocol = {...}
    rwe_results = validate_study_protocol(rwe_protocol, "RWE")
    
    # Example for SLR study
    slr_protocol = {...}
    slr_results = validate_study_protocol(slr_protocol, "SLR")