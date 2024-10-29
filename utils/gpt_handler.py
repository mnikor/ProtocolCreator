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
        """Analyze synopsis with improved handling of missing and empty sections"""
        try:
            # Default values for all possible sections
            default_analysis = {
                'study_type_and_design': {
                    'primary_classification': 'Not specified',
                    'design_type': 'Not specified',
                    'phase': 'Not specified',
                    'key_features': []
                },
                'critical_parameters': {
                    'population': 'Not specified',
                    'intervention': 'Not specified',
                    'control_comparator': 'Not specified',
                    'primary_endpoint': 'Not specified',
                    'secondary_endpoints': []
                },
                'required_sections': [],
                'missing_information': []
            }

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a protocol analysis assistant. Analyze the synopsis thoroughly and provide a complete structured output. "
                        "For any missing or unclear information, explicitly state 'Not specified' or 'None' - do not leave any fields empty. "
                        "If information is missing, provide a detailed explanation in the Missing Information section.\n\n"
                        "Required output format:\n"
                        "=== STUDY TYPE AND DESIGN ===\n"
                        "Primary Classification: [classification or 'Not specified']\n"
                        "Design Type: [type or 'Not specified']\n"
                        "Phase: [phase or 'Not specified']\n"
                        "Key Features:\n"
                        "- [feature 1 or 'None if no features identified']\n"
                        "\n=== CRITICAL PARAMETERS ===\n"
                        "Population: [description or 'Not specified']\n"
                        "Intervention: [description or 'Not specified']\n"
                        "Control/Comparator: [description or 'Not specified']\n"
                        "Primary Endpoint: [description or 'Not specified']\n"
                        "Secondary Endpoints:\n"
                        "- [endpoint or 'None if no secondary endpoints']\n"
                        "\n=== REQUIRED SECTIONS ===\n"
                        "- [Must list ALL required protocol sections]\n"
                        "\n=== MISSING INFORMATION ===\n"
                        "- [List each missing element with explanation]\n"
                    )
                },
                {
                    "role": "user",
                    "content": f"Analyze this synopsis thoroughly:\n\n{synopsis_text}"
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3
            )
            
            # Get response text
            analysis_text = response.choices[0].message.content.strip()
            
            # Parse structured text into dictionary with validation
            analysis_dict = self._parse_structured_text(analysis_text, default_analysis)
            study_type = self._determine_study_phase(analysis_dict)
            
            # Validate required content
            self._validate_analysis(analysis_dict)
            
            return analysis_dict, study_type
            
        except Exception as e:
            logger.error(f"Error in analyze_synopsis: {str(e)}")
            raise Exception(f"Error analyzing synopsis: {str(e)}")

    def _parse_structured_text(self, text, default_values):
        '''Parse structured text into dictionary with improved error handling'''
        sections = default_values.copy()  # Start with default values
        current_section = None
        current_list = {}
        
        try:
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith('=== ') and line.endswith(' ==='):
                    if current_section:
                        section_key = current_section.lower().replace(' ', '_')
                        sections[section_key] = current_list or sections.get(section_key, {})
                    current_section = line.strip('= ')
                    current_list = {}
                    continue
                    
                if ': ' in line:
                    key, value = line.split(': ', 1)
                    key = key.lower().replace(' ', '_')
                    
                    # Handle empty or 'Not specified' values
                    if value.lower() in ['', 'not specified', 'none']:
                        value = 'Not specified'
                        
                    if current_section == 'STUDY TYPE AND DESIGN':
                        if key == 'key_features':
                            current_list[key] = []
                        else:
                            current_list[key] = value
                    elif current_section == 'CRITICAL PARAMETERS':
                        if key == 'secondary_endpoints':
                            current_list[key] = []
                        else:
                            current_list[key] = value
                            
                elif line.startswith('- '):
                    item = line[2:].strip()
                    if not item or item.lower() in ['none', 'not specified']:
                        continue
                        
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
            
            # Handle the last section
            if current_section:
                section_key = current_section.lower().replace(' ', '_')
                sections[section_key] = current_list or sections.get(section_key, {})
            
            return sections
            
        except Exception as e:
            logger.error(f"Error parsing structured text: {str(e)}")
            return default_values

    def _validate_analysis(self, analysis):
        """Validate required content in analysis"""
        required_sections = ['study_type_and_design', 'critical_parameters', 'required_sections']
        missing = [section for section in required_sections if section not in analysis]
        
        if missing:
            raise ValueError(f"Analysis missing required sections: {', '.join(missing)}")
        
        # Validate study type and design
        study_design = analysis.get('study_type_and_design', {})
        if not isinstance(study_design, dict):
            raise ValueError("study_type_and_design must be a dictionary")
            
        # Ensure missing_information is always a list
        if 'missing_information' not in analysis:
            analysis['missing_information'] = []
        
        return True

    def _determine_study_phase(self, analysis):
        """Determine study phase from analysis"""
        try:
            study_design = analysis.get("study_type_and_design", {})
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
