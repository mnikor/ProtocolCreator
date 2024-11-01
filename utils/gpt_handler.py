import os
import logging
import re
from openai import OpenAI
from typing import Dict, List

logger = logging.getLogger(__name__)

class GPTHandler:
    def __init__(self):
        try:
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            if not os.environ.get("OPENAI_API_KEY"):
                logger.error("OpenAI API key not found in environment variables")
                raise ValueError("OpenAI API key not found")
            self.model = "gpt-4o-2024-08-06"  # Update to new model
            self.max_input_tokens = 128000     # New input limit
            self.max_output_tokens = 16000     # New output limit
            self.default_analysis = {
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
                    'primary_endpoint': 'Not specified'
                },
                'missing_information': []
            }
        except Exception as e:
            logger.error(f"Error initializing GPTHandler: {str(e)}")
            raise

    def _clean_generated_content(self, content):
        """Clean and format generated content"""
        if not content:
            return content
            
        # Remove markdown headers
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        
        # Remove markdown list markers but keep the content
        content = re.sub(r'^\s*[-*]\s+', '• ', content, flags=re.MULTILINE)
        
        # Remove other markdown formatting
        content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)  # Bold
        content = re.sub(r'\*(.+?)\*', r'\1', content)      # Italic
        content = re.sub(r'_(.+?)_', r'\1', content)        # Underscore
        content = re.sub(r'`(.+?)`', r'\1', content)        # Code
        
        # Clean up multiple newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()

    def generate_section(self, section_name: str, synopsis_content: str, previous_sections=None, prompt=None):
        """Generate protocol section with specified prompt"""
        try:
            if not section_name or not synopsis_content:
                raise ValueError("Section name and synopsis content are required")

            # Use provided prompt if available, otherwise use default system prompt
            messages = [
                {
                    "role": "system",
                    "content": prompt or "You are a medical writer generating protocol sections. Start directly with the content. Do not include any introductory phrases or meta-commentary. Use proper heading structure."
                },
                {
                    "role": "user",
                    "content": f"Generate the {section_name} section based on this synopsis:\n\n{synopsis_content}\n\nPrevious sections if available:\n{previous_sections or ''}"
                }
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=self.max_output_tokens
            )

            content = response.choices[0].message.content
            return self._clean_generated_content(content)

        except Exception as e:
            logger.error(f"Error generating section: {str(e)}")
            raise

    def analyze_synopsis(self, synopsis_text: str):
        """Analyze synopsis content and determine study type"""
        try:
            if not synopsis_text or not isinstance(synopsis_text, str):
                raise ValueError("Invalid synopsis text")
                
            messages = [
                {
                    "role": "system",
                    "content": '''You are a protocol analysis assistant. Analyze the synopsis and classify the study type considering:
                    - Systematic Literature Reviews (SLR)
                    - Meta-analyses
                    - Real World Evidence studies
                    - Clinical trials and their phases
                    - Consensus methods
                    - Observational studies
                    
                    Return study classification in primary_classification field.'''
                },
                {
                    "role": "user", 
                    "content": f"Analyze this synopsis:\n\n{synopsis_text}"
                }
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=self.max_output_tokens
            )
            
            analysis_text = response.choices[0].message.content
            analysis_dict = self._parse_structured_text(analysis_text, self.default_analysis)
            study_phase = self._determine_study_phase(analysis_dict)
            
            return analysis_dict, study_phase
            
        except Exception as e:
            logger.error(f"Error in analyze_synopsis: {str(e)}")
            return self.default_analysis, 'phase1'

    def _parse_structured_text(self, text: str, default_values: Dict) -> Dict:
        """Parse and structure the analysis text"""
        try:
            if not isinstance(text, str) or not text.strip():
                logger.error("Invalid or empty text response")
                return default_values

            # Initialize with default structure
            analysis = {
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
                    'primary_endpoint': 'Not specified'
                },
                'missing_information': []
            }
            
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if 'classification' in line.lower():
                    analysis['study_type_and_design']['primary_classification'] = line.split(':')[-1].strip()
                elif 'study type' in line.lower() or 'design' in line.lower():
                    analysis['study_type_and_design']['design_type'] = line.split(':')[-1].strip()
                elif 'phase' in line.lower():
                    analysis['study_type_and_design']['phase'] = line.split(':')[-1].strip()
                elif 'population' in line.lower():
                    analysis['critical_parameters']['population'] = line.split(':')[-1].strip()
                elif 'endpoint' in line.lower():
                    analysis['critical_parameters']['primary_endpoint'] = line.split(':')[-1].strip()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error parsing text: {str(e)}")
            return default_values

    def _determine_study_phase(self, analysis: Dict) -> str:
        """Determine study phase from analysis"""
        try:
            study_design = analysis.get("study_type_and_design", {})
            classification = study_design.get("primary_classification", "").lower()
            phase = study_design.get("phase", "").lower()
            
            # Check for special study types first
            if any(term in classification for term in ['systematic review', 'literature review', 'slr']):
                return "slr"
            elif 'meta-analysis' in classification:
                return "meta"
            elif 'real world' in classification:
                return "rwe"
            elif 'consensus' in classification:
                return "consensus"
            elif 'observational' in classification:
                return "observational"
            
            # Extract phase number from text
            phase_match = re.search(r'phase\s*([1234]|i{1,3}|iv)', phase, re.IGNORECASE)
            if phase_match:
                phase_text = phase_match.group(1)
                if phase_text.isdigit():
                    return f"phase{phase_text}"
                elif phase_text.lower() == 'i':
                    return "phase1"
                elif phase_text.lower() == 'ii':
                    return "phase2"
                elif phase_text.lower() == 'iii':
                    return "phase3"
                elif phase_text.lower() == 'iv':
                    return "phase4"
            
            # Default based on study type
            if 'interventional' in classification.lower():
                return "phase2"  # Most common default
                
            return "phase1"  # Final fallback
            
        except Exception as e:
            logger.error(f"Error determining study phase: {str(e)}")
            return "phase1"
