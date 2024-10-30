from typing import Dict, Optional
import logging
from utils.template_manager import TemplateManager
from utils.gpt_handler import GPTHandler

logger = logging.getLogger(__name__)

class TemplateSectionGenerator:
    def __init__(self):
        self.template_manager = TemplateManager()
        self.gpt_handler = GPTHandler()

    def generate_section(self, section_name: str, study_phase: str, synopsis_content: str, previous_sections: Optional[Dict] = None) -> str:
        """
        Generate a protocol section using phase-specific templates and GPT
        """
        try:
            # Get template for the section
            template = self.template_manager.get_section_template(study_phase, section_name)
            
            if not template:
                logger.warning(f"Template not found for {section_name} in {study_phase}")
                return self.gpt_handler.generate_section(section_name, synopsis_content, previous_sections)

            # Build enhanced prompt using template
            prompt = self._build_template_prompt(template, section_name, synopsis_content, previous_sections)
            
            # Generate content using GPT
            section_content = self.gpt_handler.generate_section(section_name, prompt, previous_sections)
            
            # Validate generated content against template requirements
            if not self._validate_generated_content(section_content, template):
                logger.warning(f"Generated content for {section_name} does not meet all template requirements")
            
            return section_content

        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            raise

    def _build_template_prompt(self, template: Dict, section_name: str, synopsis_content: str, previous_sections: Optional[Dict] = None) -> str:
        """
        Build enhanced prompt using template structure and requirements
        """
        prompt_parts = [
            f"Generate the {section_name} section for a clinical protocol based on the following synopsis:",
            synopsis_content,
            "\nRequired Structure:"
        ]

        if 'structure' in template:
            for component, details in template['structure'].items():
                prompt_parts.append(f"\n{component.replace('_', ' ').title()}:")
                if 'components' in details:
                    for item in details['components']:
                        prompt_parts.append(f"- {item}")

        if 'prompt_additions' in template:
            prompt_parts.append("\nAdditional Requirements:")
            for addition in template['prompt_additions']:
                prompt_parts.append(f"- {addition}")

        return "\n".join(prompt_parts)

    def _validate_generated_content(self, content: str, template: Dict) -> bool:
        """
        Validate that generated content includes required elements from template
        """
        if not content or not template:
            return False

        required_elements = []
        for section, details in template.get('structure', {}).items():
            if details.get('required', False):
                required_elements.extend(details.get('components', []))

        # Check if all required elements are present in the content
        missing_elements = []
        for element in required_elements:
            if element.lower() not in content.lower():
                missing_elements.append(element)

        if missing_elements:
            logger.warning(f"Missing required elements: {', '.join(missing_elements)}")
            return False

        return True
