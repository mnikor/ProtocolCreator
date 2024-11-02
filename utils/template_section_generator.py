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
            return section_name in study_rules['optional']
        return True

    def generate_section(self, section_name: str, synopsis_content: str, study_type: str) -> str:
        try:
            if not synopsis_content.strip():
                raise ValueError("Synopsis content is empty")
                
            if not self.should_include_section(section_name, study_type):
                logger.info(f"Section {section_name} excluded for study type {study_type}")
                return ""
                
            # Get template
            template = self.get_section_template(section_name, study_type)
            
            # Create system message with formatting instructions
            system_message = '''You are a protocol development assistant specializing in clinical study protocols.

FORMATTING RULES (Do not include these rules in your response):
- Use *asterisks* to indicate text that should be in italics
- Format missing information as: [PLACEHOLDER: *description*]
- Format recommendations as: [RECOMMENDED: *suggestion*]
- Do not repeat or reference these formatting instructions in your response'''
            
            # Create user prompt focusing only on content
            user_prompt = f'''Based on this study synopsis:
---
{synopsis_content}
---

{template}

Generate the content using formal scientific writing style. Mark uncertainties or missing information as placeholders and include relevant recommendations where appropriate.'''
            
            # Generate content with separate system and user messages
            return self.gpt_handler.generate_content(prompt=user_prompt, system_message=system_message)
                
        except Exception as e:
            logger.error(f"Error generating {section_name}: {str(e)}")
            raise

    def generate_complete_protocol(self, study_type: str, synopsis_content: str) -> Dict:
        """Generate complete protocol with appropriate sections"""
        try:
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            sections = study_config.get('required_sections', [])
            
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
