import os
from openai import OpenAI
from prompts.analysis_prompts import SYNOPSIS_ANALYSIS_PROMPT
from prompts.section_prompts import SECTION_PROMPTS
from utils.template_manager import TemplateManager

class GPTHandler:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = "gpt-4o-2024-08-06"
        self.template_manager = TemplateManager()

    def analyze_synopsis(self, synopsis_text):
        """Analyze synopsis using GPT-4"""
        try:
            prompt = SYNOPSIS_ANALYSIS_PROMPT.format(synopsis_text=synopsis_text)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            analysis = response.choices[0].message.content
            # Determine study phase from analysis
            study_type = self._determine_study_phase(analysis)
            return analysis, study_type
        except Exception as e:
            raise Exception(f"Error analyzing synopsis: {str(e)}")

    def _determine_study_phase(self, analysis):
        """Determine study phase from analysis"""
        try:
            analysis_dict = json.loads(analysis)
            phase = analysis_dict.get("study_type_and_design", {}).get("phase", "")
            if "1" in phase:
                return "phase1"
            elif "2" in phase:
                return "phase2"
            elif "3" in phase:
                return "phase3"
            else:
                return "phase1"  # Default to phase 1 if unclear
        except Exception:
            return "phase1"

    def generate_section(self, section_name, synopsis_content, previous_sections=None, study_type=None):
        """Generate a specific protocol section using appropriate template"""
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
                except Exception:
                    pass  # Continue without template if not found

            prompt = section_prompt.format(
                synopsis_content=synopsis_content,
                previous_sections=previous_sections or "",
                template_guidance=template_guidance
            )

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating section: {str(e)}")
