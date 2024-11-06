import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MissingInformationHandler:
    def __init__(self):
        """Initialize handler with detection patterns"""
        self.required_fields = {
            'background': ['rationale', 'current_treatment', 'unmet_need'],
            'objectives': ['primary_objective', 'secondary_objectives'],
            'study_design': ['design_type', 'sample_size', 'duration'],
            'population': ['inclusion_criteria', 'exclusion_criteria', 'sample_size'],
            'procedures': ['study_visits', 'assessments', 'follow_up'],
            'statistical_analysis': ['analysis_population', 'statistical_methods', 'sample_size_calculation'],
            'safety': ['safety_parameters', 'adverse_events', 'monitoring'],
            'endpoints': ['primary_endpoints', 'secondary_endpoints', 'safety_endpoints'],
            'survey_design': ['survey_type', 'administration_method', 'target_population'],
            'survey_instrument': ['questionnaire_type', 'validation_status', 'scoring_method'],
            'search_strategy': ['databases', 'search_terms', 'time_period'],
            'data_source': ['database_name', 'time_period', 'data_elements']
        }
        
        self.placeholder_pattern = r'\[PLACEHOLDER:\s*\*(.*?)\*\]'
        self.recommendation_pattern = r'\[RECOMMENDED:\s*\*(.*?)\*\]'
        
    def _get_field_prompt(self, field: str, section_name: str = None) -> str:
        '''Get detailed prompt for missing field with section context'''
        detailed_prompts = {
            'sample_size': (
                "Please specify the target sample size with these details:\n"
                "• Total number of participants to be enrolled\n"
                "• Statistical justification for the sample size\n"
                "• Power calculations and assumptions\n"
                "• Accounting for potential dropouts"
            ),
            'design_type': (
                "Please specify the study design including:\n"
                "• Type (e.g., randomized, open-label, single/double-blind)\n"
                "• Control group details if applicable\n"
                "• Treatment allocation ratio\n"
                "• Duration of treatment and follow-up"
            ),
            'duration': (
                "Define the study duration including:\n"
                "• Screening period length\n"
                "• Treatment period duration\n"
                "• Follow-up period details\n"
                "• Total study duration estimate"
            ),
            'inclusion_criteria': (
                "Specify inclusion criteria including:\n"
                "• Age range and gender\n"
                "• Disease/condition specific requirements\n"
                "• Required medical history\n"
                "• Laboratory/diagnostic requirements"
            ),
            'exclusion_criteria': (
                "Define exclusion criteria including:\n"
                "• Medical conditions that preclude participation\n"
                "• Prior/concomitant treatments\n"
                "• Safety-related exclusions\n"
                "• Practical/logistical exclusions"
            ),
            'primary_endpoints': (
                "Define primary endpoints including:\n"
                "• Main outcome measure(s)\n"
                "• Timing of assessments\n"
                "• Method of measurement\n"
                "• Clinical relevance"
            ),
            'statistical_methods': (
                "Specify statistical methods including:\n"
                "• Analysis populations\n"
                "• Primary analysis approach\n"
                "• Handling of missing data\n"
                "• Interim analyses if planned"
            )
        }
        
        # Add section context to prompt
        if section_name:
            base_prompt = detailed_prompts.get(
                field,
                f"Please provide detailed information about {field.replace('_', ' ')}"
            )
            return f"For the {section_name.replace('_', ' ')} section:\n{base_prompt}"
        
        return detailed_prompts.get(
            field,
            f"Please provide detailed information about {field.replace('_', ' ')}"
        )

    def detect_missing_fields(self, section_name: str, content: str) -> List[str]:
        """Detect missing required fields in a section"""
        missing_fields = []
        
        # Check required fields based on section type
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
        
        # Add specific improvement suggestions
        suggestions = []
        if missing_fields:
            for field in missing_fields:
                suggestions.append(self._get_field_prompt(field, section_name))
        
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
