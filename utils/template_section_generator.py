import logging
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager

logger = logging.getLogger(__name__)

# Define study type-specific sections
STUDY_TYPE_CONFIG = {
    "Clinical Trial": {
        "required_sections": [
            "title",  # New
            "background",
            "objectives", 
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",  # Renamed
            "safety"
        ]
    },
    "Systematic Literature Review": {
        "required_sections": [
            "title",  # New
            "background",
            "objectives",
            "methods",
            "search_strategy",
            "selection_criteria",
            "data_extraction",
            "quality_assessment",
            "synthesis_methods"  # Renamed from statistical
        ]
    },
    "Meta-analysis": {
        "required_sections": [
            "title",  # New
            "background",
            "objectives",
            "methods",
            "search_strategy", 
            "selection_criteria",
            "data_extraction",
            "quality_assessment",
            "statistical_synthesis"  # Renamed
        ]
    },
    "Real World Evidence": {
        "required_sections": [
            "title",  # New
            "background",
            "objectives",
            "study_design",
            "data_sources",
            "population",
            "variables",
            "analytical_methods",  # Renamed from statistical
            "limitations"
        ]
    },
    "Consensus Method": {
        "required_sections": [
            "title",  # New
            "background",
            "objectives",
            "methods",
            "expert_panel",
            "consensus_process",
            "voting_criteria",
            "analysis"
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
        study_type_key = self._normalize_study_type(study_type)
        
        if study_type_key not in STUDY_TYPE_CONFIG:
            logger.warning(f"Unknown study type: {study_type}, defaulting to Clinical Trial")
            return STUDY_TYPE_CONFIG["Clinical Trial"]["required_sections"]
            
        return STUDY_TYPE_CONFIG[study_type_key]["required_sections"]

    def _normalize_study_type(self, study_type):
        """Normalize study type string to match config keys"""
        study_type = study_type.lower()
        if "systematic" in study_type or "literature review" in study_type or study_type == "slr":
            return "Systematic Literature Review"
        elif "meta" in study_type:
            return "Meta-analysis"
        elif "real world" in study_type or "rwe" in study_type:
            return "Real World Evidence"
        elif "consensus" in study_type:
            return "Consensus Method"
        return "Clinical Trial"

    def _modify_prompt_for_study_type(self, section_name, study_type):
        """Modify the prompt based on study type"""
        study_type = study_type.lower()
        
        if "systematic" in study_type or "literature review" in study_type:
            return self._get_slr_prompt(section_name)
        elif "meta-analysis" in study_type:
            return self._get_meta_analysis_prompt(section_name)
        elif "real world" in study_type:
            return self._get_rwe_prompt(section_name)
        elif "consensus" in study_type:
            return self._get_consensus_prompt(section_name)
            
        return None

    def generate_section(self, section_name, study_type, synopsis_content, existing_sections=None):
        """Generate content for a specific protocol section"""
        try:
            # Input validation
            if not synopsis_content:
                raise ValueError("Synopsis content is required")
            if not section_name:
                raise ValueError("Section name is required")

            study_type = self._normalize_study_type(study_type)
            
            # Log the generation attempt
            logger.info(f"Generating section {section_name} for {study_type}")
            logger.info(f"Synopsis length: {len(str(synopsis_content))}")

            # Get required sections for study type
            required_sections = self._get_required_sections(study_type)
            
            # Map old section names to new ones based on study type
            section_mapping = {
                'study_design': 'methods',
                'population': 'selection_criteria',
                'procedures': 'data_extraction',
                'statistical': 'synthesis_methods' if study_type == "Systematic Literature Review" else
                             'statistical_synthesis' if study_type == "Meta-analysis" else
                             'analytical_methods' if study_type == "Real World Evidence" else
                             'statistical_analysis'
            }
            
            # Check if section is required (using mapped name if necessary)
            mapped_section = section_mapping.get(section_name, section_name)
            if mapped_section not in required_sections:
                logger.info(f"Section {mapped_section} not required for {study_type} - skipping")
                return None

            # Generate content
            content = self.gpt_handler.generate_section(
                section_name=mapped_section,
                synopsis_content=synopsis_content,
                previous_sections=existing_sections or {},
                prompt=None
            )

            return content

        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            return None

    def generate_complete_protocol(self, study_type, synopsis_content):
        """Generate all applicable protocol sections for the given study type"""
        try:
            if not synopsis_content:
                raise ValueError("Synopsis content is required")

            study_type = self._normalize_study_type(study_type)
            
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
