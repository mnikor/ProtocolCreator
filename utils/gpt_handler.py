import logging
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

class GPTHandler:
    def __init__(self):
        try:
            self.api_key = os.environ.get('OPENAI_API_KEY')
            if not self.api_key:
                raise ValueError("OpenAI API key not found")
            self.client = OpenAI(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize GPT handler: {str(e)}")
            raise

    def generate_content(self, prompt: str, system_message: str = None) -> str:
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model="gpt-4",  # Fixed model name
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
