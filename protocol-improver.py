# protocol_improver.py

class ProtocolImprover:
    def __init__(self, gpt_handler):
        self.gpt_handler = gpt_handler
        
    async def improve_section(self, section_name: str, content: str, issues: Dict) -> str:
        """Improve section based on validation issues"""
        improvement_prompt = self._create_improvement_prompt(section_name, content, issues)
        improved_content = await self.gpt_handler.generate_section(
            section_name=section_name,
            prompt=improvement_prompt
        )
        return improved_content

    def _create_improvement_prompt(self, section_name: str, content: str, issues: Dict) -> str:
        missing_items = issues.get('missing_items', [])
        improvements_needed = [
            f"- Add {item}" for item in missing_items
        ]
        
        return f"""Improve this {section_name} section by addressing these issues:
{chr(10).join(improvements_needed)}

Current content:
{content}

Ensure the improved version:
1. Adds all missing elements
2. Maintains existing good content
3. Improves clarity and structure
4. Follows protocol standards
"""