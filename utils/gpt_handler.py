from openai import OpenAI
import os
import json
import logging
from utils.template_manager import TemplateManager
from prompts.section_prompts import SECTION_PROMPTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTHandler:
    def __init__(self):
        try:
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            if not os.environ.get("OPENAI_API_KEY"):
                logger.error("OpenAI API key not found in environment variables")
                raise ValueError("OpenAI API key not found")
            self.model_name = "gpt-4o-2024-08-06"  # Updated model name
            self.template_manager = TemplateManager()
        except Exception as e:
            logger.error(f"Error initializing GPTHandler: {str(e)}")
            raise

    def analyze_synopsis(self, synopsis_text):
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

        try:
            messages = [
                {
                    "role": "system",
                    "content": '''You are a protocol analysis assistant. Analyze the synopsis and classify the study type considering:
- Clinical trial phases (1-4)
- Real World Evidence studies
- Systematic Literature Reviews
- Meta-analyses
- Consensus methods
- Observational studies

Return the information in this exact format:

STUDY TYPE AND DESIGN
Primary Classification: [Trial type e.g., Interventional, Observational, Meta-analysis]
Design Type: [e.g., Randomized, Double-blind, Systematic Review]
Phase: [Study phase or N/A for non-clinical trials]
Key Features:
- [List key design features]

CRITICAL PARAMETERS
Population: [Target population description]
Intervention: [Study intervention details]
Control/Comparator: [Control group details if applicable]
Primary Endpoint: [Primary endpoint]
Secondary Endpoints:
- [List secondary endpoints]

REQUIRED SECTIONS
- [List required protocol sections identified]

MISSING INFORMATION
- [List any critical missing information]

Return ONLY the structured information above, no additional text.'''
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
            logger.info(f"GPT Analysis Response:\n{analysis_text}")

            # Parse the structured text format
            analysis_dict = self._parse_structured_text(analysis_text, default_analysis)
            
            if not isinstance(analysis_dict, dict):
                logger.error("Analysis result is not a dictionary")
                analysis_dict = default_analysis

            # Determine study type
            study_type = self._determine_study_type(analysis_dict)

            return analysis_dict, study_type

        except Exception as e:
            logger.error(f"Error in analyze_synopsis: {str(e)}")
            return default_analysis, 'phase1'

    def _determine_study_type(self, analysis):
        """Determine study type from analysis"""
        try:
            study_design = analysis.get("study_type_and_design", {})
            phase = study_design.get("phase", "").lower()
            design_type = study_design.get("design_type", "").lower()
            classification = study_design.get("primary_classification", "").lower()
            
            # Check for special study types first
            if any(term in classification.lower() for term in ['systematic review', 'literature review']):
                return 'slr'
            elif 'meta-analysis' in classification.lower():
                return 'meta'
            elif 'consensus' in classification.lower():
                return 'consensus'
            elif 'real world' in classification.lower() or 'observational' in classification.lower():
                return 'rwe'
            elif 'phase 4' in phase or 'phase iv' in phase:
                return 'phase4'
            elif 'phase 3' in phase or 'phase iii' in phase:
                return 'phase3'
            elif 'phase 2' in phase or 'phase ii' in phase:
                return 'phase2'
            elif 'phase 1' in phase or 'phase i' in phase:
                return 'phase1'
            else:
                return 'observational'  # Default to observational if no specific type detected

        except Exception as e:
            logger.error(f"Error determining study type: {str(e)}")
            return "phase1"

    def _parse_structured_text(self, text, default_values):
        """Parse the structured text response"""
        try:
            if not isinstance(text, str):
                logger.error("Input text is not a string")
                return default_values

            result = default_values.copy()
            sections = text.split('\n\n')
            current_section = None

            for section in sections:
                section = section.strip()
                if not section:
                    continue

                if section.startswith('STUDY TYPE AND DESIGN'):
                    current_section = 'study_type_and_design'
                    lines = section.split('\n')[1:]
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().lower().replace(' ', '_')
                            value = value.strip()
                            if key == 'key_features':
                                features = [f.strip('- ').strip() for f in lines[lines.index(line)+1:] 
                                          if f.strip().startswith('-')]
                                result['study_type_and_design']['key_features'] = features
                            else:
                                result['study_type_and_design'][key] = value

                elif section.startswith('CRITICAL PARAMETERS'):
                    current_section = 'critical_parameters'
                    lines = section.split('\n')[1:]
                    for line in lines:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().lower().replace('/', '_').replace(' ', '_')
                            value = value.strip()
                            if key == 'secondary_endpoints':
                                endpoints = [e.strip('- ').strip() for e in lines[lines.index(line)+1:] 
                                          if e.strip().startswith('-')]
                                result['critical_parameters']['secondary_endpoints'] = endpoints
                            else:
                                result['critical_parameters'][key] = value

                elif section.startswith('REQUIRED SECTIONS'):
                    required_sections = [line.strip('- ').strip() 
                                      for line in section.split('\n')[1:]
                                      if line.strip().startswith('-')]
                    result['required_sections'] = required_sections

                elif section.startswith('MISSING INFORMATION'):
                    missing_info = [line.strip('- ').strip() 
                                  for line in section.split('\n')[1:]
                                  if line.strip().startswith('-')]
                    result['missing_information'] = missing_info

            return result

        except Exception as e:
            logger.error(f"Error parsing text: {str(e)}")
            return default_values

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
