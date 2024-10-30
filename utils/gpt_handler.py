from openai import OpenAI
import os
import json
import logging
from utils.template_manager import TemplateManager
from prompts.section_prompts import SECTION_PROMPTS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTHandler:
    def __init__(self):
        try:
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            if not os.environ.get("OPENAI_API_KEY"):
                logger.error("OpenAI API key not found in environment variables")
                raise ValueError("OpenAI API key not found")
            self.model_name = "gpt-4"  # Updated model name as requested
            self.template_manager = TemplateManager()
        except Exception as e:
            logger.error(f"Error initializing GPTHandler: {str(e)}")
            raise

        # Rest of the file content remains the same
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
            }
        }
