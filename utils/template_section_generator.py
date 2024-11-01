import logging
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager

logger = logging.getLogger(__name__)

# Define unified study type configuration
STUDY_TYPE_CONFIG = {
    "phase1": {
        "required_sections": [
            "title",
            "background",
            "objectives", 
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",
            "safety"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "statistical_methods": "statistical_analysis",
            "study_procedures": "procedures",
            "procedures": "procedures"
        }
    },
    "phase2": {
        "required_sections": [
            "title",
            "background",
            "objectives", 
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",
            "safety"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "statistical_methods": "statistical_analysis",
            "study_procedures": "procedures",
            "procedures": "procedures"
        }
    },
    "phase3": {
        "required_sections": [
            "title",
            "background",
            "objectives", 
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",
            "safety"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "statistical_methods": "statistical_analysis",
            "study_procedures": "procedures",
            "procedures": "procedures"
        }
    },
    "phase4": {
        "required_sections": [
            "title",
            "background",
            "objectives", 
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",
            "safety"
        ],
        "section_aliases": {
            "statistical": "statistical_analysis",
            "statistical_methods": "statistical_analysis",
            "study_procedures": "procedures",
            "procedures": "procedures"
        }
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
            "statistical_analysis",
            "limitations"
        ],
        "section_aliases": {
            "analytical_methods": "statistical_analysis",
            "data_sources": "procedures",
            "procedures": "data_sources"
        }
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
            "statistical_analysis",
            "synthesis_methods"
        ],
        "section_aliases": {
            "methods": "study_design",
            "synthesis_methods": "statistical_analysis",
            "statistical": "statistical_analysis",
            "data_extraction": "procedures",
            "procedures": "data_extraction"
        }
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
            "statistical_analysis",
            "quality_assessment"
        ],
        "section_aliases": {
            "methods": "study_design",
            "statistical_synthesis": "statistical_analysis",
            "statistical": "statistical_analysis",
            "data_extraction": "procedures",
            "procedures": "data_extraction"
        }
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
            "statistical_analysis",
            "limitations"
        ],
        "section_aliases": {
            "analytical_methods": "statistical_analysis",
            "statistical": "statistical_analysis",
            "data_collection": "procedures",
            "procedures": "data_collection"
        }
    }
}

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
        self.template_manager = TemplateManager()

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

    def _normalize_study_type(self, study_type):
        """Normalize study type string to match config keys"""
        if not study_type:
            return "phase1"

        study_type = study_type.lower().strip()

        # Define mappings for various study type names
        type_mappings = {
            ("systematic", "literature", "review"): "slr",
            ("slr",): "slr",
            ("meta",): "meta",
            ("meta-analysis", "metaanalysis"): "meta",
            ("real world", "rwe", "real-world"): "rwe",
            ("observational",): "observational"
        }

        # Check phase studies first
        if "phase" in study_type:
            phase = ''.join(filter(str.isdigit, study_type))
            return f"phase{phase}" if phase in ['1','2','3','4'] else "phase1"

        # Check other study types
        for keywords, mapped_type in type_mappings.items():
            if any(all(word in study_type for word in keyword_tuple) for keyword_tuple in [keywords]):
                return mapped_type

        return "phase1"

    def _get_normalized_section_name(self, section_name, study_type):
        """Get normalized section name using aliases"""
        study_config = STUDY_TYPE_CONFIG.get(study_type, {})
        aliases = study_config.get("section_aliases", {})
        
        # First check if section name is already in required sections
        if section_name in study_config.get("required_sections", []):
            return section_name
        
        # Then check aliases
        normalized_name = aliases.get(section_name, section_name)
        
        # Verify the normalized name is in required sections
        if normalized_name not in study_config.get("required_sections", []):
            logger.error(f"Normalized section name {normalized_name} not in required sections")
            return None
        
        if normalized_name != section_name:
            logger.info(f"Normalized section name from {section_name} to {normalized_name}")
        
        return normalized_name

    def generate_section(self, section_name, study_type, synopsis_content, existing_sections=None):
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

            # Log generation attempt
            logger.info(f"Generating section {normalized_section} for {study_type}")

            # Get template and study config
            template = self.template_manager.get_section_template(study_type, normalized_section)

            # Generate content
            content = self.gpt_handler.generate_section(
                section_name=normalized_section,
                synopsis_content=synopsis_content,
                previous_sections=existing_sections,
                prompt=template.get('prompt') if template else None
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

            # Get required sections
            study_config = STUDY_TYPE_CONFIG.get(study_type, STUDY_TYPE_CONFIG["phase1"])
            required_sections = study_config["required_sections"]

            logger.info(f"Generating protocol for {study_type} with sections: {required_sections}")

            sections = {}
            for section_name in required_sections:
                content = self.generate_section(
                    section_name=section_name,
                    study_type=study_type,
                    synopsis_content=synopsis_content,
                    existing_sections=sections
                )
                if content:
                    sections[section_name] = content

            return sections

        except Exception as e:
            logger.error(f"Error generating complete protocol: {str(e)}")
            raise
