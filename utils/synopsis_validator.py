# synopsis_validator.py

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
        self.section_rules = {
            # Keep your existing rules...
        }

    def _validate_basic_structure(self, content):
        """Validate basic synopsis structure"""
        try:
            if content is None:
                logger.error("Synopsis content is None")
                return {
                    'is_valid': False,
                    'missing_sections': [],
                    'warnings': ["Empty synopsis content"]
                }

            if not isinstance(content, str):
                logger.warning(f"Converting synopsis content from {type(content)} to string")
                content = str(content)

            if not content.strip():
                logger.error("Synopsis content is empty string")
                return {
                    'is_valid': False,
                    'missing_sections': [],
                    'warnings': ["Empty synopsis content"]
                }

            # Your existing validation logic...
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

        except Exception as e:
            logger.error(f"Error in basic structure validation: {str(e)}")
            return {
                'is_valid': False,
                'missing_sections': [],
                'warnings': [f"Error validating structure: {str(e)}"]
            }

    def analyze_study_type(self, content):
        """Analyze study type from synopsis content"""
        try:
            # First ensure content is valid
            if not content or not isinstance(content, str):
                logger.error("Invalid content for study type analysis")
                return "Clinical Trial"  # Default fallback

            # Look for specific keywords indicating study type
            content_lower = content.lower()

            # Check for SLR indicators
            if ('systematic' in content_lower and 'review' in content_lower) or \
               'systematic literature review' in content_lower or \
               'slr' in content_lower:
                return "Systematic Literature Review"

            # Check for Meta-analysis indicators
            if ('meta' in content_lower and 'analysis' in content_lower) or \
               'meta-analysis' in content_lower:
                return "Meta-analysis"

            # Default to Clinical Trial if no other type is detected
            return "Clinical Trial"

        except Exception as e:
            logger.error(f"Error analyzing study type: {str(e)}")
            return "Clinical Trial"

def validate_synopsis(content):
    """Validate synopsis structure and content with enhanced feedback"""
    try:
        validator = SynopsisValidator()

        # Log the incoming content
        logger.info(f"Validating synopsis content type: {type(content)}")
        logger.info(f"Content length: {len(str(content)) if content else 0}")

        # Basic structure validation
        basic_validation = validator._validate_basic_structure(content)
        if not basic_validation['is_valid']:
            logger.warning("Basic validation failed")
            return basic_validation

        # Determine study type first
        study_type = validator.analyze_study_type(content)
        logger.info(f"Detected study type: {study_type}")

        # Use GPT for detailed analysis
        try:
            detailed_analysis, _ = validator.gpt_handler.analyze_synopsis(content)
            if not isinstance(detailed_analysis, dict):
                logger.warning("GPT analysis returned invalid format")
                detailed_analysis = {
                    'study_type_and_design': {},
                    'critical_parameters': {},
                    'required_sections': [],
                    'missing_information': []
                }
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            detailed_analysis = {
                'study_type_and_design': {},
                'critical_parameters': {},
                'required_sections': [],
                'missing_information': [str(e)]
            }

        # Template-based validation
        template_validation = validator._validate_against_template(content, study_type)

        # Generate feedback
        feedback = validator._generate_feedback(
            basic_validation,
            template_validation,
            detailed_analysis
        )

        # Return combined results
        validation_results = {
            'is_valid': basic_validation['is_valid'] and \
                       len(template_validation.get('missing_requirements', [])) == 0,
            'study_type': study_type,
            'basic_validation': basic_validation,
            'template_validation': template_validation,
            'detailed_analysis': detailed_analysis,
            'feedback': feedback
        }

        return validation_results

    except Exception as e:
        logger.error(f"Error in validate_synopsis: {str(e)}")
        return {
            'is_valid': False,
            'study_type': "Clinical Trial",
            'basic_validation': {'is_valid': False, 'warnings': [str(e)]},
            'template_validation': {},
            'detailed_analysis': {},
            'feedback': [{'type': 'error', 'message': str(e)}]
        }