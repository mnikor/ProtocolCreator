import logging
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager

logger = logging.getLogger(__name__)

# Define study type-specific sections
STUDY_TYPE_CONFIG = {
    "phase1": {
        "required_sections": [
            "title",
            "background",
            "objectives", 
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",  # Renamed from statistical
            "safety"
        ]
    },
    "phase2": {
        "required_sections": [
            "title",
            "background",
            "objectives", 
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",  # Renamed from statistical
            "safety"
        ]
    },
    "phase3": {
        "required_sections": [
            "title",
            "background",
            "objectives", 
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",  # Renamed from statistical
            "safety"
        ]
    },
    "phase4": {
        "required_sections": [
            "title",
            "background",
            "objectives", 
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",  # Renamed from statistical
            "safety"
        ]
    },
    "rwe": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "data_sources",
            "population",
            "variables",
            "analytical_methods",
            "limitations"
        ]
    },
    "slr": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "methods",
            "search_strategy",
            "selection_criteria",
            "data_extraction",
            "quality_assessment",
            "synthesis_methods"
        ]
    },
    "meta": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "methods",
            "search_strategy",
            "selection_criteria",
            "data_extraction",
            "quality_assessment",
            "statistical_synthesis"
        ]
    },
    "observational": {
        "required_sections": [
            "title",
            "background",
            "objectives",
            "study_design",
            "population",
            "variables",
            "data_collection",
            "analytical_methods",
            "limitations"
        ]
    }
}

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
        self.template_manager = TemplateManager()

    def get_required_sections(self, study_type=None):
        """Get required sections for the given study type"""
        if not study_type:
            return []
            
        study_type = self._normalize_study_type(study_type)
        return STUDY_TYPE_CONFIG.get(study_type, STUDY_TYPE_CONFIG["phase1"])["required_sections"]

    def _normalize_study_type(self, study_type):
        """Normalize study type string to match config keys"""
        study_type = study_type.lower() if study_type else ""
        if "systematic" in study_type or "literature review" in study_type:
            return "slr"
        elif "meta" in study_type:
            return "meta"
        elif "real world" in study_type.lower() or "rwe" in study_type.lower():
            return "rwe"
        elif "observational" in study_type:
            return "observational"
        elif "phase" in study_type:
            phase = ''.join(filter(str.isdigit, study_type))
            return f"phase{phase}" if phase in ['1','2','3','4'] else "phase1"
        return "phase1"

    def generate_section(self, section_name, study_type, synopsis_content, existing_sections=None):
        """Generate content for a specific protocol section"""
        try:
            if not synopsis_content:
                raise ValueError("Synopsis content is required")
            if not section_name:
                raise ValueError("Section name is required")

            study_type = self._normalize_study_type(study_type)
            
            # Log generation attempt
            logger.info(f"Generating section {section_name} for {study_type}")
            logger.info(f"Synopsis length: {len(str(synopsis_content))}")

            # Get required sections
            required_sections = self.get_required_sections(study_type)
            
            # Check if section is required
            if section_name not in required_sections:
                logger.info(f"Section {section_name} not required for {study_type} - skipping")
                return None

            # Generate content
            content = self.gpt_handler.generate_section(
                section_name=section_name,
                synopsis_content=synopsis_content,
                previous_sections=existing_sections or {},
                prompt=None
            )

            return content

        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            return None

    def generate_complete_protocol(self, study_type, synopsis_content):
        """Generate all applicable protocol sections"""
        try:
            if not synopsis_content:
                raise ValueError("Synopsis content is required")

            study_type = self._normalize_study_type(study_type)
            
            # Log generation start
            logger.info(f"Generating complete protocol for {study_type}")
            logger.info(f"Synopsis length: {len(str(synopsis_content))}")

            required_sections = self.get_required_sections(study_type)
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
