import logging
from datetime import datetime
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager
from utils.protocol_validator import ProtocolValidator
from config.study_type_definitions import COMPREHENSIVE_STUDY_CONFIGS as STUDY_TYPE_CONFIG

logger = logging.getLogger(__name__)

STUDY_TYPE_GUIDELINES = {
    'phase1': 'SPIRIT',
    'phase2': 'SPIRIT',
    'phase3': 'SPIRIT',
    'phase4': 'SPIRIT',
    'slr': 'PRISMA',
    'meta': 'PRISMA',
    'observational': 'STROBE',
    'rwe': 'RECORD'
}

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
        self.template_manager = TemplateManager()
        self.validator = ProtocolValidator()
        self.study_configs = STUDY_TYPE_CONFIG

    def _normalize_study_type(self, study_type):
        """Normalize study type string to match config keys"""
        if not study_type:
            return "phase1"

        study_type = study_type.lower().strip()
        
        # Direct mappings for special study types
        direct_mappings = {
            "rwe": "rwe",
            "slr": "slr",
            "meta": "meta",
            "observational": "observational",
            "systematic review": "slr",
            "meta-analysis": "meta",
            "real world evidence": "rwe"
        }
        
        # Check direct mappings first
        if study_type in direct_mappings:
            logger.info(f"Mapped study type {study_type} to {direct_mappings[study_type]}")
            return direct_mappings[study_type]
        
        # Handle phase studies
        if "phase" in study_type:
            phase = ''.join(filter(str.isdigit, study_type))
            normalized = f"phase{phase}" if phase in ['1','2','3','4'] else "phase1"
            logger.info(f"Normalized phase study type {study_type} to {normalized}")
            return normalized
        
        # Handle special cases
        if any(term in study_type for term in ["real world", "real-world"]):
            logger.info(f"Mapped {study_type} to rwe")
            return "rwe"
        if "systematic" in study_type and "review" in study_type:
            logger.info(f"Mapped {study_type} to slr")
            return "slr"
        if "meta" in study_type and "analysis" in study_type:
            logger.info(f"Mapped {study_type} to meta")
            return "meta"
        if "observation" in study_type:
            logger.info(f"Mapped {study_type} to observational")
            return "observational"
            
        logger.warning(f"Could not specifically map {study_type}, defaulting to phase1")
        return "phase1"

    def get_required_sections(self, study_type):
        """Get required sections for a study type"""
        try:
            study_type = self._normalize_study_type(study_type)
            study_config = self.study_configs.get(study_type)
            
            if not study_config:
                logger.warning(f"No config found for {study_type}, using phase1 config")
                study_config = self.study_configs["phase1"]
            
            logger.info(f"Retrieved sections for {study_type}: {study_config['required_sections']}")
            return study_config["required_sections"]
            
        except Exception as e:
            logger.error(f"Error getting required sections: {str(e)}")
            return self.study_configs["phase1"]["required_sections"]

    def generate_section(self, section_name, study_type, synopsis_content, existing_sections=None):
        """Generate a single protocol section"""
        try:
            start_time = datetime.now()
            logger.info(f"Starting generation of {section_name} at {start_time}")

            if not synopsis_content:
                raise ValueError("Synopsis content is required")
            if not section_name:
                raise ValueError("Section name is required")

            # Log generation attempt
            logger.info(f"Attempting to generate {section_name} for {study_type}")
            
            study_type = self._normalize_study_type(study_type)
            study_config = self.study_configs.get(study_type)
            
            if not study_config:
                logger.warning(f"No config found for study type {study_type}, using phase1")
                study_config = self.study_configs["phase1"]
            
            logger.info(f"Study config: {study_config}")
            
            # Check if section is required
            if section_name not in study_config["required_sections"]:
                raise ValueError(f"Section {section_name} not required for study type {study_type}")

            # Get applicable guidelines
            guideline = STUDY_TYPE_GUIDELINES.get(study_type, 'SPIRIT')
            
            # Add guideline requirements to prompt
            prompt = f'''Generate {section_name} following {guideline} guidelines.
                        Include all mandatory {guideline} elements for this section.
                        Ensure compliance with reporting standards.
                        
                        Previous content:
                        {synopsis_content}'''

            # Generate content with guideline awareness
            content = self.gpt_handler.generate_section(
                section_name=section_name,
                synopsis_content=synopsis_content,
                previous_sections=existing_sections,
                prompt=prompt
            )

            if not content:
                raise ValueError(f"No content generated for {section_name}")

            # Validate against guideline requirements
            validation_results = self.validator.validate_against_guidelines(
                content,
                section_name,
                guideline
            )
            
            if validation_results.get("missing_elements"):
                logger.warning(f"Missing {guideline} elements: {validation_results['missing_elements']}")
                
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            logger.info(f"Completed {section_name} in {generation_time:.2f}s")

            return {
                'content': content,
                'generation_time': generation_time,
                'validation_results': validation_results
            }

        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            raise

    def generate_complete_protocol(self, study_type, synopsis_content):
        """Generate complete protocol with all required sections"""
        try:
            if not synopsis_content:
                raise ValueError("Synopsis content is required")

            logger.info(f"Starting complete protocol generation for {study_type}")
            study_type = self._normalize_study_type(study_type)
            study_config = self.study_configs.get(study_type)
            
            if not study_config:
                logger.warning(f"No config found for study type {study_type}, using phase1")
                study_config = self.study_configs["phase1"]
            
            required_sections = study_config["required_sections"]
            logger.info(f"Required sections for {study_type}: {required_sections}")
            
            sections = {}
            generation_errors = []
            guideline_validations = []
            
            # Get applicable guideline
            guideline = STUDY_TYPE_GUIDELINES.get(study_type, 'SPIRIT')
            
            for section_name in required_sections:
                try:
                    logger.info(f"Generating section: {section_name}")
                    result = self.generate_section(
                        section_name=section_name,
                        study_type=study_type,
                        synopsis_content=synopsis_content,
                        existing_sections=sections
                    )
                    
                    if result:
                        sections[section_name] = result['content']
                        logger.info(f"Successfully generated {section_name}")
                        
                        # Store validation results
                        guideline_validations.append({
                            'section': section_name,
                            'validation': result['validation_results']
                        })
                    else:
                        raise ValueError(f"No content generated for {section_name}")
                        
                except Exception as e:
                    error_msg = f"Error generating section {section_name}: {str(e)}"
                    logger.error(error_msg)
                    generation_errors.append(error_msg)
                    continue
            
            # Validate complete protocol
            logger.info("Starting protocol validation")
            validation_results = self.validator.validate_protocol(sections, study_type)
            validation_report = self.validator.generate_validation_report(validation_results)
            
            logger.info(f"Protocol generation completed. Generated {len(sections)}/{len(required_sections)} sections")
            
            return {
                "sections": sections,
                "validation_results": validation_results,
                "validation_report": validation_report,
                "generation_errors": generation_errors,
                "guideline_validations": guideline_validations,
                "guideline": guideline
            }
            
        except Exception as e:
            logger.error(f"Error generating protocol: {str(e)}")
            raise
