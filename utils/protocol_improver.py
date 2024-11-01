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
            return improved_content
        except Exception as e:
            logger.error(f"Error improving section {section_name}: {str(e)}")
            return content

    def _create_improvement_prompt(self, section_name: str, content: str, issues: Dict) -> str:
        """Create improvement prompt based on validation issues"""
        missing_items = issues.get('missing_items', [])
        recommendations = issues.get('recommendations', [])
        
        prompt_parts = [
            f"Improve this {section_name} section while maintaining existing content structure.",
            "\nRequired improvements:"
        ]
        
        if missing_items:
            prompt_parts.append("\nAdd missing elements:")
            for item in missing_items:
                prompt_parts.append(f"- {item}")
                
        if recommendations:
            prompt_parts.append("\nAddress recommendations:")
            for rec in recommendations:
                prompt_parts.append(f"- {rec}")
                
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
