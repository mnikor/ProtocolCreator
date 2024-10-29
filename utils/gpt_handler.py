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

        # Phase 3 specific requirements
        self.phase3_requirements = {
            'background': {
                'required_elements': [
                    'disease_state',
                    'current_treatments',
                    'treatment_guidelines',
                    'market_landscape'
                ],
                'validation_rules': {
                    'min_sections': 4,
                    'required_keywords': ['standard of care', 'guidelines', 'treatment options']
                }
            },
            'statistical_considerations': {
                'required_elements': [
                    'sample_size_calculation',
                    'power_analysis',
                    'interim_analyses',
                    'multiplicity_adjustment'
                ],
                'validation_rules': {
                    'min_sections': 3,
                    'required_keywords': ['power', 'sample size', 'analysis population']
                }
            },
            'study_design': {
                'required_elements': [
                    'control_comparator',
                    'randomization',
                    'blinding',
                    'treatment_duration'
                ],
                'validation_rules': {
                    'min_sections': 4,
                    'required_keywords': ['control', 'comparator', 'randomization']
                }
            }
        }

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

    def _validate_phase_specific_requirements(self, analysis, phase):
        """Validate phase-specific requirements"""
        if phase == 'phase3':
            requirements = self.phase3_requirements
            for section, rules in requirements.items():
                self._validate_section_requirements(analysis, section, rules)

    def _validate_section_requirements(self, analysis, section, rules):
        """Validate specific section requirements"""
        validation_feedback = analysis.setdefault('validation_feedback', [])
        
        # Check required elements
        missing_elements = []
        for element in rules['required_elements']:
            if not self._check_element_presence(analysis, section, element):
                missing_elements.append(element)
        
        if missing_elements:
            feedback = {
                'section': section,
                'missing_elements': missing_elements,
                'guidelines': self.mandatory_sections[section]['guidelines'],
                'examples': self.mandatory_sections[section]['example_content']
            }
            validation_feedback.append(feedback)

    def _check_element_presence(self, analysis, section, element):
        """Check if an element is present in the analysis"""
        if section in analysis:
            section_content = str(analysis[section]).lower()
            return element.replace('_', ' ') in section_content
        return False

    def _generate_detailed_feedback(self, analysis):
        """Generate detailed feedback for missing or incomplete sections"""
        feedback = []
        
        for section, details in self.mandatory_sections.items():
            if section in analysis.get('missing_sections', []):
                feedback.append({
                    'section': section,
                    'message': f"Missing required section: {section}",
                    'description': details['description'],
                    'examples': details['example_content'],
                    'guidelines': details['guidelines'],
                    'impact': "This section is critical for protocol completeness and regulatory compliance"
                })
        
        analysis['detailed_feedback'] = feedback

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
                    
                    # Handle empty or 'Not specified' values with placeholders
                    if not value or value.lower() in ['', 'not specified', 'none']:
                        value = 'Not specified'
                        if key in ['key_features', 'secondary_endpoints']:
                            value = ['None specified']
                    
                    # Enhanced validation for critical fields
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
                        sections.setdefault('required_sections', []).append(item)
                    elif current_section == 'MISSING INFORMATION':
                        sections.setdefault('missing_information', []).append(item)
                    elif current_section == 'STUDY TYPE AND DESIGN' and 'key_features' in current_list:
                        current_list.setdefault('key_features', []).append(item)
                    elif current_section == 'CRITICAL PARAMETERS' and 'secondary_endpoints' in current_list:
                        current_list.setdefault('secondary_endpoints', []).append(item)
            
            # Handle the last section
            if current_section:
                section_key = current_section.lower().replace(' ', '_')
                sections[section_key] = current_list or sections.get(section_key, {})
            
            return sections
            
        except Exception as e:
            logger.error(f"Error parsing structured text: {str(e)}")
            return default_values

    def _validate_mandatory_sections(self, analysis, synopsis_text):
        """Validate presence of mandatory sections with enhanced feedback"""
        missing_sections = []
        
        for section, details in self.mandatory_sections.items():
            if details['required']:
                if not any(section.lower() in text.lower() for text in [synopsis_text]):
                    missing_sections.append({
                        'section': section,
                        'description': details['description'],
                        'examples': details['example_content'],
                        'guidelines': details['guidelines']
                    })
        
        if missing_sections:
            analysis['missing_sections'] = missing_sections
            for missing in missing_sections:
                analysis['missing_information'].append(
                    f"Missing required section: {missing['section']}\n"
                    f"Description: {missing['description']}\n"
                    f"Expected content examples:\n"
                    f"{chr(10).join(['- ' + ex for ex in missing['examples']])}\n"
                    f"Relevant guidelines: {', '.join(missing['guidelines'])}"
                )

    def _determine_study_phase(self, analysis):
        """Determine study phase from analysis with enhanced validation"""
        try:
            study_design = analysis.get("study_type_and_design", {})
            phase = study_design.get("phase", "").lower()
            logger.info(f"Detected study phase: {phase}")
            
            # Map phase string to template type with validation
            if "1" in phase or "i" in phase:
                return "phase1"
            elif "2" in phase or "ii" in phase:
                return "phase2"
            elif "3" in phase or "iii" in phase:
                return "phase3"
            else:
                logger.warning("Study phase unclear, defaulting to phase1")
                analysis['validation_feedback'].append({
                    'warning': 'Study phase not clearly specified',
                    'impact': 'Using Phase 1 template as default',
                    'recommendation': 'Please specify study phase explicitly in synopsis'
                })
                return "phase1"

        except Exception as e:
            logger.error(f"Error determining study phase: {str(e)}")
            raise Exception(f"Error determining study phase: {str(e)}")

    def generate_section(self, section_name, synopsis_content, previous_sections=None, study_type=None):
        """Generate protocol section with enhanced template handling"""
        if not section_name or not synopsis_content:
            raise ValueError("Section name and synopsis content are required")

        try:
            section_prompt = SECTION_PROMPTS.get(section_name)
            if not section_prompt:
                raise ValueError(f"No prompt template found for section: {section_name}")

            # Get template-specific guidance with enhanced validation
            template_guidance = ""
            if study_type:
                try:
                    template = self.template_manager.get_section_template(study_type, section_name)
                    
                    # Add validation requirements
                    if study_type == 'phase3':
                        if section_name in self.phase3_requirements:
                            template['validation'] = self.phase3_requirements[section_name]
                    
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
                    "content": "You are a medical writer generating protocol sections. Provide detailed, scientifically accurate content following ICH guidelines."
                }, {
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating section: {str(e)}")
            raise Exception(f"Error generating section: {str(e)}")
