import logging
from typing import Dict, Optional
from utils.gpt_handler import GPTHandler
from config.study_type_definitions import COMPREHENSIVE_STUDY_CONFIGS

logger = logging.getLogger(__name__)

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
        
    def generate_complete_protocol(
        self, study_type: str, synopsis_content: str
    ) -> Dict:
        try:
            # Get study configuration
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            sections = study_config.get('required_sections', [])
            
            # Generate each section
            generated_sections = {}
            for section_name in sections:
                section_content = self.gpt_handler.generate_section(
                    section_name=section_name,
                    synopsis_content=synopsis_content,
                    study_type=study_type
                )
                generated_sections[section_name] = section_content
            
            return {"sections": generated_sections}
            
        except Exception as e:
            logger.error(f"Error generating protocol: {str(e)}")
            raise
