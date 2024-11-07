import logging
from typing import Dict, Optional
from utils.gpt_handler import GPTHandler
from config.study_type_definitions import COMPREHENSIVE_STUDY_CONFIGS
from prompts.section_templates import SECTION_TEMPLATES, CONDITIONAL_SECTIONS, DEFAULT_TEMPLATES
import streamlit as st

logger = logging.getLogger(__name__)

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
    
    def generate_study_schema(self, study_type: str) -> str:
        """Generate Mermaid diagram with enhanced styling"""
        if study_type.startswith('phase'):
            phase = study_type[-1]
            return f'''```mermaid
    graph TD
        A[Screening] --> B[Randomization]
        B --> C[Treatment Phase]
        C --> D[Follow-up]
        
        style A fill:#f9f,stroke:#333,stroke-width:4px
        style B fill:#bbf,stroke:#333,stroke-width:4px
        style C fill:#dfd,stroke:#333,stroke-width:4px
        style D fill:#fdd,stroke:#333,stroke-width:4px
        
        subgraph "Phase {phase} Study Flow"
        A
        B
        C
        D
        end
    ```'''
        elif study_type == 'observational':
            return '''```mermaid
    graph TD
        A[Enrollment] --> B[Data Collection]
        B --> C[Follow-up]
        C --> D[Analysis]
        
        style A fill:#f9f,stroke:#333,stroke-width:4px
        style B fill:#bbf,stroke:#333,stroke-width:4px
        style C fill:#dfd,stroke:#333,stroke-width:4px
        style D fill:#fdd,stroke:#333,stroke-width:4px
        
        subgraph "Observational Study Flow"
        A
        B
        C
        D
        end
    ```'''
        return None

    def get_section_template(self, section_name: str, study_type: str) -> str:
        """Get the appropriate template for the section based on study type"""
        # Add study type-specific template overrides
        study_specific_templates = {
            'secondary_rwe': {
                'statistical_analysis': '''
Generate Statistical Analysis Plan for Secondary RWE study including:

1. Analysis Populations:
   • Define target population
   • Specify inclusion/exclusion criteria
   • Detail subgroup definitions

2. Statistical Methods:
   • Specify primary analysis methods
   • Define significance levels
   • List covariates and adjustments
   • Detail sensitivity analyses

3. Missing Data Handling:
   • Define handling of missing values
   • Specify imputation methods
   • Detail documentation requirements

4. Quality Control:
   • Define data quality checks
   • Specify validation procedures
   • Detail documentation requirements

Cross-reference with:
- Data Source section for data elements
- Variables section for definitions
- Limitations section for potential biases
''',
                'safety': '''
Define Safety Analysis for Secondary RWE including:

1. Safety Outcome Identification:
   • Define safety endpoints
   • Specify coding dictionaries
   • Detail outcome validation

2. Analysis Methods:
   • Specify statistical approaches
   • Define reporting periods
   • Detail stratification factors

3. Risk Assessment:
   • Define risk evaluation methods
   • Specify signal detection
   • Detail documentation requirements

Cross-reference with:
- Data Source for safety data elements
- Variables for outcome definitions
- Limitations for potential biases
'''
            }
        }
        
        # Check for study-specific template first
        if study_type in study_specific_templates:
            if section_name in study_specific_templates[study_type]:
                return study_specific_templates[study_type][section_name]
                
        # Check study type templates
        if study_type in SECTION_TEMPLATES:
            study_templates = SECTION_TEMPLATES[study_type]
            if section_name in study_templates:
                return study_templates[section_name]
        
        # Fall back to default template
        return DEFAULT_TEMPLATES.get(section_name, f"Generate content for {section_name} section")

    def generate_section(self, section_name: str, synopsis_content: str, study_type: str) -> str:
        try:
            # Get previously generated sections for context
            previous_sections = {}
            if hasattr(st.session_state, 'generated_sections'):
                previous_sections = {
                    name: content for name, content in st.session_state.generated_sections.items()
                    if name != section_name
                }
            
            # Add context to system message
            system_message = '''You are a protocol development assistant specializing in clinical study protocols.
            
Previous sections have been generated. Ensure your content:
1. Does not duplicate information already present
2. Maintains consistency with previous sections
3. References relevant details from other sections appropriately
4. Adds new, section-specific information
5. Uses cross-references where appropriate

Format using:
- *asterisks* for italic text
- [PLACEHOLDER: *description*] for missing information
- [RECOMMENDED: *suggestion*] for recommendations
- HTML tables with appropriate classes'''

            # Get template
            template = self.get_section_template(section_name, study_type)
            
            # Add study schema for study_design section
            if section_name == 'study_design':
                schema = self.generate_study_schema(study_type)
                if schema:
                    template += "\n\nInclude the following study schema diagram:\n" + schema

            # Add previous sections to prompt
            context = "Previously generated sections:\n\n"
            for prev_name, prev_content in previous_sections.items():
                context += f"{prev_name.replace('_', ' ').title()}:\n{prev_content}\n\n"
            
            prompt = f"{context}Based on this study synopsis:\n{synopsis_content}\n\n{template}"
            
            return self.gpt_handler.generate_content(prompt=prompt, system_message=system_message)
            
        except Exception as e:
            logger.error(f"Error generating {section_name}: {str(e)}")
            raise

    def should_include_section(self, section_name: str, study_type: str) -> bool:
        '''Determine if a section should be included based on study type rules'''
        critical_sections = {
            'synopsis',
            'ethical_considerations',
            'data_monitoring',
            'completion_criteria'
        }
        
        if section_name in critical_sections:
            return True
            
        if study_type in CONDITIONAL_SECTIONS:
            study_rules = CONDITIONAL_SECTIONS[study_type]
            if section_name in study_rules['required'] or section_name in study_rules['optional']:
                return True
            if section_name in study_rules['excluded']:
                return False
            
        return True
