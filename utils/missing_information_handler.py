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
        """Analyze section completeness and missing information"""
        missing_fields = self.detect_missing_fields(section_name, content)
        recommendations = self.detect_recommendations(content)
        
        analysis = {
            'section_name': section_name,
            'missing_fields': missing_fields,
            'recommendations': recommendations,
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
