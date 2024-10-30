import logging
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager

logger = logging.getLogger(__name__)

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
        self.template_manager = TemplateManager()

    def generate_section(self, section_name: str, study_type: str, synopsis_content: str, existing_sections: dict = None):
        """Generate a protocol section"""
        try:
            logger.info(f"Starting generation of {section_name} section")

            # Input validation
            if not section_name:
                raise ValueError("Section name is required")
            if not study_type:
                raise ValueError("Study type is required")
            if not synopsis_content:
                raise ValueError("Synopsis content is required")

            # Log the state before generation
            logger.info(f"Generating section: {section_name}")
            logger.info(f"Study type: {study_type}")
            logger.info(f"Synopsis length: {len(synopsis_content)}")
            logger.info(f"Existing sections: {list(existing_sections.keys()) if existing_sections else []}")

            # Special handling for procedures section
            if section_name == 'procedures':
                logger.info("Using special handling for procedures section")
                return self._generate_procedures_section(synopsis_content, existing_sections)

            # Get template
            template = self._get_section_template(study_type, section_name)

            # Format previous sections if they exist
            previous_sections = self._format_previous_sections(existing_sections) if existing_sections else ""

            # Generate content
            content = self.gpt_handler.generate_section(
                section_name=section_name,
                synopsis_content=synopsis_content,
                previous_sections=previous_sections
            )

            # Validate generated content
            if not content or len(content.strip()) < 10:
                raise ValueError(f"Generated content for {section_name} is too short or empty")

            logger.info(f"Successfully generated {section_name} section")
            return content

        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            raise

    def _generate_procedures_section(self, synopsis_content: str, existing_sections: dict = None):
        """Special handler for procedures section"""
        try:
            procedures_content = """
# Study Procedures

## Overview
This section details the procedures to be followed during the study, including screening, treatment, and follow-up phases.

## Screening Procedures
1. Informed consent
2. Demographics and medical history
3. Physical examination
4. Vital signs
5. ECOG performance status
6. Laboratory assessments
7. Disease assessment imaging
8. ECG
9. Inclusion/exclusion criteria review

## Treatment Phase Procedures
1. Drug administration
2. Safety monitoring
3. Efficacy assessments
4. Laboratory tests
5. Quality of life assessments
6. Adverse event monitoring
7. Concomitant medication review

## Follow-up Procedures
1. Safety follow-up
2. Disease assessment
3. Survival status
4. Subsequent therapy documentation

## Study Assessments
### Safety Assessments
- Physical examinations
- Vital signs
- Laboratory tests
- Adverse event monitoring
- ECG monitoring when clinically indicated

### Efficacy Assessments
- Radiographic assessments
- PSA measurements
- Clinical progression evaluation
- Pain assessments
- Quality of life questionnaires

### Laboratory Assessments
- Hematology
- Clinical chemistry
- PSA
- Testosterone
- Pharmacokinetic sampling

### Other Assessments
- Patient-reported outcomes
- Resource utilization
- Biomarker sampling
            """

            # Now use GPT to enhance this template with study-specific details
            enhanced_content = self.gpt_handler.generate_section(
                section_name='procedures',
                synopsis_content=synopsis_content,
                previous_sections=procedures_content
            )

            return enhanced_content if enhanced_content else procedures_content

        except Exception as e:
            logger.error(f"Error generating procedures section: {str(e)}")
            return procedures_content  # Return base template if enhancement fails

    def _get_section_template(self, study_type: str, section_name: str) -> dict:
        """Get template for a specific section"""
        try:
            return self.template_manager.get_section_template(study_type, section_name)
        except Exception as e:
            logger.error(f"Error getting template: {str(e)}")
            return {}

    def _format_previous_sections(self, existing_sections: dict) -> str:
        """Format previously generated sections for context"""
        try:
            formatted_sections = []
            for section_name, content in existing_sections.items():
                if content and isinstance(content, str):
                    formatted_sections.append(f"=== {section_name.upper()} ===\n{content}\n")
            return "\n".join(formatted_sections)
        except Exception as e:
            logger.error(f"Error formatting sections: {str(e)}")
            return ""