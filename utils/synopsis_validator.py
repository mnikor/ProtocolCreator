import re
import logging
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        if not isinstance(content, str):
            logger.error("Synopsis content must be a string")
            return {
                'is_valid': False,
                'missing_sections': [],
                'warnings': ["Invalid synopsis content format"]
            }

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
        if not isinstance(content, str):
            logger.error("Content must be a string")
            return {
                'missing_requirements': [],
                'study_phase': study_phase
            }

        try:
            template = self.template_manager.get_template(study_phase)
            if not template or not isinstance(template, dict):
                logger.error(f"Invalid template for phase {study_phase}")
                return {
                    'missing_requirements': [],
                    'study_phase': study_phase
                }

            missing_requirements = []
            template_sections = template.get('sections', {})

            if isinstance(template_sections, dict):
                for section, requirements in template_sections.items():
                    # Load section template
                    section_template = self.template_manager.get_section_template(study_phase, section)
                    if section_template and isinstance(section_template, dict):
                        # Check required components
                        structure = section_template.get('structure', {})
                        if isinstance(structure, dict):
                            for component, details in structure.items():
                                if details.get('required', False):
                                    if not self._check_component_presence(content, component):
                                        missing_requirements.append({
                                            'section': section,
                                            'component': component,
                                            'example_content': details.get('components', []),
                                            'guidelines': self.section_rules.get(section, {}).get('guidelines', [])
                                        })

            return {
                'missing_requirements': missing_requirements,
                'study_phase': study_phase
            }

        except Exception as e:
            logger.error(f"Error in template validation: {str(e)}")
            return {
                'missing_requirements': [],
                'study_phase': study_phase
            }

    def _check_component_presence(self, content, component):
        """Check if a component is present in the content"""
        if not isinstance(content, str) or not isinstance(component, str):
            return False
        component_name = component.lower().replace('_', ' ')
        return bool(re.search(rf'\b{component_name}\b', content.lower()))

    def _generate_feedback(self, basic_validation, template_validation, detailed_analysis):
        """Generate comprehensive feedback with guidance"""
        feedback = []

        # Basic structure feedback
        if isinstance(basic_validation, dict):
            for missing in basic_validation.get('missing_sections', []):
                if isinstance(missing, dict):
                    feedback.append({
                        'type': 'missing_section',
                        'section': missing.get('section', ''),
                        'message': f"Missing required section: {missing.get('section', '')}",
                        'guidelines': missing.get('guidelines', []),
                        'suggested_content': missing.get('suggested_content', []),
                        'impact': "Required for protocol completeness and regulatory compliance"
                    })

        # Template-specific feedback
        if isinstance(template_validation, dict):
            for missing in template_validation.get('missing_requirements', []):
                if isinstance(missing, dict):
                    feedback.append({
                        'type': 'template_requirement',
                        'section': missing.get('section', ''),
                        'component': missing.get('component', ''),
                        'message': f"Missing required component in {missing.get('section', '')}: {missing.get('component', '')}",
                        'example_content': missing.get('example_content', []),
                        'guidelines': missing.get('guidelines', [])
                    })

        # Detailed analysis feedback
        if isinstance(detailed_analysis, dict):
            missing_info = detailed_analysis.get('missing_information', [])
            if isinstance(missing_info, list):
                for info in missing_info:
                    feedback.append({
                        'type': 'content_guidance',
                        'message': str(info),
                        'impact': "May affect protocol quality and regulatory acceptance"
                    })

        return feedback

def validate_synopsis(content):
    """Validate synopsis structure and content with enhanced feedback"""
    try:
        validator = SynopsisValidator()

        # Basic structure validation
        basic_validation = validator._validate_basic_structure(content)

        # Use GPT for detailed analysis
        detailed_analysis, study_phase = validator.gpt_handler.analyze_synopsis(content)

        if not isinstance(detailed_analysis, dict):
            logger.error("Invalid detailed analysis format")
            detailed_analysis = {
                'study_type_and_design': {},
                'critical_parameters': {},
                'required_sections': [],
                'missing_information': []
            }

        # Template-based validation
        template_validation = validator._validate_against_template(content, study_phase)

        # Generate feedback
        feedback = validator._generate_feedback(
            basic_validation,
            template_validation,
            detailed_analysis
        )

        # Combine all validation results
        validation_results = {
            'is_valid': basic_validation.get('is_valid', False) and 
                       len(template_validation.get('missing_requirements', [])) == 0,
            'missing_sections': basic_validation.get('missing_sections', []),
            'warnings': basic_validation.get('warnings', []),
            'template_validation': template_validation,
            'detailed_analysis': detailed_analysis,
            'feedback': feedback
        }

        return validation_results

    except Exception as e:
        logger.error(f"Error in validate_synopsis: {str(e)}")
        raise Exception(f"Error validating synopsis: {str(e)}")