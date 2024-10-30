import logging
import streamlit as st
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemplateSectionGenerator:
    def __init__(self):
        try:
            self.gpt_handler = GPTHandler()
            self.template_manager = TemplateManager()
        except Exception as e:
            logger.error(f"Error initializing TemplateSectionGenerator: {str(e)}")
            st.error(f"Error initializing generator: {str(e)}")
            raise

    def generate_section(self, section_name: str, study_type: str, synopsis_content: str, existing_sections: dict = None):
        """Generate a protocol section"""
        try:
            logger.info(f"Starting generation of {section_name} section")

            # Validate inputs
            if not section_name:
                raise ValueError("Section name is required")
            if not study_type:
                raise ValueError("Study type is required")
            if not synopsis_content:
                raise ValueError("Synopsis content is required")

            logger.info(f"Getting template for {section_name}")
            # Get template for this section
            try:
                template = self.template_manager.get_section_template(study_type, section_name)
            except Exception as e:
                logger.error(f"Error getting template: {str(e)}")
                raise ValueError(f"Failed to get template for {section_name}: {str(e)}")

            # Format previous sections if they exist
            previous_sections = ""
            if existing_sections:
                try:
                    previous_sections = self._format_previous_sections(existing_sections)
                except Exception as e:
                    logger.warning(f"Error formatting previous sections: {str(e)}")
                    # Continue without previous sections if there's an error

            logger.info("Generating content with GPT")
            # Generate content using GPT
            try:
                content = self.gpt_handler.generate_section(
                    section_name=section_name,
                    synopsis_content=synopsis_content,
                    previous_sections=previous_sections
                )
            except Exception as e:
                logger.error(f"Error in GPT generation: {str(e)}")
                raise ValueError(f"Failed to generate content: {str(e)}")

            # Validate generated content
            if not content:
                raise ValueError("No content was generated")

            logger.info("Generation completed successfully")
            return content

        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            raise

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
            return ""  # Return empty string on error