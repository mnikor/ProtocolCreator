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

    def analyze_synopsis(self, synopsis_text):
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a protocol analysis assistant. Analyze the synopsis and provide output in the following format:"
                        "\n=== STUDY TYPE AND DESIGN ==="
                        "\nPrimary Classification: [classification]"
                        "\nDesign Type: [type]"
                        "\nPhase: [phase]"
                        "\nKey Features:"
                        "\n- [feature 1]"
                        "\n- [feature 2]"
                        "\n=== CRITICAL PARAMETERS ==="
                        "\nPopulation: [description]"
                        "\nIntervention: [description]"
                        "\nControl/Comparator: [description]"
                        "\nPrimary Endpoint: [description]"
                        "\nSecondary Endpoints:"
                        "\n- [endpoint 1]"
                        "\n- [endpoint 2]"
                        "\n=== REQUIRED SECTIONS ==="
                        "\n- [section 1]"
                        "\n- [section 2]"
                        "\n=== MISSING INFORMATION ==="
                        "\n- [missing item 1]"
                        "\n- [missing item 2]"
                    )
                },
                {
                    "role": "user",
                    "content": f"Analyze this synopsis:\n\n{synopsis_text}"
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3
            )
            
            # Get response text
            analysis_text = response.choices[0].message.content.strip()
            
            # Parse structured text into dictionary
            analysis_dict = self._parse_structured_text(analysis_text)
            study_type = self._determine_study_phase(analysis_dict)
            
            return analysis_dict, study_type
            
        except Exception as e:
            logger.error(f"Error in analyze_synopsis: {str(e)}")
            raise Exception(f"Error analyzing synopsis: {str(e)}")

    def _parse_structured_text(self, text):
        '''Parse structured text into dictionary'''
        sections = {}
        current_section = None
        current_list = {}
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('=== ') and line.endswith(' ==='):
                if current_section:
                    sections[current_section.lower().replace(' ', '_')] = current_list
                current_section = line.strip('= ')
                current_list = {}
                continue
                
            if ': ' in line:
                key, value = line.split(': ', 1)
                if current_section == 'STUDY TYPE AND DESIGN':
                    if key == 'Key Features':
                        current_list[key.lower().replace(' ', '_')] = []
                    else:
                        current_list[key.lower().replace(' ', '_')] = value
                elif current_section == 'CRITICAL PARAMETERS':
                    if key == 'Secondary Endpoints':
                        current_list[key.lower().replace(' ', '_')] = []
                    else:
                        current_list[key.lower().replace(' ', '_')] = value
            elif line.startswith('- '):
                item = line[2:].strip()
                if current_section == 'REQUIRED SECTIONS':
                    if 'required_sections' not in sections:
                        sections['required_sections'] = []
                    sections['required_sections'].append(item)
                elif current_section == 'MISSING INFORMATION':
                    if 'missing_information' not in sections:
                        sections['missing_information'] = []
                    sections['missing_information'].append(item)
                elif current_section == 'STUDY TYPE AND DESIGN' and 'key_features' in current_list:
                    current_list['key_features'].append(item)
                elif current_section == 'CRITICAL PARAMETERS' and 'secondary_endpoints' in current_list:
                    current_list['secondary_endpoints'].append(item)
        
        if current_section:
            sections[current_section.lower().replace(' ', '_')] = current_list
        
        return sections

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

        except Exception as e:
            logger.error(f"Error determining study phase: {str(e)}")
            raise Exception(f"Error determining study phase: {str(e)}")

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

        except Exception as e:
            logger.error(f"Error generating section: {str(e)}")
            raise Exception(f"Error generating section: {str(e)}")
