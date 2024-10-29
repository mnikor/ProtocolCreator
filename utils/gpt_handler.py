import os
from openai import OpenAI
from prompts.analysis_prompts import SYNOPSIS_ANALYSIS_PROMPT
from prompts.section_prompts import SECTION_PROMPTS

class GPTHandler:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model_name = "gpt-4o-2024-08-06"  # Updated model name

    def analyze_synopsis(self, synopsis_text):
        """Analyze synopsis using GPT-4"""
        try:
            prompt = SYNOPSIS_ANALYSIS_PROMPT.format(synopsis_text=synopsis_text)
            response = self.client.chat.completions.create(
                model=self.model_name,  # Using updated model name
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error analyzing synopsis: {str(e)}")

    def generate_section(self, section_name, synopsis_content, previous_sections=None):
        """Generate a specific protocol section"""
        try:
            section_prompt = SECTION_PROMPTS.get(section_name)
            if not section_prompt:
                raise ValueError(f"No prompt template found for section: {section_name}")
                
            prompt = section_prompt.format(
                synopsis_content=synopsis_content,
                previous_sections=previous_sections or ""
            )
            response = self.client.chat.completions.create(
                model=self.model_name,  # Using updated model name
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating section: {str(e)}")
