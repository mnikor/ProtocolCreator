import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class ProtocolImprover:
    def __init__(self, gpt_handler):
        self.gpt_handler = gpt_handler
        
    def improve_section(self, section_name: str, content: str, issues: Dict) -> str:
        """Improve section based on validation issues"""
        try:
            improvement_prompt = self._create_improvement_prompt(section_name, content, issues)
            
            improved_content = self.gpt_handler.generate_section(
                section_name=section_name,
                synopsis_content=content,  # Use existing content as context
                prompt=improvement_prompt
            )
            
            # Validate improvements maintain key content
            if not self._validate_improvements(content, improved_content):
                logger.warning(f"Improvements may have lost key content in {section_name}")
                return content  # Return original if improvements are problematic
                
            return improved_content
            
        except Exception as e:
            logger.error(f"Error improving section {section_name}: {str(e)}")
            return content  # Return original content on error

    def _create_improvement_prompt(self, section_name: str, content: str, issues: Dict) -> str:
        """Create detailed improvement prompt"""
        missing_items = issues.get('missing_items', [])
        recommendations = issues.get('recommendations', [])
        
        # Create structured prompt
        prompt_parts = [
            f"Improve this {section_name} section while maintaining existing content structure.",
            "\nRequired improvements:",
        ]
        
        # Add missing items
        if missing_items:
            prompt_parts.append("\nAdd missing elements:")
            for item in missing_items:
                prompt_parts.append(f"- {item.replace('_', ' ').title()}")
                
        # Add recommendations
        if recommendations:
            prompt_parts.append("\nAddress recommendations:")
            for rec in recommendations:
                prompt_parts.append(f"- {rec}")
                
        # Add content preservation instructions
        prompt_parts.extend([
            "\nRequirements:",
            "1. Preserve all existing valid content",
            "2. Maintain document structure and formatting",
            "3. Ensure compliance with protocol standards",
            "4. Use clear, precise language",
            "5. Add specific details for each missing element",
            
            "\nOriginal content:",
            content
        ])
        
        return "\n".join(prompt_parts)

    def _validate_improvements(self, original: str, improved: str) -> bool:
        """Validate that improvements maintain key content"""
        if not improved:
            return False
            
        # Extract key phrases from original (sentences containing important keywords)
        key_phrases = self._extract_key_phrases(original)
        
        # Check if key phrases are maintained (allowing for minor variations)
        maintained_count = 0
        for phrase in key_phrases:
            if self._phrase_exists(phrase, improved):
                maintained_count += 1
                
        # Require at least 70% of key phrases to be maintained
        return maintained_count >= len(key_phrases) * 0.7

    def _extract_key_phrases(self, content: str) -> List[str]:
        """Extract key phrases from content"""
        keywords = [
            "objective", "endpoint", "criteria", "analysis",
            "safety", "efficacy", "design", "population"
        ]
        
        phrases = []
        sentences = content.split(". ")
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                phrases.append(sentence)
                
        return phrases

    def _phrase_exists(self, phrase: str, content: str) -> bool:
        """Check if phrase exists in content, allowing minor variations"""
        # Convert to lowercase and remove extra whitespace
        phrase = " ".join(phrase.lower().split())
        content = " ".join(content.lower().split())
        
        # Check for exact match
        if phrase in content:
            return True
            
        # Check for similarity (70% of words match)
        phrase_words = set(phrase.split())
        content_words = set(content.split())
        
        matching_words = phrase_words.intersection(content_words)
        return len(matching_words) >= len(phrase_words) * 0.7
