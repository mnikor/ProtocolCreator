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
        
        # Define mandatory protocol sections with enhanced validation rules
        self.mandatory_sections = {
            'background': {
                'required': True,
                'description': 'Disease background, current treatments, and study rationale',
                'example_content': [
                    'Disease epidemiology and burden',
                    'Current treatment options',
                    'Unmet medical needs',
                    'Therapeutic rationale'
                ],
                'guidelines': ['ICH E6(R2)', 'ICH E8']
            },
            'objectives': {
                'required': True,
                'description': 'Primary and secondary objectives with endpoints',
                'example_content': [
                    'Clear primary objective',
                    'Measurable endpoints',
                    'Secondary objectives hierarchy',
                    'Timeline specifications'
                ],
                'guidelines': ['ICH E9']
            },
            'study_design': {
                'required': True,
                'description': 'Overall design, methodology, and procedures',
                'example_content': [
                    'Study design type',
                    'Treatment arms',
                    'Randomization details',
                    'Blinding procedures'
                ],
                'guidelines': ['ICH E6(R2)', 'ICH E9']
            }
        }

    def analyze_synopsis(self, synopsis_text):
        try:
            # Initialize default structure
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

            # Prepare system message with strict formatting requirements
            messages = [
                {
                    "role": "system",
                    "content": "You are a protocol analysis assistant. Return analysis in a structured format. Do not include any explanatory text."
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
            
            # Get response text and parse
            analysis_text = response.choices[0].message.content.strip()
            
            # Parse the structured text format
            analysis_dict = self._parse_structured_text(analysis_text, default_analysis)
            
            # Determine study phase
            study_phase = self._determine_study_phase(analysis_dict)
            
            return analysis_dict, study_phase
            
        except Exception as e:
            logger.error(f"Error in analyze_synopsis: {str(e)}")
            # Return default structure on error
            return default_analysis, 'phase1'

    def _parse_structured_text(self, text, default_values):
        try:
            # Start with default values
            result = default_values.copy()
            
            # Split into sections
            current_section = None
            current_dict = {}
            
            for line in text.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Check for section headers
                if line.startswith('=== ') and line.endswith(' ==='):
                    if current_section and current_dict:
                        if current_section == 'STUDY TYPE AND DESIGN':
                            result['study_type_and_design'] = current_dict
                        elif current_section == 'CRITICAL PARAMETERS':
                            result['critical_parameters'] = current_dict
                    
                    current_section = line.strip('= ')
                    current_dict = {}
                    continue
                
                # Handle list items
                if line.startswith('•') or line.startswith('-'):
                    item = line[1:].strip()
                    if current_section == 'REQUIRED SECTIONS':
                        if 'required_sections' not in result:
                            result['required_sections'] = []
                        result['required_sections'].append(item)
                    elif current_section == 'MISSING INFORMATION':
                        if 'missing_information' not in result:
                            result['missing_information'] = []
                        result['missing_information'].append(item)
                    continue
                
                # Handle key-value pairs
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    if value:
                        current_dict[key] = value
            
            # Add last section
            if current_section and current_dict:
                if current_section == 'STUDY TYPE AND DESIGN':
                    result['study_type_and_design'] = current_dict
                elif current_section == 'CRITICAL PARAMETERS':
                    result['critical_parameters'] = current_dict
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing text: {str(e)}")
            return default_values

    def _determine_study_phase(self, analysis):
        """Determine study phase from analysis"""
        try:
            study_design = analysis.get("study_type_and_design", {})
            phase = study_design.get("phase", "").lower()
            logger.info(f"Detected study phase: {phase}")
            
            if "1" in phase or "i" in phase:
                return "phase1"
            elif "2" in phase or "ii" in phase:
                return "phase2"
            elif "3" in phase or "iii" in phase:
                return "phase3"
            else:
                logger.warning("Study phase unclear, defaulting to phase1")
                return "phase1"
                
        except Exception as e:
            logger.error(f"Error determining study phase: {str(e)}")
            return "phase1"

    def generate_section(self, section_name, synopsis_content, previous_sections=None):
        """Generate protocol section"""
        try:
            if not section_name or not synopsis_content:
                raise ValueError("Section name and synopsis content are required")

            prompt = SECTION_PROMPTS.get(section_name, "").format(
                synopsis_content=synopsis_content,
                previous_sections=previous_sections or ""
            )

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical writer generating protocol sections."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating section: {str(e)}")
            raise Exception(f"Error generating section: {str(e)}")
