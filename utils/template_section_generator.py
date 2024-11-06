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

    def generate_study_schedule_table(self, study_type: str, synopsis_content: str) -> str:
        """Generate HTML table for study schedule"""
        prompt = f'''Based on this synopsis for a {study_type} study:
{synopsis_content}

Generate a detailed study schedule table with visits, timepoints, and procedures.
Format as an HTML table with columns: Visit, Timepoint, Procedures.
Include screening, treatment, and follow-up visits.'''

        table_content = self.gpt_handler.generate_content(prompt)
        
        if '|' in table_content and '<table' not in table_content:
            rows = [row.strip() for row in table_content.split('\n') if row.strip()]
            if rows:
                table_html = '<table class="study-schedule">'
                for i, row in enumerate(rows):
                    cells = [cell.strip() for cell in row.split('|')]
                    table_html += '<tr>'
                    cell_tag = 'th' if i == 0 else 'td'
                    table_html += ''.join(f'<{cell_tag}>{cell}</{cell_tag}>' for cell in cells)
                    table_html += '</tr>'
                table_html += '</table>'
                return table_html
        
        return table_content

    def get_section_template(self, section_name: str, study_type: str) -> str:
        """Get the appropriate template for the section based on study type"""
        if study_type in SECTION_TEMPLATES:
            study_templates = SECTION_TEMPLATES[study_type]
            if section_name in study_templates:
                return study_templates[section_name]
        return DEFAULT_TEMPLATES.get(section_name, f"Generate content for {section_name} section")

    def generate_section(self, section_name: str, synopsis_content: str, study_type: str) -> str:
        try:
            # Get previously generated sections for context
            previous_sections = {}
            if hasattr(st.session_state, 'generated_sections'):
                previous_sections = {
                    name: content for name, content in st.session_state.generated_sections.items()
                    if name != section_name  # Exclude current section
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

            # Add study schedule table for procedures section
            if section_name == 'procedures':
                schedule_table = self.generate_study_schedule_table(study_type, synopsis_content)
                if schedule_table:
                    template += "\n\nInclude the following study schedule:\n" + schedule_table

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

    def generate_complete_protocol(self, study_type: str, synopsis_content: str) -> Dict:
        try:
            study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
            base_sections = study_config.get('required_sections', [])
            
            conditional_config = CONDITIONAL_SECTIONS.get(study_type, {})
            required_sections = conditional_config.get('required', [])
            optional_sections = conditional_config.get('optional', [])
            excluded_sections = conditional_config.get('excluded', [])
            
            all_sections = list(set(base_sections + required_sections))
            all_sections = [s for s in all_sections if s not in excluded_sections]
            
            if not all_sections:
                logger.error(f"No sections defined for study type: {study_type}")
                raise ValueError(f"No sections defined for study type: {study_type}")
            
            generated_sections = {}
            for section_name in all_sections:
                logger.info(f"Generating section: {section_name}")
                if self.should_include_section(section_name, study_type):
                    section_content = self.generate_section(
                        section_name=section_name,
                        synopsis_content=synopsis_content,
                        study_type=study_type
                    )
                    if section_content:
                        generated_sections[section_name] = section_content
                    else:
                        logger.warning(f"No content generated for section: {section_name}")
                else:
                    logger.info(f"Section {section_name} excluded for study type {study_type}")
            
            logger.info(f"Generated {len(generated_sections)} sections out of {len(all_sections)} required")
            return {"sections": generated_sections}
            
        except Exception as e:
            logger.error(f"Error generating protocol: {str(e)}")
            raise
