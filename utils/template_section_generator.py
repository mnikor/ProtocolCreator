import logging
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager
from utils.protocol_validator import ProtocolValidator
from config.study_type_definitions import COMPREHENSIVE_STUDY_CONFIGS as STUDY_TYPE_CONFIG

logger = logging.getLogger(__name__)

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
        self.template_manager = TemplateManager()
        self.validator = ProtocolValidator()
        self.study_configs = STUDY_TYPE_CONFIG  # Use imported config

    def _normalize_study_type(self, study_type):
        """Normalize study type string to match config keys"""
        if not study_type:
            return "phase1"

        study_type = study_type.lower().strip()
        
        direct_mappings = {
            "rwe": "rwe",
            "slr": "slr",
            "meta": "meta",
            "observational": "observational"
        }
        
        if study_type in direct_mappings:
            return direct_mappings[study_type]
        
        if "phase" in study_type:
            phase = ''.join(filter(str.isdigit, study_type))
            return f"phase{phase}" if phase in ['1','2','3','4'] else "phase1"
        
        if "real world" in study_type or "real-world" in study_type:
            return "rwe"
        if "systematic" in study_type and "review" in study_type:
            return "slr"
        if "meta" in study_type and "analysis" in study_type:
            return "meta"
        if "observation" in study_type:
            return "observational"
            
        return "phase1"

    def get_required_sections(self, study_type):
        '''Get required sections for a study type'''
        try:
            study_type = self._normalize_study_type(study_type)
            study_config = self.study_configs.get(study_type, self.study_configs["phase1"])
            return study_config["required_sections"]
        except Exception as e:
            logger.error(f"Error getting required sections: {str(e)}")
            return self.study_configs["phase1"]["required_sections"]

    def generate_section(self, section_name, study_type, synopsis_content, existing_sections=None):
        try:
            if not synopsis_content:
                raise ValueError("Synopsis content is required")
            if not section_name:
                raise ValueError("Section name is required")

            study_type = self._normalize_study_type(study_type)
            
            # Get study config using class property
            study_config = self.study_configs.get(study_type)
            if not study_config:
                logger.warning(f"No config found for study type {study_type}, using phase1")
                study_config = self.study_configs["phase1"]
                
            # Check if section is required for this study type
            if section_name not in study_config["required_sections"]:
                raise ValueError(f"Section {section_name} not required for study type {study_type}")

            # Generate content
            content = self.gpt_handler.generate_section(
                section_name=section_name,
                synopsis_content=synopsis_content,
                previous_sections=existing_sections
            )

            if not content:
                raise ValueError(f"No content generated for {section_name}")

            return content

        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            raise

    def generate_complete_protocol(self, study_type, synopsis_content):
        try:
            if not synopsis_content:
                raise ValueError("Synopsis content is required")

            study_type = self._normalize_study_type(study_type)
            study_config = self.study_configs.get(study_type)
            if not study_config:
                logger.warning(f"No config found for study type {study_type}, using phase1")
                study_config = self.study_configs["phase1"]
                
            required_sections = study_config["required_sections"]
            sections = {}
            
            for section_name in required_sections:
                try:
                    content = self.generate_section(
                        section_name=section_name,
                        study_type=study_type,
                        synopsis_content=synopsis_content,
                        existing_sections=sections
                    )
                    if content:
                        sections[section_name] = content
                except Exception as e:
                    logger.error(f"Error generating section {section_name}: {str(e)}")
                    continue
            
            validation_results = self.validator.validate_protocol(sections, study_type)
            validation_report = self.validator.generate_validation_report(validation_results)
            
            return {
                "sections": sections,
                "validation_results": validation_results,
                "validation_report": validation_report
            }

        except Exception as e:
            logger.error(f"Error generating protocol: {str(e)}")
            raise
