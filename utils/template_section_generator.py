import logging
from typing import Dict, Optional
from utils.gpt_handler import GPTHandler
from config.study_type_definitions import COMPREHENSIVE_STUDY_CONFIGS
from prompts.section_templates import SECTION_TEMPLATES, CONDITIONAL_SECTIONS, DEFAULT_TEMPLATES

logger = logging.getLogger(__name__)

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
    
    def get_section_template(self, section_name: str, study_type: str) -> str:
        """Get the appropriate template for the section based on study type"""
        if study_type in SECTION_TEMPLATES:
            study_templates = SECTION_TEMPLATES[study_type]
            if section_name in study_templates:
                return study_templates[section_name]
        return DEFAULT_TEMPLATES.get(section_name, f"Generate content for {section_name} section")

    def should_include_section(self, section_name: str, study_type: str) -> bool:
        """Determine if a section should be included based on study type rules"""
        if study_type in CONDITIONAL_SECTIONS:
            study_rules = CONDITIONAL_SECTIONS[study_type]
            if section_name in study_rules['excluded']:
                return False
            if section_name in study_rules['required']:
                return True
            # Optional sections included by default
            return section_name in study_rules['optional']
        return True

    def generate_section(self, section_name: str, synopsis_content: str, study_type: str) -> str:
        """Generate a section using appropriate template and validation"""
        try:
            # Check if section should be included
            if not self.should_include_section(section_name, study_type):
                logger.info(f"Section {section_name} excluded for study type {study_type}")
                return ""
            
            # Get appropriate template and format prompt
            template = self.get_section_template(section_name, study_type)
            prompt = template.format(synopsis=synopsis_content)
            
            # Generate content using GPT
            return self.gpt_handler.generate_content(prompt)
            
        except Exception as e:
            logger.error(f"Error generating {section_name}: {str(e)}")
            raise

    def generate_complete_protocol(self, study_type: str, synopsis_content: str) -> Dict:
        """Generate complete protocol with appropriate sections"""
        try:
            # Get study configuration
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            sections = study_config.get('required_sections', [])
            
            # Generate each section
            generated_sections = {}
            for section_name in sections:
                if self.should_include_section(section_name, study_type):
                    section_content = self.generate_section(
                        section_name=section_name,
                        synopsis_content=synopsis_content,
                        study_type=study_type
                    )
                    if section_content:
                        generated_sections[section_name] = section_content
            
            return {"sections": generated_sections}
            
        except Exception as e:
            logger.error(f"Error generating protocol: {str(e)}")
            raise
