import logging
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

class GPTHandler:
    def __init__(self):
        """Initialize OpenAI client with API key from environment"""
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    def generate_content(self, prompt: str, system_message: str = None) -> str:
        """Generate content using GPT-4 based on the provided prompt"""
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model="gpt-4o-2024-08-06",  # Update to correct model name
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content if response.choices else ""
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
