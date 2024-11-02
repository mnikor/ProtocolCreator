import logging
from typing import Dict, Optional
from .missing_information_handler import MissingInformationHandler
from .gpt_handler import GPTHandler

logger = logging.getLogger(__name__)

class ProtocolImprover:
    def __init__(self):
        """Initialize improver with handlers"""
        self.missing_info_handler = MissingInformationHandler()
        self.gpt_handler = GPTHandler()
        
    def analyze_synopsis(self, content: str, study_type: str = None) -> Dict:
        '''Analyze synopsis content with study type specific validation'''
        content_lower = content.lower()
        
        # Get study-specific required fields
        required_fields = self._get_study_type_requirements(study_type)
        
        missing_fields = {}
        for field, patterns in required_fields.items():
            found = any(pattern in content_lower for pattern in patterns)
            if not found:
                missing_fields[field] = self._get_field_prompt(field, study_type)
        
        return {
            'critical_missing': bool(missing_fields),
            'critical_fields': missing_fields,
            'study_type_specific': True if study_type else False
        }

    def _get_study_type_requirements(self, study_type: str) -> Dict:
        '''Get required fields based on study type'''
        base_fields = {
            'study_population': [
                'inclusion criteria', 'patient population', 'subjects',
                'eligible patients', 'study population'
            ],
            'primary_objective': [
                'primary objective', 'primary endpoint',
                'primary goal', 'main objective'
            ]
        }
        
        # Add study-type specific fields
        if study_type == 'systematic_review':
            base_fields.update({
                'search_strategy': [
                    'search strategy', 'database search',
                    'literature search', 'systematic search'
                ],
                'eligibility_criteria': [
                    'inclusion criteria', 'exclusion criteria',
                    'study selection', 'eligibility'
                ]
            })
        elif study_type == 'secondary_rwe':
            base_fields.update({
                'data_source': [
                    'database', 'data source', 'real world data',
                    'electronic health records', 'claims data'
                ],
                'time_period': [
                    'study period', 'time frame', 'data period',
                    'observation period'
                ]
            })
        elif study_type == 'patient_survey':
            base_fields.update({
                'survey_instrument': [
                    'questionnaire', 'survey tool', 'assessment tool',
                    'patient reported outcome'
                ],
                'administration': [
                    'survey administration', 'data collection',
                    'survey method', 'questionnaire delivery'
                ]
            })
        
        return base_fields

    def _get_field_prompt(self, field: str, study_type: str) -> str:
        '''Get context-aware prompt for missing field'''
        base_prompts = {
            'study_population': 'Please specify the target study population',
            'primary_objective': 'What is the primary objective of the study?'
        }
        
        study_specific_prompts = {
            'systematic_review': {
                'search_strategy': 'What databases will be searched? Include search strategy details',
                'eligibility_criteria': 'Define inclusion/exclusion criteria for study selection'
            },
            'secondary_rwe': {
                'data_source': 'Which database(s) or data source(s) will be used?',
                'time_period': 'What is the study time period for data collection?'
            },
            'patient_survey': {
                'survey_instrument': 'What survey instrument or questionnaire will be used?',
                'administration': 'How will the survey be administered to participants?'
            }
        }
        
        if study_type and study_type in study_specific_prompts:
            base_prompts.update(study_specific_prompts[study_type])
        
        return base_prompts.get(field, f'Please provide information about {field.replace("_", " ")}')
        
    def analyze_protocol_sections(self, sections: Dict[str, str]) -> Dict:
        """Analyze all protocol sections for missing information"""
        analysis_results = {}
        overall_completeness = 0.0
        total_sections = len(sections)
        
        for section_name, content in sections.items():
            section_analysis = self.missing_info_handler.analyze_section_completeness(
                section_name, content
            )
            analysis_results[section_name] = section_analysis
            overall_completeness += section_analysis['completeness_score']
            
        if total_sections > 0:
            overall_completeness /= total_sections
            
        return {
            'section_analyses': analysis_results,
            'overall_completeness': overall_completeness,
            'overall_quality_score': self._calculate_quality_score(analysis_results)
        }
        
    def _calculate_quality_score(self, analyses: Dict) -> float:
        """Calculate overall quality score based on completeness and recommendations"""
        total_score = 0.0
        total_weight = 0
        
        weights = {
            'background': 1.0,
            'objectives': 1.2,
            'study_design': 1.5,
            'population': 1.2,
            'procedures': 1.0,
            'statistical_analysis': 1.3,
            'safety': 1.4,
            'endpoints': 1.3
        }
        
        for section_name, analysis in analyses.items():
            weight = weights.get(section_name, 1.0)
            score = analysis['completeness_score']
            
            # Reduce score for sections with many missing fields
            if len(analysis['missing_fields']) > 3:
                score *= 0.8
                
            # Adjust score based on recommendations
            if analysis['recommendations']:
                score *= 0.9
                
            total_score += score * weight
            total_weight += weight
            
        if total_weight == 0:
            return 0.0
            
        return round((total_score / total_weight) * 10, 1)  # Score out of 10
        
    def get_improvement_suggestions(self, section_name: str, analysis: Dict) -> str:
        """Generate improvement suggestions for a section"""
        if not analysis['missing_fields'] and not analysis['recommendations']:
            return "No immediate improvements needed."
            
        suggestions = []
        
        if analysis['missing_fields']:
            suggestions.append("Missing information:")
            for field in analysis['missing_fields']:
                suggestions.append(f"- Add details about: {field.replace('_', ' ')}")
                
        if analysis['recommendations']:
            suggestions.append("\nRecommendations:")
            for rec in analysis['recommendations']:
                suggestions.append(f"- {rec}")
                
        return "\n".join(suggestions)
        
    def generate_field_prompt(self, field_name: str, section_name: str) -> str:
        """Generate a user-friendly prompt for missing field input"""
        field_prompts = {
            'sample_size': "What is the target sample size for this study?",
            'primary_objective': "What is the primary objective of this study?",
            'duration': "What is the planned duration of the study?",
            'inclusion_criteria': "Please specify the key inclusion criteria:",
            'exclusion_criteria': "Please specify the key exclusion criteria:",
            'primary_endpoints': "What are the primary endpoints of the study?",
            'safety_parameters': "What safety parameters will be monitored?"
        }
        
        return field_prompts.get(
            field_name,
            f"Please provide information about {field_name.replace('_', ' ')}:"
        )
