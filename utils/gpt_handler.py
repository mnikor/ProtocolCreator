import logging
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

class GPTHandler:
    def __init__(self):
        """Initialize OpenAI client with API key from environment"""
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    def generate_content(self, prompt: str) -> str:
        '''Generate content using GPT-4 based on the provided prompt'''
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a protocol development assistant with expertise in clinical study protocols."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
