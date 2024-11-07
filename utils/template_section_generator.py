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
        # Add study-specific statistical templates
        study_specific_templates = {
            'clinical_trial': {
                'statistical_analysis': '''
Think through:
1. Power calculations and sample size
   - What is the primary endpoint?
   - What effect size is clinically meaningful?
   - What variability is expected?
   - What dropout rate is anticipated?

2. Interim analyses requirements
   - When should interim analyses occur?
   - What are the stopping rules?
   - How to control overall alpha?
   - What safety monitoring is needed?

3. Missing data handling approach
   - What patterns of missing data are expected?
   - Which imputation methods are appropriate?
   - What sensitivity analyses are needed?
   - How to document missing data?

4. Subgroup analyses plan
   - Which subgroups are clinically relevant?
   - How to control for multiplicity?
   - What sample sizes are needed?
   - How to interpret results?

Then generate Statistical Analysis Plan including:
1. Analysis Populations
2. Primary Analysis Methods
3. Secondary Analyses
4. Safety Analyses
5. Interim Analyses
6. Missing Data Approach
7. Sensitivity Analyses
8. Subgroup Analyses
''',
                'study_design': '''
Think through design elements:
1. Study Framework
   - What phase-specific requirements apply?
   - How to ensure proper randomization?
   - What blinding approach is needed?
   - How to maintain study integrity?

2. Quality Control Measures
   - What monitoring is required?
   - How to ensure data quality?
   - What documentation is needed?
   - How to track protocol compliance?

3. Safety Considerations
   - What safety monitoring is needed?
   - How often to review safety data?
   - What are stopping criteria?
   - How to handle adverse events?

Then generate detailed design specifications.
'''
            },
            'secondary_rwe': {
                'statistical_analysis': '''
Think through:
1. Confounding control methods
   - What confounders are expected?
   - Which methods best control bias?
   - How to assess residual confounding?
   - What sensitivity analyses needed?

2. Propensity scoring approach
   - Which variables to include?
   - What matching method to use?
   - How to assess balance?
   - What diagnostics needed?

3. Sensitivity analyses plan
   - Which assumptions to test?
   - What alternative methods to use?
   - How to present results?
   - What thresholds for robustness?

4. Time-varying effects
   - How to handle time-dependent confounding?
   - What methods for time-varying exposure?
   - How to assess temporal relationships?
   - What follow-up required?

Then generate Statistical Analysis Plan including:
1. Data Quality Assessment
2. Variable Definitions
3. Primary Analysis Methods
4. Bias Control Approach
5. Sensitivity Analyses
6. Missing Data Handling
7. Subgroup Analyses
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
            
            # Enhanced system message with study type-specific thinking
            system_message = '''You are a protocol development assistant specializing in clinical study protocols.

Think through study type requirements:
1. For Clinical Trials:
   - Phase-specific requirements
   - Regulatory guidance
   - Quality standards
   - Safety monitoring needs

2. For RWE Studies:
   - Data source quality
   - Variable definitions
   - Bias control
   - Generalizability

3. For Systematic Reviews:
   - Search methodology
   - Quality assessment
   - Evidence synthesis
   - Bias evaluation

4. For Patient Registries:
   - Data collection standards
   - Quality control measures
   - Long-term follow-up
   - Real-world evidence generation

Then for each section:
1. Consider study-type specific requirements
2. Apply appropriate validity measures
3. Include quality control elements
4. Ensure regulatory compliance

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

            # Add previous sections to prompt with improved context
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
