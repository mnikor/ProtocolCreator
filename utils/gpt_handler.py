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
            },
            'statistical_considerations': {
                'required': True,
                'description': 'Sample size, analysis methods, and statistical plan',
                'example_content': [
                    'Sample size calculation',
                    'Primary analysis method',
                    'Secondary analyses',
                    'Interim analyses'
                ],
                'guidelines': ['ICH E9']
            },
            'population': {
                'required': True,
                'description': 'Inclusion/exclusion criteria and population characteristics',
                'example_content': [
                    'Key inclusion criteria',
                    'Key exclusion criteria',
                    'Population stratification',
                    'Withdrawal criteria'
                ],
                'guidelines': ['ICH E6(R2)']
            }
        }

    def _parse_structured_text(self, text, default_values):
        '''Parse structured text into dictionary'''
        try:
            # Initialize with default values
            analysis_dict = default_values.copy()
            
            # Split text into sections
            sections = text.split('===')
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                    
                # Get section name from first line
                lines = section.split('\n')
                section_name = lines[0].strip().lower()
                section_name = section_name.replace(' ', '_')
                
                # Process section content
                content = {}
                current_list = []
                current_key = None
                
                for line in lines[1:]:
                    line = line.strip()
                    if not line:
                        continue
                        
                    if line.startswith('•') or line.startswith('-'):
                        item = line[1:].strip()
                        if current_key:
                            if not isinstance(content.get(current_key), list):
                                content[current_key] = []
                            content[current_key].append(item)
                        else:
                            current_list.append(item)
                    elif ':' in line:
                        current_key, value = line.split(':', 1)
                        current_key = current_key.strip().lower().replace(' ', '_')
                        value = value.strip()
                        if value:
                            content[current_key] = value
                            
                # Store section content
                if section_name == 'study_type_and_design':
                    analysis_dict['study_type_and_design'] = content
                elif section_name == 'critical_parameters':
                    analysis_dict['critical_parameters'] = content
                elif section_name == 'required_sections':
                    analysis_dict['required_sections'] = current_list
                elif section_name == 'missing_information':
                    analysis_dict['missing_information'] = current_list
                    
            return analysis_dict
            
        except Exception as e:
            logger.error(f"Error parsing structured text: {str(e)}")
            logger.error(f"Problematic text: {text}")
            return default_values

    def analyze_synopsis(self, synopsis_text):
        """Analyze synopsis with improved handling of missing and empty sections"""
        try:
            # Default values with enhanced validation
            default_analysis = {
                'study_type_and_design': {
                    'primary_classification': 'Not specified',
                    'design_type': 'Not specified',
                    'phase': 'Not specified',
                    'key_features': ['None specified']
                },
                'critical_parameters': {
                    'population': 'Not specified',
                    'intervention': 'Not specified',
                    'control_comparator': 'Not specified',
                    'primary_endpoint': 'Not specified',
                    'secondary_endpoints': ['None specified']
                },
                'required_sections': [],
                'missing_sections': [],
                'missing_information': [],
                'validation_feedback': []
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
            
            analysis_text = response.choices[0].message.content.strip()
            analysis_dict = self._parse_structured_text(analysis_text, default_analysis)
            
            # Validate based on study phase
            study_phase = self._determine_study_phase(analysis_dict)
            self._validate_phase_specific_requirements(analysis_dict, study_phase)
            
            # Validate mandatory sections
            self._validate_mandatory_sections(analysis_dict, synopsis_text)
            
            # Provide detailed feedback
            self._generate_detailed_feedback(analysis_dict)
            
            return analysis_dict, study_phase
            
        except Exception as e:
            logger.error(f"Error in analyze_synopsis: {str(e)}")
            raise Exception(f"Error analyzing synopsis: {str(e)}")

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

    def _validate_phase_specific_requirements(self, analysis, phase):
        """Validate phase-specific requirements"""
        try:
            template = self.template_manager.get_template(phase)
            missing_requirements = []
            
            for section, requirements in template['sections'].items():
                section_content = analysis.get(section, {})
                if not section_content:
                    missing_requirements.append({
                        'section': section,
                        'message': f"Missing required section for {phase}"
                    })
            
            if missing_requirements:
                analysis.setdefault('validation_feedback', []).extend(missing_requirements)
                
        except Exception as e:
            logger.error(f"Error in phase validation: {str(e)}")

    def _validate_mandatory_sections(self, analysis, synopsis_text):
        """Validate presence of mandatory sections"""
        try:
            missing_sections = []
            
            for section, details in self.mandatory_sections.items():
                if details['required']:
                    if not any(section.lower() in text.lower() for text in [synopsis_text]):
                        missing_sections.append({
                            'section': section,
                            'description': details['description'],
                            'guidelines': details['guidelines']
                        })
            
            if missing_sections:
                analysis['missing_sections'] = missing_sections
                
        except Exception as e:
            logger.error(f"Error in mandatory section validation: {str(e)}")

    def _generate_detailed_feedback(self, analysis):
        """Generate detailed feedback for missing or incomplete sections"""
        try:
            feedback = []
            
            for section, details in self.mandatory_sections.items():
                if section in analysis.get('missing_sections', []):
                    feedback.append({
                        'section': section,
                        'message': f"Missing required section: {section}",
                        'description': details['description'],
                        'guidelines': details['guidelines']
                    })
            
            analysis['detailed_feedback'] = feedback
            
        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}")

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
