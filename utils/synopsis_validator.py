import re
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager

class SynopsisValidator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
        self.template_manager = TemplateManager()
        
        # Section-specific validation rules
        self.section_rules = {
            'background': {
                'required_elements': [
                    'disease_background',
                    'current_treatments',
                    'study_rationale'
                ],
                'suggested_content': [
                    'Disease epidemiology',
                    'Current treatment options',
                    'Unmet medical needs',
                    'Study drug rationale'
                ],
                'guidelines': ['ICH E6(R2)', 'ICH E8']
            },
            'objectives': {
                'required_elements': [
                    'primary_objective',
                    'primary_endpoint',
                    'secondary_objectives'
                ],
                'suggested_content': [
                    'Clear primary objective statement',
                    'Measurable endpoints',
                    'Timeline specifications'
                ],
                'guidelines': ['ICH E9']
            },
            'study_design': {
                'required_elements': [
                    'design_type',
                    'population',
                    'treatment_groups'
                ],
                'suggested_content': [
                    'Study design diagram',
                    'Treatment allocation',
                    'Study duration'
                ],
                'guidelines': ['ICH E6(R2)']
            }
        }

    def _validate_basic_structure(self, content):
        """Validate basic synopsis structure"""
        required_sections = [
            'background',
            'objectives',
            'study design',
            'population',
            'endpoints',
            'statistical considerations'
        ]
        
        missing_sections = []
        warnings = []
        
        # Check for required sections
        for section in required_sections:
            if not re.search(rf'\b{section}\b', content.lower()):
                missing_sections.append({
                    'section': section,
                    'guidelines': self.section_rules.get(section, {}).get('guidelines', []),
                    'suggested_content': self.section_rules.get(section, {}).get('suggested_content', [])
                })
        
        return {
            'is_valid': len(missing_sections) == 0,
            'missing_sections': missing_sections,
            'warnings': warnings
        }

    def _validate_against_template(self, content, study_phase):
        """Validate synopsis against phase-specific template"""
        template = self.template_manager.get_template(study_phase)
        missing_requirements = []
        
        for section, requirements in template['sections'].items():
            # Load section template
            section_template = self.template_manager.get_section_template(study_phase, section)
            
            # Check required components
            for component in section_template['structure']:
                if component.get('required', False):
                    if not self._check_component_presence(content, component):
                        missing_requirements.append({
                            'section': section,
                            'component': component,
                            'example_content': section_template['structure'][component].get('components', []),
                            'guidelines': self.section_rules.get(section, {}).get('guidelines', [])
                        })
        
        return {
            'missing_requirements': missing_requirements,
            'study_phase': study_phase
        }

    def _check_component_presence(self, content, component):
        """Check if a component is present in the content"""
        component_name = component.lower().replace('_', ' ')
        return bool(re.search(rf'\b{component_name}\b', content.lower()))

    def _generate_feedback(self, basic_validation, template_validation, detailed_analysis):
        """Generate comprehensive feedback with guidance"""
        feedback = []
        
        # Basic structure feedback
        for missing in basic_validation['missing_sections']:
            feedback.append({
                'type': 'missing_section',
                'section': missing['section'],
                'message': f"Missing required section: {missing['section']}",
                'guidelines': missing['guidelines'],
                'suggested_content': missing['suggested_content'],
                'impact': "Required for protocol completeness and regulatory compliance"
            })
        
        # Template-specific feedback
        for missing in template_validation['missing_requirements']:
            feedback.append({
                'type': 'template_requirement',
                'section': missing['section'],
                'component': missing['component'],
                'message': f"Missing required component in {missing['section']}: {missing['component']}",
                'example_content': missing['example_content'],
                'guidelines': missing['guidelines']
            })
        
        # Detailed analysis feedback
        if detailed_analysis.get('missing_information'):
            for info in detailed_analysis['missing_information']:
                feedback.append({
                    'type': 'content_guidance',
                    'message': info,
                    'impact': "May affect protocol quality and regulatory acceptance"
                })
        
        return feedback

def validate_synopsis(content):
    """Validate synopsis structure and content with enhanced feedback"""
    validator = SynopsisValidator()
    
    try:
        # Basic structure validation
        basic_validation = validator._validate_basic_structure(content)
        
        # Use GPT for detailed analysis
        gpt_handler = GPTHandler()
        detailed_analysis, study_phase = gpt_handler.analyze_synopsis(content)
        
        # Template-based validation
        template_validation = validator._validate_against_template(content, study_phase)
        
        # Combine all validation results
        validation_results = {
            'is_valid': basic_validation['is_valid'] and len(template_validation['missing_requirements']) == 0,
            'missing_sections': basic_validation['missing_sections'],
            'warnings': basic_validation['warnings'],
            'template_validation': template_validation,
            'detailed_analysis': detailed_analysis,
            'feedback': validator._generate_feedback(
                basic_validation,
                template_validation,
                detailed_analysis
            )
        }
        
        return validation_results
        
    except Exception as e:
        raise Exception(f"Error validating synopsis: {str(e)}")
