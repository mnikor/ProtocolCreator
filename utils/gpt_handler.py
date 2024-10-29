import os
import json
import logging
from openai import OpenAI
from prompts.analysis_prompts import SYNOPSIS_ANALYSIS_PROMPT
from prompts.section_prompts import SECTION_PROMPTS
from utils.template_manager import TemplateManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTHandler:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = "gpt-4"
        self.template_manager = TemplateManager()

    def _validate_analysis_json(self, analysis_dict):
        """Validate the JSON structure of analysis response"""
        required_fields = {
            "study_type_and_design": ["primary_classification", "design_type", "phase", "key_features"],
            "critical_parameters": ["population", "intervention", "control_comparator", "primary_endpoint", "secondary_endpoints"],
            "required_protocol_sections": [],
            "missing_information": []
        }

        try:
            for field, subfields in required_fields.items():
                if field not in analysis_dict:
                    raise ValueError(f"Missing required field: {field}")
                if subfields:
                    for subfield in subfields:
                        if subfield not in analysis_dict[field]:
                            raise ValueError(f"Missing required subfield: {subfield} in {field}")
            return analysis_dict
        except Exception as e:
            raise ValueError(f"Invalid analysis structure: {str(e)}")

    def analyze_synopsis(self, synopsis_text):
        """Analyze synopsis using GPT-4"""
        try:
            prompt = SYNOPSIS_ANALYSIS_PROMPT.format(synopsis_text=synopsis_text)
            logger.info("Sending synopsis analysis request to GPT-4")
            
            # Ensure strict JSON response
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "system",
                    "content": "You are a protocol analysis assistant. Always respond with valid JSON only."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                response_format={"type": "json_object"}
            )
            
            # Get response content
            analysis_json = response.choices[0].message.content
            
            # Clean response - remove any non-JSON content
            analysis_json = analysis_json.strip()
            if analysis_json.startswith('"') or analysis_json.startswith("'"):
                analysis_json = analysis_json[1:]
            if analysis_json.endswith('"') or analysis_json.endswith("'"):
                analysis_json = analysis_json[:-1]
                
            # Parse and validate JSON
            try:
                validated_analysis = json.loads(analysis_json)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}, Content: {analysis_json}")
                raise ValueError(f"Invalid JSON response: {str(e)}")
                
            # Validate structure
            self._validate_analysis_json(validated_analysis)
            study_type = self._determine_study_phase(validated_analysis)
            
            return validated_analysis, study_type
            
        except Exception as e:
            logger.error(f"Error analyzing synopsis: {str(e)}")
            raise Exception(f"Error analyzing synopsis: {str(e)}")

    def _determine_study_phase(self, analysis):
        """Determine study phase from analysis"""
        try:
            if not isinstance(analysis, dict):
                raise ValueError("Analysis must be a dictionary")

            study_design = analysis.get("study_type_and_design", {})
            if not isinstance(study_design, dict):
                raise ValueError("study_type_and_design must be a dictionary")

            phase = study_design.get("phase", "").lower()
            logger.info(f"Detected study phase: {phase}")
            
            # Map phase string to template type
            if "1" in phase or "i" in phase:
                return "phase1"
            elif "2" in phase or "ii" in phase:
                return "phase2"
            elif "3" in phase or "iii" in phase:
                return "phase3"
            else:
                logger.warning("Study phase unclear, defaulting to phase1")
                return "phase1"  # Default to phase 1 if unclear

        except (AttributeError, KeyError) as e:
            logger.error(f"Error parsing study phase: {str(e)}")
            raise ValueError(f"Error parsing study phase: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error determining study phase: {str(e)}")
            raise Exception(f"Unexpected error determining study phase: {str(e)}")

    def generate_section(self, section_name, synopsis_content, previous_sections=None, study_type=None):
        """Generate a specific protocol section using appropriate template"""
        if not section_name or not synopsis_content:
            raise ValueError("Section name and synopsis content are required")

        try:
            section_prompt = SECTION_PROMPTS.get(section_name)
            if not section_prompt:
                raise ValueError(f"No prompt template found for section: {section_name}")

            # Get template-specific guidance
            template_guidance = ""
            if study_type:
                try:
                    template = self.template_manager.get_section_template(study_type, section_name)
                    template_guidance = f"\n\nTemplate Requirements:\n{json.dumps(template, indent=2)}"
                except Exception as e:
                    logger.warning(f"Could not load template - {str(e)}")

            prompt = section_prompt.format(
                synopsis_content=synopsis_content,
                previous_sections=previous_sections or "",
                template_guidance=template_guidance
            )

            logger.info(f"Generating section: {section_name}")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{
                    "role": "system",
                    "content": "You are a medical writer generating protocol sections. Provide detailed, scientifically accurate content."
                }, {
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.choices[0].message.content

        except ValueError as e:
            logger.error(f"Section generation error: {str(e)}")
            raise ValueError(f"Section generation error: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating section: {str(e)}")
            raise Exception(f"Error generating section: {str(e)}")
