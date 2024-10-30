import logging
from utils.gpt_handler import GPTHandler
from utils.template_manager import TemplateManager
from streamlit_mermaid import st_mermaid
import streamlit as st

logger = logging.getLogger(__name__)

class TemplateSectionGenerator:
    def __init__(self):
        self.gpt_handler = GPTHandler()
        self.template_manager = TemplateManager()

    def generate_section(self, section_name: str, study_type: str, synopsis_content: str, existing_sections: dict = None):
        """Generate a protocol section"""
        try:
            logger.info(f"Starting generation of {section_name} section")
            
            # Input validation
            if not section_name:
                raise ValueError("Section name is required")
            if not study_type:
                raise ValueError("Study type is required")
            if not synopsis_content:
                raise ValueError("Synopsis content is required")

            # Log the state before generation
            logger.info(f"Generating section: {section_name}")
            logger.info(f"Study type: {study_type}")
            logger.info(f"Synopsis length: {len(synopsis_content)}")
            logger.info(f"Existing sections: {list(existing_sections.keys()) if existing_sections else []}")

            # Special handling for study design section to include Mermaid diagram
            if section_name == 'study_design':
                return self._generate_study_design_section(synopsis_content, study_type, existing_sections)

            # Special handling for procedures section
            if section_name == 'procedures':
                logger.info("Using special handling for procedures section")
                return self._generate_procedures_section(synopsis_content, existing_sections)

            # Get template
            template = self._get_section_template(study_type, section_name)

            # Format previous sections if they exist
            previous_sections = self._format_previous_sections(existing_sections) if existing_sections else ""

            # Generate content
            content = self.gpt_handler.generate_section(
                section_name=section_name,
                synopsis_content=synopsis_content,
                previous_sections=previous_sections
            )

            # Validate generated content
            if not content or len(content.strip()) < 10:
                raise ValueError(f"Generated content for {section_name} is too short or empty")

            logger.info(f"Successfully generated {section_name} section")
            return content

        except Exception as e:
            logger.error(f"Error generating section {section_name}: {str(e)}")
            raise

    def _generate_study_design_section(self, synopsis_content: str, study_type: str, existing_sections: dict = None):
        """Generate study design section with Mermaid diagram"""
        try:
            # Generate base content first
            content = self.gpt_handler.generate_section(
                section_name='study_design',
                synopsis_content=synopsis_content,
                previous_sections=self._format_previous_sections(existing_sections)
            )

            # Extract design information from synopsis for diagram
            design_info = self._extract_design_info(synopsis_content)

            # Generate Mermaid diagram code
            mermaid_code = self._generate_mermaid_diagram(design_info)

            # Split content and add study schema section
            content_parts = content.split('## Overall Design')
            if len(content_parts) > 1:
                content = f"{content_parts[0]}## Overall Design{content_parts[1]}\n\n## Study Schema\n"
            else:
                content = f"{content}\n\n## Study Schema\n"

            # Render Mermaid diagram
            st_mermaid(mermaid_code)

            return content

        except Exception as e:
            logger.error(f"Error generating study design section: {str(e)}")
            raise

    def _extract_design_info(self, synopsis_content: str) -> dict:
        """Extract study design information from synopsis"""
        try:
            # Use GPT to extract design information
            prompt = f"""
            Analyze this synopsis and extract the following information in JSON format:
            - Study design type (parallel, crossover, etc.)
            - Number of treatment groups
            - Study duration
            - Key timepoints/visits

            Synopsis:
            {synopsis_content}
            """

            response = self.gpt_handler.client.chat.completions.create(
                model=self.gpt_handler.model_name,
                messages=[
                    {"role": "system", "content": "Extract study design information in JSON format"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            design_info = eval(response.choices[0].message.content)
            return design_info

        except Exception as e:
            logger.error(f"Error extracting design info: {str(e)}")
            return {
                "design_type": "parallel",
                "treatment_groups": 2,
                "duration": "52 weeks",
                "timepoints": ["Screening", "Randomization", "Treatment", "Follow-up"]
            }

    def _generate_mermaid_diagram(self, design_info: dict) -> str:
        """Generate Mermaid diagram code based on study design"""
        try:
            if design_info["design_type"].lower() == "crossover":
                return self._generate_crossover_diagram(design_info)
            else:
                return self._generate_parallel_diagram(design_info)
        except Exception as e:
            logger.error(f"Error generating diagram: {str(e)}")
            return """graph TD
    A[Screening] --> B[Randomization]
    B --> C[Treatment Group 1]
    B --> D[Treatment Group 2]
    C --> E[Follow-up]
    D --> E"""

    def _generate_parallel_diagram(self, design_info: dict) -> str:
        """Generate diagram for parallel design"""
        groups = design_info.get("treatment_groups", 2)
        mermaid_code = ["graph TD"]
        mermaid_code.append("    A[Screening] --> B[Randomization]")
        
        # Add treatment groups
        for i in range(groups):
            group_letter = chr(67 + i)  # C, D, E, etc.
            mermaid_code.append(f"    B --> {group_letter}[Treatment Group {i + 1}]")
            mermaid_code.append(f"    {group_letter} --> F[Follow-up]")
        
        return "\n".join(mermaid_code)

    def _generate_crossover_diagram(self, design_info: dict) -> str:
        """Generate diagram for crossover design"""
        return """graph TD
    A[Screening] --> B[Randomization]
    B --> C[Group 1: Treatment A]
    B --> D[Group 2: Treatment B]
    C --> E[Washout]
    D --> E
    E --> F[Crossover]
    F --> G[Group 1: Treatment B]
    F --> H[Group 2: Treatment A]
    G --> I[Follow-up]
    H --> I"""

    def _generate_procedures_section(self, synopsis_content: str, existing_sections: dict = None):
        """Special handler for procedures section"""
        try:
            procedures_content = """
# Study Procedures

## Overview
This section details the procedures to be followed during the study, including screening, treatment, and follow-up phases.

## Screening Procedures
1. Informed consent
2. Demographics and medical history
3. Physical examination
4. Vital signs
5. Laboratory assessments
6. Disease assessment
7. Inclusion/exclusion criteria review

## Treatment Phase Procedures
1. Drug administration
2. Safety monitoring
3. Efficacy assessments
4. Laboratory tests
5. Quality of life assessments
6. Adverse event monitoring
7. Concomitant medication review

## Follow-up Procedures
1. Safety follow-up
2. Disease assessment
3. Survival status
4. Subsequent therapy documentation

## Study Assessments
### Safety Assessments
- Physical examinations
- Vital signs
- Laboratory tests
- Adverse event monitoring
- ECG monitoring when indicated

### Efficacy Assessments
- Disease-specific assessments
- Response evaluation
- Patient-reported outcomes
- Quality of life measures

### Laboratory Assessments
- Hematology
- Clinical chemistry
- Biomarker sampling
- PK/PD assessments when applicable
            """

            # Now use GPT to enhance this template with study-specific details
            enhanced_content = self.gpt_handler.generate_section(
                section_name='procedures',
                synopsis_content=synopsis_content,
                previous_sections=procedures_content
            )

            return enhanced_content if enhanced_content else procedures_content

        except Exception as e:
            logger.error(f"Error generating procedures section: {str(e)}")
            return procedures_content  # Return base template if enhancement fails

    def _get_section_template(self, study_type: str, section_name: str) -> dict:
        """Get template for a specific section"""
        try:
            return self.template_manager.get_section_template(study_type, section_name)
        except Exception as e:
            logger.error(f"Error getting template: {str(e)}")
            return {}

    def _format_previous_sections(self, existing_sections: dict) -> str:
        """Format previously generated sections for context"""
        try:
            formatted_sections = []
            for section_name, content in existing_sections.items():
                if content and isinstance(content, str):
                    formatted_sections.append(f"=== {section_name.upper()} ===\n{content}\n")
            return "\n".join(formatted_sections)
        except Exception as e:
            logger.error(f"Error formatting sections: {str(e)}")
            return ""
