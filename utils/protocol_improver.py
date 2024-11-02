import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class ProtocolImprover:
    def __init__(self, gpt_handler):
        self.gpt_handler = gpt_handler
        
    def improve_section(self, section_name: str, content: str, issues: Dict) -> str:
        """Improve section based on validation issues"""
        try:
            logger.info(f"Starting improvement for section: {section_name}")
            improvement_prompt = self._create_improvement_prompt(
                section_name=section_name,
                content=content,
                issues=issues,
                target_score=9.0  # Set target score to 9/10
            )
            
            # Generate improved content
            improved_content = self.gpt_handler.generate_section(
                section_name=section_name,
                synopsis_content=content,  # Use existing content as context
                prompt=improvement_prompt
            )
            
            if not improved_content:
                logger.warning(f"No improved content generated for {section_name}")
                return content
                
            logger.info(f"Successfully improved section: {section_name}")
            return improved_content
            
        except Exception as e:
            logger.error(f"Error improving section {section_name}: {str(e)}")
            return content

    def _create_improvement_prompt(self, section_name: str, content: str, issues: Dict, target_score: float) -> str:
        """Create detailed improvement prompt based on validation issues"""
        try:
            missing_items = issues.get('missing_items', [])
            recommendations = issues.get('recommendations', [])
            
            prompt_parts = [
                f"Improve this {section_name} section to achieve a quality score of {target_score}/10.",
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
                "1. Comprehensively address all missing elements",
                "2. Significantly enhance existing content",
                "3. Add detailed methodology and rationale",
                "4. Ensure robust scientific justification",
                "5. Include comprehensive statistical approach",
                "6. Address potential limitations and mitigations",
                "7. Maintain clear, precise language",
                "8. Exceed standard protocol requirements",
                
                "\nOriginal content:",
                content
            ])
            
            return "\n".join(prompt_parts)
            
        except Exception as e:
            logger.error(f"Error creating improvement prompt: {str(e)}")
            return f"Improve {section_name} content while maintaining structure:\n\n{content}"
