import logging
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager

logger = logging.getLogger(__name__)

# Define study type-specific sections
STUDY_TYPE_CONFIG = {
    "Clinical Trial": {
        "required_sections": [
            "title",
            "background",
            "objectives", 
            "study_design",
            "population",
            "procedures",
            "statistical_analysis",
            "safety"
        ]
    },
    "Systematic Literature Review": {
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
    "Meta-analysis": {
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
    "Real World Evidence": {
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
    "Consensus Method": {
        "required_sections": [
            "title",
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

    def _normalize_study_type(self, study_type):
        """Normalize study type string to match config keys"""
        study_type = study_type.lower() if study_type else ""
        if "systematic" in study_type or "literature review" in study_type or study_type == "slr":
            return "Systematic Literature Review"
        elif "meta" in study_type:
            return "Meta-analysis"
        elif "real world" in study_type.lower() or "rwe" in study_type.lower():
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

    def _get_rwe_prompt(self, section_name):
        """Get prompts for Real World Evidence studies"""
        prompts = {
            "title": "Generate title for Real World Evidence study...",
            "background": "Generate background section for Real World Evidence study focusing on the disease area, current evidence gaps, and rationale for using real-world data...",
            "objectives": "Generate objectives for Real World Evidence study including primary and secondary research questions...",
            "study_design": "Generate study design section for Real World Evidence study describing the overall approach, study period, and key design considerations...",
            "data_sources": "Generate data sources section describing the databases, registries, or other real-world data sources to be used...",
            "population": "Generate population section describing the target population, inclusion/exclusion criteria, and sample selection process...",
            "variables": "Generate variables section listing and defining all study variables including exposures, outcomes, covariates, and potential confounders...",
            "analytical_methods": "Generate analytical methods section describing statistical approaches, confounding control, and sensitivity analyses...",
            "limitations": "Generate limitations section discussing potential biases, data quality issues, and generalizability..."
        }
        return prompts.get(section_name)

    def _get_section_mapping(self, study_type):
        """Get section mapping based on study type"""
        base_mapping = {
            'study_design': 'study_design',
            'population': 'population',
            'procedures': 'procedures',
            'statistical': 'statistical_analysis',
            'safety': 'safety'
        }

        if study_type == "Real World Evidence":
            base_mapping.update({
                'study_design': 'study_design',
                'population': 'population',
                'procedures': 'variables',
                'statistical': 'analytical_methods',
                'safety': 'limitations',
                'data_sources': 'data_sources',
                'variables': 'variables',
                'analytical_methods': 'analytical_methods',
                'limitations': 'limitations'
            })

        return base_mapping

    def generate_section(self, section_name, study_type, synopsis_content, existing_sections=None):
        """Generate content for a specific protocol section"""
        try:
            # Input validation
            if not synopsis_content:
                raise ValueError("Synopsis content is required")
            if not section_name:
                raise ValueError("Section name is required")

            study_type = self._normalize_study_type(study_type)
            
            # Log generation attempt
            logger.info(f"Generating section {section_name} for {study_type}")
            logger.info(f"Synopsis length: {len(str(synopsis_content))}")

            # Get section mapping
            section_mapping = self._get_section_mapping(study_type)
            mapped_section = section_mapping.get(section_name, section_name)

            # Get required sections
            required_sections = STUDY_TYPE_CONFIG.get(study_type, STUDY_TYPE_CONFIG["Clinical Trial"])["required_sections"]

            # Check if section is required
            if mapped_section not in required_sections:
                logger.info(f"Section {mapped_section} not required for {study_type} - skipping")
                return None

            # Get study type-specific prompt
            prompt = self._modify_prompt_for_study_type(mapped_section, study_type)

            # Generate content
            content = self.gpt_handler.generate_section(
                section_name=mapped_section,
                synopsis_content=synopsis_content,
                previous_sections=existing_sections or {},
                prompt=prompt
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

            required_sections = STUDY_TYPE_CONFIG.get(study_type, STUDY_TYPE_CONFIG["Clinical Trial"])["required_sections"]
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
