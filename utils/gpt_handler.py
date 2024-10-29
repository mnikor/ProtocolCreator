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
        
        # Define mandatory protocol sections
        self.mandatory_sections = {
            'background': {
                'required': True,
                'description': 'Disease background, current treatments, and study rationale'
            },
            'objectives': {
                'required': True,
                'description': 'Primary and secondary objectives with endpoints'
            },
            'study_design': {
                'required': True,
                'description': 'Overall design, methodology, and procedures'
            },
            'statistical_considerations': {
                'required': True,
                'description': 'Sample size, analysis methods, and statistical plan'
            },
            'population': {
                'required': True,
                'description': 'Inclusion/exclusion criteria and population characteristics'
            }
        }

    def analyze_synopsis(self, synopsis_text):
        """Analyze synopsis with improved handling of missing and empty sections"""
        try:
            # Default values for all possible sections with explicit handling
            default_analysis = {
                'study_type_and_design': {
                    'primary_classification': 'Not specified',
                    'design_type': 'Not specified',
                    'phase': 'Not specified',
                    'key_features': ['None specified']  # Always include at least one item
                },
                'critical_parameters': {
                    'population': 'Not specified',
                    'intervention': 'Not specified',
                    'control_comparator': 'Not specified',
                    'primary_endpoint': 'Not specified',
                    'secondary_endpoints': ['None specified']  # Always include at least one item
                },
                'required_sections': [],
                'missing_sections': [],
                'missing_information': []
            }

            messages = [
                {
                    "role": "system",
                    "content": SYNOPSIS_ANALYSIS_PROMPT
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
            
            # Validate mandatory sections and content
            self._validate_mandatory_sections(analysis_dict, synopsis_text)
            
            # Determine study type
            study_type = self._determine_study_phase(analysis_dict)
            
            # Validate required content
            self._validate_analysis(analysis_dict)
            
            return analysis_dict, study_type
            
        except Exception as e:
            logger.error(f"Error in analyze_synopsis: {str(e)}")
            raise Exception(f"Error analyzing synopsis: {str(e)}")

    def _parse_structured_text(self, text, default_values):
        '''Parse structured text into dictionary with improved error handling'''
        sections = default_values.copy()
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
                    if not value or value.lower() in ['', 'not specified', 'none']:
                        value = 'Not specified'
                        if key in ['key_features', 'secondary_endpoints']:
                            value = ['None specified']
                    
                    if current_section == 'STUDY TYPE AND DESIGN':
                        if key == 'key_features':
                            current_list[key] = value if isinstance(value, list) else []
                        else:
                            current_list[key] = value
                    elif current_section == 'CRITICAL PARAMETERS':
                        if key == 'secondary_endpoints':
                            current_list[key] = value if isinstance(value, list) else []
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
                        if not current_list['key_features'] or current_list['key_features'] == ['None specified']:
                            current_list['key_features'] = []
                        current_list['key_features'].append(item)
                    elif current_section == 'CRITICAL PARAMETERS' and 'secondary_endpoints' in current_list:
                        if not current_list['secondary_endpoints'] or current_list['secondary_endpoints'] == ['None specified']:
                            current_list['secondary_endpoints'] = []
                        current_list['secondary_endpoints'].append(item)
            
            # Handle the last section
            if current_section:
                section_key = current_section.lower().replace(' ', '_')
                sections[section_key] = current_list or sections.get(section_key, {})
            
            # Ensure lists are never empty
            if 'study_type_and_design' in sections:
                if not sections['study_type_and_design'].get('key_features'):
                    sections['study_type_and_design']['key_features'] = ['None specified']
                    
            if 'critical_parameters' in sections:
                if not sections['critical_parameters'].get('secondary_endpoints'):
                    sections['critical_parameters']['secondary_endpoints'] = ['None specified']
            
            return sections
            
        except Exception as e:
            logger.error(f"Error parsing structured text: {str(e)}")
            return default_values

    def _validate_mandatory_sections(self, analysis, synopsis_text):
        """Validate presence of mandatory sections in synopsis"""
        missing_sections = []
        
        for section, details in self.mandatory_sections.items():
            if details['required']:
                # Check for section presence using case-insensitive search
                if not any(section.lower() in text.lower() for text in [synopsis_text]):
                    missing_sections.append({
                        'section': section,
                        'description': details['description']
                    })
        
        if missing_sections:
            analysis['missing_sections'] = missing_sections
            # Add detailed feedback for missing sections
            for missing in missing_sections:
                analysis['missing_information'].append(
                    f"Missing required section: {missing['section']} - {missing['description']}"
                )

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
        
        # Validate critical parameters
        critical_params = analysis.get('critical_parameters', {})
        if not critical_params.get('control_comparator'):
            analysis['missing_information'].append(
                "Control/Comparator information is required but not specified"
            )
        
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
