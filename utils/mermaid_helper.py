import streamlit as st

def render_mermaid_to_text(diagram_code: str) -> str:
    '''Convert Mermaid diagram to text description'''
    try:
        # For now, just return a text description of the diagram
        return f"""
Study Flow Diagram:
{diagram_code}
"""
    except Exception as e:
        st.warning(f"Could not render diagram: {str(e)}")
        return None
