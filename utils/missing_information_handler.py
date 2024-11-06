import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MissingInformationHandler:
    def __init__(self):
        """Initialize handler with enhanced detection patterns"""
        self.required_fields = {
            'statistical_analysis': [
                'analysis_populations',
                'statistical_methods',
                'missing_data_handling',
                'interim_analyses',
                'statistical_software',
                'multiplicity_adjustment'
            ],
            'study_design': [
                'study_phase',
                'treatment_arms',
                'allocation_ratio',
                'stratification_factors',
                'visit_schedule',
                'operational_flow',
                'timeline'
            ],
            'safety': [
                'ae_definitions',
                'ae_grading',
                'safety_review',
                'dsmb_requirements',
                'laboratory_monitoring',
                'stopping_rules',
                'risk_management'
            ],
            'population': [
                'demographics',
                'clinical_characteristics',
                'laboratory_requirements',
                'screening_procedures',
                'rescreening_policy',
                'informed_consent'
            ]
        }
        
        self.placeholder_pattern = r'\[PLACEHOLDER:\s*\*(.*?)\*\]'
        self.recommendation_pattern = r'\[RECOMMENDED:\s*\*(.*?)\*\]'
        
    def _get_field_prompt(self, field: str, section_name: str = None) -> Dict:
        '''Get detailed prompt for missing field with section context and severity'''
        detailed_prompts = {
            'analysis_populations': '''
Define analysis populations including:
• Intent-to-Treat (ITT) population definition
• Per-Protocol (PP) population criteria
• Safety population specifications
• Protocol deviation handling''',
            
            'statistical_methods': '''
Specify statistical methods including:
• Primary analysis approach and models
• Significance levels and power
• Covariates and stratification
• Secondary analysis methods''',
            
            'missing_data_handling': '''
Detail missing data approach:
• Primary imputation methods
• Sensitivity analyses
• Dropout handling
• Partially missing data''',
            
            'interim_analyses': '''
Define interim analyses:
• Analysis timing
• Stopping rules
• Alpha spending
• DSMB review process''',
            
            'study_phase': '''
Specify study phase details:
• Phase designation
• Design rationale
• Treatment duration
• Follow-up period''',
            
            'treatment_arms': '''
Define treatment arms:
• Number of arms
• Interventions per arm
• Control group details
• Treatment assignment''',
            
            'visit_schedule': '''
Detail visit schedule:
• Screening timeline
• Treatment visits
• Follow-up schedule
• Visit windows''',
            
            'ae_definitions': '''
Specify adverse event definitions:
• AE categorization
• Severity grading
• Causality assessment
• Reporting requirements''',
            
            'laboratory_monitoring': '''
Define laboratory monitoring:
• Required tests
• Testing schedule
• Alert values
• Result handling''',
            
            'demographics': '''
Specify demographic requirements:
• Age ranges
• Gender considerations
• Ethnic factors
• Geographic restrictions''',
            
            'laboratory_requirements': '''
Define laboratory requirements:
• Required values
• Testing windows
• Retesting procedures
• Eligibility ranges''',
            
            'screening_procedures': '''
Detail screening procedures:
• Required assessments
• Documentation needs
• Timeline requirements
• Process flow'''
        }
        
        message = detailed_prompts.get(
            field,
            f"Please provide detailed information about {field.replace('_', ' ')}"
        )
        
        # Add section context if provided
        if section_name:
            message = f"For the {section_name.replace('_', ' ')} section:\n{message}"
        
        return {
            'message': message,
            'severity': self._get_field_severity(field, section_name)
        }

    def _get_field_severity(self, field: str, section_name: str = None) -> str:
        """Determine severity level for missing field"""
        critical_fields = {
            'analysis_populations', 'statistical_methods', 'study_phase',
            'treatment_arms', 'ae_definitions', 'dsmb_requirements',
            'demographics', 'laboratory_requirements', 'screening_procedures'
        }
        major_fields = {
            'missing_data_handling', 'interim_analyses', 'visit_schedule',
            'operational_flow', 'laboratory_monitoring', 'stopping_rules',
            'rescreening_policy', 'informed_consent'
        }
        
        if field in critical_fields:
            return 'critical'
        elif field in major_fields:
            return 'major'
        return 'minor'

    def detect_missing_fields(self, section_name: str, content: str) -> List[str]:
        """Detect missing required fields in a section"""
        missing_fields = []
        
        if section_name in self.required_fields:
            required = self.required_fields[section_name]
            content_lower = content.lower()
            
            for field in required:
                field_pattern = field.replace('_', ' ')
                if field_pattern not in content_lower:
                    missing_fields.append(field)
                    
        # Extract placeholders
        placeholders = re.findall(self.placeholder_pattern, content)
        if placeholders:
            missing_fields.extend(placeholders)
            
        return missing_fields
        
    def detect_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from content"""
        return re.findall(self.recommendation_pattern, content)
        
    def analyze_section_completeness(self, section_name: str, content: str) -> Dict:
        """Analyze section completeness and provide detailed feedback"""
        missing_fields = self.detect_missing_fields(section_name, content)
        recommendations = self.detect_recommendations(content)
        
        # Add specific improvement suggestions with severity
        suggestions = []
        if missing_fields:
            for field in missing_fields:
                field_info = self._get_field_prompt(field, section_name)
                suggestions.append({
                    'message': field_info['message'],
                    'severity': field_info['severity']
                })
        
        analysis = {
            'section_name': section_name,
            'missing_fields': missing_fields,
            'recommendations': recommendations,
            'improvement_suggestions': suggestions,
            'completeness_score': self._calculate_completeness(section_name, missing_fields)
        }
        
        return analysis
        
    def _calculate_completeness(self, section_name: str, missing_fields: List[str]) -> float:
        """Calculate section completeness score"""
        if section_name not in self.required_fields:
            return 1.0
            
        total_fields = len(self.required_fields[section_name])
        missing_count = len([f for f in missing_fields if f in self.required_fields[section_name]])
        
        if total_fields == 0:
            return 1.0
            
        return (total_fields - missing_count) / total_fields

    def validate_section_structure(self, section_name: str, content: str) -> Dict:
        """Validate section structure and organization"""
        structure_issues = []
        
        # Check section length
        min_length = 200  # Minimum characters for meaningful content
        if len(content) < min_length:
            structure_issues.append({
                "type": "structure",
                "severity": "minor",
                "message": f"Section content may be too brief ({len(content)} characters)",
                "suggestion": "Consider expanding the section with more details"
            })
            
        # Check paragraph structure
        paragraphs = content.split('\n\n')
        if len(paragraphs) < 2:
            structure_issues.append({
                "type": "structure",
                "severity": "minor",
                "message": "Limited paragraph structure",
                "suggestion": "Consider breaking content into multiple paragraphs for better readability"
            })
            
        return {
            "section_name": section_name,
            "issues": structure_issues,
            "score": 100 - (len(structure_issues) * 10)
        }
