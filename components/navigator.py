import streamlit as st
import logging
import time
from utils.template_section_generator import TemplateSectionGenerator
from utils.synopsis_validator import SynopsisValidator
from config.study_type_definitions import COMPREHENSIVE_STUDY_CONFIGS
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)

def check_connection():
    """Check if application can establish necessary connections"""
    try:
        generator = TemplateSectionGenerator()
        return True
    except Exception as e:
        logger.error(f"Connection check failed: {str(e)}")
        return False

def create_docx(generated_sections):
    try:
        doc = Document()
        
        # Set up basic styles
        styles = doc.styles
        if 'TOC 1' not in styles:
            toc_style = styles.add_style('TOC 1', 1)
            toc_style.base_style = styles['Normal']
            font = toc_style.font
            font.size = Pt(12)
            font.name = 'Calibri'
        
        # Add title
        title = doc.add_heading('Study Protocol', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_paragraph()
        
        # Add table of contents header
        doc.add_heading('Table of Contents', level=1)
        
        # Add TOC entries as regular paragraphs with indentation
        for section in generated_sections:
            p = doc.add_paragraph(style='TOC 1')
            p.paragraph_format.left_indent = Inches(0.25)
            p.add_run(section.replace('_', ' ').title())
        
        doc.add_page_break()
        
        # Add sections with proper formatting
        for section, content in generated_sections.items():
            # Add section heading
            heading = doc.add_heading(section.replace('_', ' ').title(), level=1)
            
            # Split content into paragraphs
            paragraphs = content.split('\n')
            for para in paragraphs:
                if para.strip():
                    p = doc.add_paragraph()
                    # Handle formatting markers
                    parts = para.split('*')
                    for i, part in enumerate(parts):
                        if part.strip():
                            run = p.add_run(part.strip())
                            run.font.name = 'Calibri'
                            run.font.size = Pt(11)
                            if i % 2:  # Odd indices are italic
                                run.italic = True
            
            # Add spacing between sections
            doc.add_paragraph()
        
        return doc
        
    except Exception as e:
        logger.error(f"Error creating DOCX: {str(e)}")
        raise Exception(f"Failed to create DOCX document: {str(e)}")

def render_navigator():
    """Render the section navigator with improved generation tracking"""
    try:
        # Add custom styling
        st.markdown("""
            <style>
            .section-status {
                font-size: 0.9em;
                color: #666;
                margin-top: 5px;
            }
            .progress-section {
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 1rem;
            }
            .stButton > button:first-child {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                height: 3em;
                border-radius: 10px;
                margin: 0.5em 0;
                width: 100%;
            }
            .disabled-button {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .download-buttons {
                display: flex;
                gap: 10px;
            }
            .download-buttons > div {
                flex: 1;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Initialize session state for progress tracking
        if 'generation_in_progress' not in st.session_state:
            st.session_state.generation_in_progress = False
        if 'section_status' not in st.session_state:
            st.session_state.section_status = {}
            
        # Check connection
        if not check_connection():
            st.sidebar.error("⚠️ Connection issues detected. Please refresh the page.")
            return
            
        st.sidebar.markdown("## Protocol Development")
        
        # Study type detection and analysis
        if synopsis_content := st.session_state.get('synopsis_content'):
            validator = SynopsisValidator()
            validation_result = validator.validate_synopsis(synopsis_content)
            
            if validation_result:
                if study_type := validation_result.get('study_type'):
                    st.sidebar.success(f"📋 Study Type: {study_type.replace('_', ' ').title()}")
                    if study_type in ['phase1', 'phase2', 'phase3', 'phase4']:
                        st.sidebar.info(f"🔬 Clinical Trial Phase: {study_type[-1]}")
                else:
                    st.sidebar.warning("⚠️ Could not detect study type")
                    
                if therapeutic_area := validation_result.get('therapeutic_area'):
                    st.sidebar.info(f"🏥 Therapeutic Area: {therapeutic_area.replace('_', ' ').title()}")
                    
            # Section Navigation
            study_type = st.session_state.get('study_type')
            if study_type:
                st.sidebar.markdown("### 📑 Protocol Sections")
                
                study_config = COMPREHENSIVE_STUDY_CONFIGS.get(study_type, {})
                sections = study_config.get('required_sections', [])
                
                # Progress tracking
                completed = sum(1 for section in sections 
                              if st.session_state.section_status.get(section, {}).get('status') == 'completed')
                total = len(sections)
                progress = completed / total if total > 0 else 0
                
                # Progress section
                with st.sidebar.container():
                    st.markdown('<div class="progress-section">', unsafe_allow_html=True)
                    st.progress(progress, text=f"Progress: {completed}/{total} sections")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Generate Protocol button
                if not st.session_state.generation_in_progress:
                    if st.sidebar.button(
                        "Generate Complete Protocol",
                        key="generate_btn",
                        use_container_width=True
                    ):
                        st.session_state.generation_in_progress = True
                        progress_bar = st.sidebar.progress(0)
                        status_area = st.sidebar.empty()
                        
                        try:
                            generator = TemplateSectionGenerator()
                            sections = study_config.get('required_sections', [])
                            
                            generated_sections = {}
                            for idx, section in enumerate(sections):
                                progress = (idx + 1) / len(sections)
                                progress_bar.progress(progress)
                                status_area.info(f"Generating {section.replace('_', ' ').title()}...")
                                
                                try:
                                    content = generator.generate_section(
                                        section_name=section,
                                        synopsis_content=synopsis_content,
                                        study_type=study_type
                                    )
                                    if content:
                                        generated_sections[section] = content
                                        st.session_state.section_status[section] = {
                                            'status': 'completed',
                                            'timestamp': time.strftime('%H:%M:%S')
                                        }
                                except Exception as e:
                                    logger.error(f"Error generating {section}: {str(e)}")
                                    st.session_state.section_status[section] = {
                                        'status': 'failed',
                                        'error': str(e)
                                    }
                                    continue
                            
                            st.session_state.generated_sections = generated_sections
                            st.session_state.generation_in_progress = False
                            st.rerun()
                            
                        except Exception as e:
                            logger.error(f"Error in protocol generation: {str(e)}")
                            st.session_state.generation_in_progress = False
                            st.sidebar.error(f"Error: {str(e)}")
                
                # Section navigation and download options
                if generated_sections := st.session_state.get('generated_sections'):
                    # Display sections
                    st.sidebar.markdown("### 📑 Generated Sections")
                    for section in sections:
                        if content := generated_sections.get(section):
                            with st.sidebar.expander(f"📝 {section.replace('_', ' ').title()}"):
                                st.text_area(
                                    "Content",
                                    value=content,
                                    height=150,
                                    disabled=True,
                                    key=f"nav_{section}"
                                )
                    
                    # Download options
                    st.sidebar.markdown("### 📥 Download Protocol")
                    
                    try:
                        # Create temporary directory if it doesn't exist
                        if not os.path.exists('temp'):
                            os.makedirs('temp')
                        
                        # Generate DOCX first
                        doc = create_docx(generated_sections)
                        temp_docx = 'temp/protocol.docx'
                        doc.save(temp_docx)
                        
                        # Add DOCX download button
                        with open(temp_docx, 'rb') as f:
                            docx_data = f.read()
                            st.sidebar.download_button(
                                label="📄 Download DOCX",
                                data=docx_data,
                                file_name="protocol.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )
                        
                        # Generate PDF using WeasyPrint
                        # Create HTML content from sections
                        html_content = '''
                        <html>
                            <head>
                                <style>
                                    @page {
                                        margin: 2.5cm;
                                        @top-right {
                                            content: counter(page);
                                        }
                                    }
                                    body {
                                        font-family: Arial, sans-serif;
                                        line-height: 1.5;
                                    }
                                    h1 {
                                        color: #2c3e50;
                                        margin-top: 1em;
                                        margin-bottom: 0.5em;
                                    }
                                    .toc-entry {
                                        margin: 0.5em 0;
                                        padding-left: 20px;
                                    }
                                    .content {
                                        text-align: justify;
                                    }
                                    .italic {
                                        font-style: italic;
                                    }
                                </style>
                            </head>
                            <body>
                                <h1 style="text-align: center;">Study Protocol</h1>
                                <div style="text-align: center; margin: 20px 0;">
                                    Generated: ''' + time.strftime("%B %d, %Y") + '''
                                </div>
                                
                                <h1>Table of Contents</h1>
                        '''
                        
                        # Add TOC entries
                        for section in generated_sections:
                            html_content += f'<div class="toc-entry">{section.replace("_", " ").title()}</div>'
                        
                        # Add sections
                        for section, content in generated_sections.items():
                            html_content += f'''
                                <h1>{section.replace("_", " ").title()}</h1>
                                <div class="content">
                            '''
                            
                            # Handle italic markers
                            paragraphs = content.split('\n')
                            for para in paragraphs:
                                if para.strip():
                                    parts = para.split('*')
                                    formatted_para = ''
                                    for i, part in enumerate(parts):
                                        if part.strip():
                                            if i % 2:  # Odd indices are italic
                                                formatted_para += f'<span class="italic">{part}</span>'
                                            else:
                                                formatted_para += part
                                    html_content += f'<p>{formatted_para}</p>'
                            
                            html_content += '</div>'
                        
                        html_content += '''
                            </body>
                        </html>
                        '''
                        
                        # Configure fonts
                        font_config = FontConfiguration()
                        
                        # Generate PDF
                        temp_pdf = 'temp/protocol.pdf'
                        HTML(string=html_content).write_pdf(
                            temp_pdf,
                            font_config=font_config,
                            presentational_hints=True
                        )
                        
                        # Add PDF download button
                        with open(temp_pdf, 'rb') as f:
                            pdf_data = f.read()
                            st.sidebar.download_button(
                                label="📥 Download PDF",
                                data=pdf_data,
                                file_name="protocol.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        
                        # Cleanup temporary files
                        os.remove(temp_docx)
                        os.remove(temp_pdf)
                        
                    except Exception as e:
                        error_msg = str(e)
                        logger.error(f"Document creation error: {error_msg}")
                        st.sidebar.error(f"Error creating documents: {error_msg}")
                        
    except Exception as e:
        logger.error(f"Error in navigator rendering: {str(e)}")
        st.sidebar.error("An error occurred while rendering the navigator")
