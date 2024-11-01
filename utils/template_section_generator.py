import logging
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager
from utils.protocol_validator import ProtocolValidator

logger = logging.getLogger(__name__)

STUDY_TYPE_CONFIG = {
    "phase1": {
        "required_sections": [
            "title", "background", "objectives", "study_design", 
            "population", "procedures", "statistical_analysis", "safety"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "statistical_methods": "statistical_analysis",
            "study_procedures": "procedures"
        }
    },
    "phase2": {
        "required_sections": [
            "title", "background", "objectives", "study_design", 
            "population", "procedures", "statistical_analysis", "safety"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "statistical_methods": "statistical_analysis",
            "study_procedures": "procedures"
        }
    },
    "phase3": {
        "required_sections": [
            "title", "background", "objectives", "study_design", 
            "population", "procedures", "statistical_analysis", "safety"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "statistical_methods": "statistical_analysis",
            "study_procedures": "procedures"
        }
    },
    "phase4": {
        "required_sections": [
            "title", "background", "objectives", "study_design", 
            "population", "procedures", "statistical_analysis", "safety",
            "pharmacoeconomics"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "statistical_methods": "statistical_analysis",
            "study_procedures": "procedures",
            "economics": "pharmacoeconomics"
        }
    },
    "rwe": {
        "required_sections": [
            "title", "background", "objectives", "study_design", 
            "data_sources", "population", "variables", 
            "statistical_analysis", "limitations"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "methods": "study_design",
            "data": "data_sources"
        }
    },
    "slr": {
        "required_sections": [
            "title", "background", "objectives", "methods",
            "search_strategy", "data_extraction", "quality_assessment",
            "data_synthesis"
        ],
        "section_aliases": {
            "methodology": "methods",
            "extraction": "data_extraction",
            "synthesis": "data_synthesis"
        }
    },
    "meta": {
        "required_sections": [
            "title", "background", "objectives", "methods",
            "search_strategy", "data_extraction", "statistical_analysis",
            "quality_assessment"
        ],
        "section_aliases": {
            "methodology": "methods",
            "extraction": "data_extraction",
            "statistical": "statistical_analysis"
        }
    },
    "observational": {
        "required_sections": [
            "title", "background", "objectives", "study_design",
            "population", "variables", "data_collection",
            "statistical_analysis", "limitations"
        ],
        "section_aliases": {
            "methods": "study_design",
            "outcomes": "variables",
            "statistical": "statistical_analysis"
        }
    }
}

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
        self.template_manager = TemplateManager()
        self.validator = ProtocolValidator()

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
            study_config = STUDY_TYPE_CONFIG.get(study_type, STUDY_TYPE_CONFIG["phase1"])
            return study_config["required_sections"]
        except Exception as e:
            logger.error(f"Error getting required sections: {str(e)}")
            return STUDY_TYPE_CONFIG["phase1"]["required_sections"]

    def generate_section(self, section_name, study_type, synopsis_content, existing_sections=None):
        try:
            if not synopsis_content:
                raise ValueError("Synopsis content is required")
            if not section_name:
                raise ValueError("Section name is required")

            study_type = self._normalize_study_type(study_type)
            
            study_config = STUDY_TYPE_CONFIG.get(study_type)
            if not study_config:
                logger.warning(f"No config found for study type {study_type}, using phase1")
                study_config = STUDY_TYPE_CONFIG["phase1"]
                
            if section_name not in study_config["required_sections"]:
                raise ValueError(f"Section {section_name} not required for study type {study_type}")

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
            study_config = STUDY_TYPE_CONFIG.get(study_type)
            if not study_config:
                logger.warning(f"No config found for study type {study_type}, using phase1")
                study_config = STUDY_TYPE_CONFIG["phase1"]
                
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