import logging
from openai import OpenAI
import os
import re

logger = logging.getLogger(__name__)

class GPTHandler:
    def __init__(self):
        try:
            self.api_key = os.environ.get('OPENAI_API_KEY')
            if not self.api_key:
                raise ValueError("OpenAI API key not found")
                
            self.client = OpenAI(api_key=self.api_key)
            
            # Test connection with a simple completion
            test_response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            if not test_response.choices:
                raise ValueError("Failed to get valid response from OpenAI API")
                
            logger.info("GPT handler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize GPT handler: {str(e)}")
            raise

    def _simplify_language(self, text: str) -> str:
        """Remove overly formal language"""
        formal_phrases = {
            'meticulously': 'carefully',
            'thoroughly': 'completely',
            'comprehensively': 'fully',
            'exhaustively': 'completely',
            'painstakingly': 'carefully',
            'scrupulously': 'carefully',
            'facilitate': 'help',
            'utilize': 'use',
            'implement': 'use',
            'commence': 'start',
            'terminate': 'end',
            'endeavor': 'try',
            'necessitate': 'need',
            'pursuant to': 'following',
            'aforementioned': 'previous',
            'accordingly': 'therefore'
        }
        
        for formal, simple in formal_phrases.items():
            text = re.sub(
                rf'\b{formal}\b',
                simple,
                text,
                flags=re.IGNORECASE
            )
        
        return text

    def generate_content(self, prompt: str, system_message: str = None) -> str:
        try:
            if not prompt.strip():
                logger.error("Empty prompt provided")
                raise ValueError("Empty prompt provided")
                
            messages = []
            default_system_message = '''
            Write in clear, direct language appropriate for technical documents.
            - Use simple, precise terms
            - Be direct and clear
            - Avoid unnecessary formality
            - Focus on essential information
            - Use active voice
            - Keep sentences concise
            '''
            
            messages.append({
                "role": "system", 
                "content": system_message or default_system_message
            })
            messages.append({"role": "user", "content": prompt})
            
            logger.info("Sending request to OpenAI API")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.3,
                max_tokens=3000
            )
            
            if not response.choices:
                logger.error("No choices in response")
                raise ValueError("No response choices returned from API")
                
            content = response.choices[0].message.content
            if not content:
                logger.error("Empty content returned")
                raise ValueError("Empty content returned from API")
            
            # Simplify language in the response
            content = self._simplify_language(content)
            
            logger.info("Successfully generated content")
            return content
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
