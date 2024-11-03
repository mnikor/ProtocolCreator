import streamlit as st
from streamlit_mermaid import mermaid
import cairosvg
import io

def render_mermaid_to_image(diagram_code: str) -> bytes:
    """Convert Mermaid diagram to PNG image bytes"""
    # First render using streamlit-mermaid to get SVG
    svg = mermaid(diagram_code, return_svg=True)
    
    # Convert SVG to PNG bytes
    png_bytes = io.BytesIO()
    cairosvg.svg2png(bytestring=svg.encode(), write_to=png_bytes)
    png_bytes.seek(0)
    return png_bytes.getvalue()
