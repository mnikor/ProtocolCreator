import os
import json
import logging
from openai import OpenAI
from prompts.analysis_prompts import SYNOPSIS_ANALYSIS_PROMPT
from prompts.section_prompts import SECTION_PROMPTS
from utils.template_manager import TemplateManager
from jsonschema import validate, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTHandler:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = "gpt-4"
        self.template_manager = TemplateManager()

    def _validate_analysis_json(self, analysis_dict):
        schema = {
            "type": "object",
            "required": ["study_type_and_design", "critical_parameters", "required_protocol_sections", "missing_information"],
            "properties": {
                "study_type_and_design": {
                    "type": "object",
                    "required": ["primary_classification", "design_type", "phase", "key_features"],
                    "properties": {
                        "primary_classification": {"type": "string"},
                        "design_type": {"type": "string"},
                        "phase": {"type": "string"},
                        "key_features": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "critical_parameters": {
                    "type": "object",
                    "required": ["population", "intervention", "control_comparator", "primary_endpoint", "secondary_endpoints"],
                    "properties": {
                        "population": {"type": "string"},
                        "intervention": {"type": "string"},
                        "control_comparator": {"type": "string"},
                        "primary_endpoint": {"type": "string"},
                        "secondary_endpoints": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "required_protocol_sections": {"type": "array", "items": {"type": "string"}},
                "missing_information": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        try:
            validate(instance=analysis_dict, schema=schema)
            return analysis_dict
        except ValidationError as e:
            raise ValueError(f"JSON validation failed: {str(e)}")

    def analyze_synopsis(self, synopsis_text):
        try:
            # Prepare the system and user messages
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a protocol analysis assistant. Your responses must:"
                        "\n1. Contain ONLY a valid JSON object"
                        "\n2. Start with '{' and end with '}'"
                        "\n3. Use double quotes for strings"
                        "\n4. Include no explanation or additional text"
                    )
                },
                {
                    "role": "user",
                    "content": SYNOPSIS_ANALYSIS_PROMPT.format(synopsis_text=synopsis_text)
                }
            ]
            
            logger.info("Sending synopsis analysis request to GPT-4")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.3  # Lower temperature for more consistent formatting
            )
            
            # Get and clean response
            response_text = response.choices[0].message.content.strip()
            
            # Log the raw response for debugging
            logger.debug(f"Raw GPT response: {response_text}")
            
            # Ensure the response starts with { and ends with }
            if not (response_text.startswith('{') and response_text.endswith('}')):
                raise ValueError("Response is not a valid JSON object")
                
            try:
                # Parse JSON with strict decoder
                analysis_dict = json.loads(
                    response_text,
                    strict=True  # Enforce strict JSON syntax
                )
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                logger.error(f"Problematic JSON: {response_text}")
                raise ValueError(f"Failed to parse JSON response: {str(e)}")
                
            # Validate structure
            validated_analysis = self._validate_analysis_json(analysis_dict)
            study_type = self._determine_study_phase(validated_analysis)
            
            return validated_analysis, study_type
            
        except Exception as e:
            logger.error(f"Error in analyze_synopsis: {str(e)}")
            logger.error(f"Full error context: {str(e.__class__.__name__)}")
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
