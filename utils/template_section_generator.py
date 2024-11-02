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
        """Generate a section using appropriate template and validation"""
        try:
            if not synopsis_content.strip():
                raise ValueError("Synopsis content is empty")
            
            if not self.should_include_section(section_name, study_type):
                logger.info(f"Section {section_name} excluded for study type {study_type}")
                return ""
            
            # Get template and create context-aware prompt
            template = self.get_section_template(section_name, study_type)
            context_prompt = f'''
Based on the following study synopsis:
---
{synopsis_content}
---

{template}

Important formatting instructions:
1. Use markdown-style *asterisks* for italic text
2. Always format placeholders and recommendations in italics using *asterisks*
3. Format missing information as: [PLACEHOLDER: *missing information description*]
4. Format recommendations as: [RECOMMENDED: *specific recommendation*]

Example format:
"The study will enroll [PLACEHOLDER: *specific number to be determined based on power calculations*] participants.
[RECOMMENDED: *Consider adding stratification factors based on disease severity*]."
'''
            # Generate content
            return self.gpt_handler.generate_content(context_prompt)
            
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
