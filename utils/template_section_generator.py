from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager
import logging

logger = logging.getLogger(__name__)

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
        self.template_manager = TemplateManager()

    def generate_section(self, section_name, study_type, synopsis_content, existing_sections=None):
        '''Generate content for a specific protocol section'''
        try:
            if not section_name or not synopsis_content:
                raise ValueError("Section name and synopsis content are required")

            # Get section template
            template = self.template_manager.get_section_template(study_type, section_name)
            if not template:
                logger.warning(f"No template found for {section_name} in {study_type}")

            # Generate content using GPT
            content = self.gpt_handler.generate_section(
                section_name=section_name,
                synopsis_content=synopsis_content,
                previous_sections=existing_sections or {}
            )

            if not content:
                raise ValueError(f"No content generated for {section_name}")

            return content

        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            raise

    def generate_complete_protocol(self, study_type, synopsis_content):
        '''Generate all protocol sections'''
        sections = {}
        try:
            if not study_type or not synopsis_content:
                raise ValueError("Study type and synopsis content are required")

            section_list = [
                'background', 'objectives', 'study_design', 'population',
                'procedures', 'statistical', 'safety'
            ]

            for section_name in section_list:
                sections[section_name] = self.generate_section(
                    section_name=section_name,
                    study_type=study_type,
                    synopsis_content=synopsis_content,
                    existing_sections=sections
                )
            return sections
        except Exception as e:
            logger.error(f"Error generating complete protocol: {str(e)}")
            raise