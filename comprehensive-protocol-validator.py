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
            # Scientific validation rules
            "scientific": {
                "methodology_requirements": self._get_methodology_rules(),
                "statistical_requirements": self._get_statistical_rules(),
                "bias_controls": self._get_bias_rules()
            },
            # Compliance validation rules
            "compliance": {
                "regulatory_requirements": self._get_regulatory_rules(),
                "ethical_requirements": self._get_ethical_rules(),
                "reporting_standards": self._get_reporting_rules()
            }
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
        # Check required elements
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

        # Check consistency
        self._check_consistency(content, results)
        
        # Check completeness
        self._check_completeness(content, study_type, results)

    def _validate_scientific_rigor(self, content: Dict, study_type: str, results: Dict):
        """Validate scientific methodology and rigor"""
        # Check methodology
        methodology_rules = self.validation_rules["scientific"]["methodology_requirements"]
        self._check_methodology(content, methodology_rules, results)
        
        # Check statistical approach
        statistical_rules = self.validation_rules["scientific"]["statistical_requirements"]
        self._check_statistics(content, statistical_rules, results)
        
        # Check bias control
        bias_rules = self.validation_rules["scientific"]["bias_controls"]
        self._check_bias_controls(content, bias_rules, results)

    def _validate_language(self, content: Dict, results: Dict):
        """Validate language appropriateness and clarity"""
        language_rules = self.validation_rules["language"]
        
        for section_name, section_content in content.items():
            # Check for inappropriate terms
            for term in language_rules["inappropriate_terms"]:
                if term in section_content.lower():
                    results["issues"].append({
                        "type": IssueType.TONE,
                        "severity": IssueSeverity.MINOR,
                        "message": f"Inappropriate term '{term}' in {section_name}",
                        "location": section_name,
                        "suggestion": f"Replace '{term}' with more formal language"
                    })
            
            # Check for informal terms
            for informal, formal in language_rules["informal_terms"].items():
                if informal in section_content.lower():
                    results["issues"].append({
                        "type": IssueType.FORMALITY,
                        "severity": IssueSeverity.MINOR,
                        "message": f"Informal term '{informal}' in {section_name}",
                        "location": section_name,
                        "suggestion": f"Replace with '{formal}'"
                    })

    def _validate_compliance(self, content: Dict, study_type: str, results: Dict):
        """Validate regulatory and ethical compliance"""
        compliance_rules = self.validation_rules["compliance"]
        
        # Check regulatory requirements
        self._check_regulatory_compliance(content, study_type, results)
        
        # Check ethical requirements
        self._check_ethical_compliance(content, results)
        
        # Check reporting standards
        self._check_reporting_standards(content, study_type, results)

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