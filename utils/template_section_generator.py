# template_section_generator.py

from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager
import logging

logger = logging.getLogger(__name__)

# Define study type-specific sections
STUDY_TYPE_CONFIG = {
    "Clinical Trial": {
        "required_sections": [
            "background",
            "objectives", 
            "study_design",
            "population",
            "procedures",
            "statistical",
            "safety"
        ]
    },
    "Systematic Literature Review": {
        "required_sections": [
            "background",
            "objectives",
            "study_design",
            "statistical"
        ]
    },
    "Meta-analysis": {
        "required_sections": [
            "background",
            "objectives",
            "study_design",
            "statistical"
        ]
    }
}

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
        self.template_manager = TemplateManager()

    def _get_required_sections(self, study_type):
        """Get required sections for the given study type"""
        study_type = study_type.strip() if study_type else "Clinical Trial"
        if study_type not in STUDY_TYPE_CONFIG:
            logger.warning(f"Unknown study type: {study_type}, defaulting to Clinical Trial")
            return STUDY_TYPE_CONFIG["Clinical Trial"]["required_sections"]
        return STUDY_TYPE_CONFIG[study_type]["required_sections"]

    def _modify_prompt_for_study_type(self, section_name, study_type):
        """Modify the prompt based on study type"""
        if study_type == "Systematic Literature Review":
            return f"""You are a medical writer generating the {section_name} section for a Systematic Literature Review protocol.
Focus only on literature review methodology and avoid any clinical trial elements."""
        elif study_type == "Meta-analysis":
            return f"""You are a medical writer generating the {section_name} section for a Meta-analysis protocol.
Focus only on meta-analysis methodology and avoid any clinical trial elements."""
        return None

    def generate_section(self, section_name, study_type, synopsis_content, existing_sections=None):
        '''Generate content for a specific protocol section'''
        try:
            # Input validation
            if not synopsis_content:
                raise ValueError("Synopsis content is required")
            if not section_name:
                raise ValueError("Section name is required")

            study_type = study_type.strip() if study_type else "Clinical Trial"

            # Log the generation attempt
            logger.info(f"Generating section {section_name} for {study_type}")
            logger.info(f"Synopsis length: {len(str(synopsis_content))}")

            # Check if section is required for study type
            required_sections = self._get_required_sections(study_type)
            if section_name not in required_sections:
                logger.info(f"Section {section_name} not required for {study_type} - skipping")
                return None

            # Get study type specific prompt if needed
            modified_prompt = self._modify_prompt_for_study_type(section_name, study_type)

            # Generate content
            content = self.gpt_handler.generate_section(
                section_name=section_name,
                synopsis_content=synopsis_content,
                previous_sections=existing_sections or {},
                prompt=modified_prompt
            )

            return content

        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            return None

    def generate_complete_protocol(self, study_type, synopsis_content):
        '''Generate all applicable protocol sections for the given study type'''
        try:
            # Input validation
            if not synopsis_content:
                raise ValueError("Synopsis content is required")

            study_type = study_type.strip() if study_type else "Clinical Trial"

            # Log the generation start
            logger.info(f"Generating complete protocol for {study_type}")
            logger.info(f"Synopsis length: {len(str(synopsis_content))}")

            # Get required sections for study type
            required_sections = self._get_required_sections(study_type)
            logger.info(f"Required sections: {required_sections}")

            sections = {}
            for section_name in required_sections:
                logger.info(f"Generating section: {section_name}")
                section_content = self.generate_section(
                    section_name=section_name,
                    study_type=study_type,
                    synopsis_content=synopsis_content,
                    existing_sections=sections
                )
                if section_content:
                    sections[section_name] = section_content

            return sections

        except Exception as e:
            logger.error(f"Error generating complete protocol: {str(e)}")
            raise