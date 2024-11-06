import logging
from typing import Dict, List, Optional
import re

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
                if field == 'design_type':
                    suggestions.append("Specify the type of study design (e.g., randomized, double-blind, parallel group)")
                elif field == 'sample_size':
                    suggestions.append("Include the planned number of participants and justification")
                elif field == 'duration':
                    suggestions.append("Define the expected study duration including treatment and follow-up periods")
                elif field == 'inclusion_criteria':
                    suggestions.append("List specific inclusion criteria with clear eligibility parameters")
                elif field == 'exclusion_criteria':
                    suggestions.append("Define clear exclusion criteria to protect subject safety")
                elif field == 'primary_endpoints':
                    suggestions.append("Specify primary outcome measures with timing of assessments")
                elif field == 'statistical_methods':
                    suggestions.append("Detail the statistical approaches for primary and secondary analyses")
                elif field == 'safety_parameters':
                    suggestions.append("Define safety monitoring parameters and frequency of assessments")
                elif field == 'study_visits':
                    suggestions.append("Provide a detailed schedule of study visits and procedures")
                elif field == 'questionnaire_type':
                    suggestions.append("Specify the type and format of questionnaires to be used")
                elif field == 'databases':
                    suggestions.append("List all databases to be searched with justification")
                else:
                    suggestions.append(f"Add details about {field.replace('_', ' ')}")

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
