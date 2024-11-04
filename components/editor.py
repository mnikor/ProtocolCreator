def generate_ai_suggestion(field: str, section_name: str) -> str:
    try:
        synopsis_content = st.session_state.get('synopsis_content')
        study_type = st.session_state.get('study_type')
        
        if not synopsis_content or not study_type:
            st.error("⚠️ Missing required context. Please ensure protocol is generated first.")
            return None
            
        # Create GPT handler
        gpt_handler = GPTHandler()
        
        # Build prompt
        context = f'''Based on this synopsis:
{synopsis_content}

Generate specific content for the {field.replace('_', ' ')} field in the {section_name} section.
This is for a {study_type} study.

Requirements:
- Be specific and detailed
- Match the study context and type
- Format key points with *italic* markers
- Be concise but comprehensive'''

        # Generate suggestion
        suggestion = gpt_handler.generate_content(
            prompt=context,
            system_message="You are a protocol development expert. Generate focused, scientific content."
        )
        
        return suggestion
            
    except Exception as e:
        logger.error(f"AI suggestion error: {str(e)}")
        st.error(f"Error generating suggestion: {str(e)}")
        return None
