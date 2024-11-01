import logging
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager
from utils.protocol_validator import ProtocolValidator

logger = logging.getLogger(__name__)

# Define unified study type configuration
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
        
        # Direct mappings
        direct_mappings = {
            "rwe": "rwe",
            "slr": "slr",
            "meta": "meta",
            "observational": "observational"
        }
        
        if study_type in direct_mappings:
            return direct_mappings[study_type]
        
        # Check phase studies
        if "phase" in study_type:
            phase = ''.join(filter(str.isdigit, study_type))
            return f"phase{phase}" if phase in ['1','2','3','4'] else "phase1"
        
        # Check composite terms
        if "real world" in study_type or "real-world" in study_type:
            return "rwe"
        if "systematic" in study_type and "review" in study_type:
            return "slr"
        if "meta" in study_type and "analysis" in study_type:
            return "meta"
        if "observation" in study_type:
            return "observational"
            
        return "phase1"  # Default fallback

    def get_required_sections(self, study_type):
        '''Get required sections for a study type'''
        try:
            # Normalize study type
            study_type = self._normalize_study_type(study_type)
            
            # Get study config
            study_config = STUDY_TYPE_CONFIG.get(study_type, STUDY_TYPE_CONFIG["phase1"])
            
            # Return required sections
            return study_config["required_sections"]
            
        except Exception as e:
            logger.error(f"Error getting required sections: {str(e)}")
            return STUDY_TYPE_CONFIG["phase1"]["required_sections"]

    def _get_normalized_section_name(self, section_name, study_type):
        """Get normalized section name using aliases"""
        try:
            study_config = STUDY_TYPE_CONFIG.get(study_type, {})
            aliases = study_config.get("section_aliases", {})
            
            # First check if section name is already in required sections
            if section_name in study_config.get("required_sections", []):
                return section_name
            
            # Then check aliases
            normalized_name = aliases.get(section_name.lower(), section_name)
            
            # Verify the normalized name is in required sections
            if normalized_name in study_config.get("required_sections", []):
                if normalized_name != section_name:
                    logger.info(f"Normalized section name from {section_name} to {normalized_name}")
                return normalized_name
            
            logger.error(f"Section name {section_name} not found in required sections or aliases")
            return None
            
        except Exception as e:
            logger.error(f"Error normalizing section name: {str(e)}")
            return None

    def generate_section(self, section_name, study_type, synopsis_content, existing_sections=None):
        """Generate a single protocol section"""
        try:
            if not synopsis_content:
                raise ValueError("Synopsis content is required")
            if not section_name:
                raise ValueError("Section name is required")

            # Normalize study type and section name
            study_type = self._normalize_study_type(study_type)
            normalized_section = self._get_normalized_section_name(section_name, study_type)

            if normalized_section is None:
                raise ValueError(f"Could not normalize section name: {section_name}")

            # Generate content
            content = self.gpt_handler.generate_section(
                section_name=normalized_section,
                synopsis_content=synopsis_content,
                previous_sections=existing_sections
            )

            if not content:
                raise ValueError(f"No content generated for {normalized_section}")

            return content

        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            raise

    def generate_complete_protocol(self, study_type, synopsis_content):
        """Generate complete protocol with all sections"""
        try:
            if not synopsis_content:
                raise ValueError("Synopsis content is required")

            study_type = self._normalize_study_type(study_type)
            required_sections = self.get_required_sections(study_type)
            sections = {}
            
            # Generate all sections
            for section_name in required_sections:
                content = self.generate_section(
                    section_name=section_name,
                    study_type=study_type,
                    synopsis_content=synopsis_content,
                    existing_sections=sections
                )
                if content:
                    sections[section_name] = content
            
            # Perform comprehensive validation
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
