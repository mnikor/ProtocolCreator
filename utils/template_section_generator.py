import logging
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager

logger = logging.getLogger(__name__)

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
        self.template_manager = TemplateManager()

    def generate_section(self, section_name: str, study_type: str, synopsis_content: str, existing_sections: dict = None):
        """
        Generate a protocol section using GPT and templates
        
        Args:
            section_name (str): Name of the section to generate
            study_type (str): Type of study (phase1, phase2, phase3)
            synopsis_content (str): Original synopsis content
            existing_sections (dict): Previously generated sections
            
        Returns:
            str: Generated section content
        """
        try:
            logger.info(f"Generating {section_name} section for {study_type}")
            
            # Get template for this section
            template = self.template_manager.get_section_template(study_type, section_name)
            
            # Format previous sections if they exist
            previous_sections = ""
            if existing_sections:
                previous_sections = self._format_previous_sections(existing_sections)
            
            # Generate content using GPT
            content = self.gpt_handler.generate_section(
                section_name=section_name,
                synopsis_content=synopsis_content,
                previous_sections=previous_sections
            )
            
            # Validate generated content against template
            self._validate_against_template(content, template)
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            raise Exception(f"Failed to generate {section_name} section: {str(e)}")
    
    def _format_previous_sections(self, existing_sections: dict) -> str:
        """Format previously generated sections for context"""
        formatted_sections = []
        for section_name, content in existing_sections.items():
            formatted_sections.append(f"=== {section_name.upper()} ===\n{content}\n")
        return "\n".join(formatted_sections)
    
    def _validate_against_template(self, content: str, template: dict):
        """
        Validate generated content against section template
        
        Args:
            content (str): Generated section content
            template (dict): Section template with requirements
        """
        try:
            # Check for required components
            structure = template.get('structure', {})
            for component, details in structure.items():
                if details.get('required', False):
                    # Convert component name to searchable text
                    search_text = component.lower().replace('_', ' ')
                    if search_text not in content.lower():
                        logger.warning(f"Required component '{component}' not found in generated content")
                        # We don't raise an error here, just log the warning
                        
        except Exception as e:
            logger.error(f"Error validating content against template: {str(e)}")
            # Continue despite validation errors to not block generation
    
    def generate_complete_protocol(self, study_type: str, synopsis_content: str):
        """
        Generate all protocol sections
        
        Args:
            study_type (str): Type of study (phase1, phase2, phase3)
            synopsis_content (str): Original synopsis content
            
        Returns:
            dict: Dictionary of generated sections
        """
        try:
            template = self.template_manager.get_template(study_type)
            sections = template.get('sections', {}).keys()
            
            generated_sections = {}
            for section_name in sections:
                try:
                    content = self.generate_section(
                        section_name,
                        study_type,
                        synopsis_content,
                        generated_sections
                    )
                    generated_sections[section_name] = content
                except Exception as e:
                    logger.error(f"Error generating section {section_name}: {str(e)}")
                    continue
                    
            return generated_sections
            
        except Exception as e:
            logger.error(f"Error generating complete protocol: {str(e)}")
            raise Exception(f"Failed to generate complete protocol: {str(e)}")
