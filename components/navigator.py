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
from fpdf import FPDF
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def extract_table_data(html_table):
    '''Extract data from HTML table string'''
    try:
        soup = BeautifulSoup(html_table, 'html.parser')
        rows = []
        
        # Get headers
        headers = []
        for th in soup.find_all('th'):
            headers.append(th.text.strip())
        if headers:
            rows.append(headers)
            
        # Get data rows
        for tr in soup.find_all('tr')[1:]:  # Skip header row
            row = []
            for td in tr.find_all('td'):
                row.append(td.text.strip())
            if row:
                rows.append(row)
                
        return rows
    except:
        return None

def create_pdf_table(pdf, rows):
    '''Create PDF table from data rows'''
    if not rows:
        return
        
    # Calculate column widths
    n_cols = len(rows[0])
    col_width = pdf.get_page_width() / n_cols - 20
    
    # Add table headers
    pdf.set_font('Arial', 'B', 10)
    for header in rows[0]:
        pdf.cell(col_width, 7, header, 1)
    pdf.ln()
    
    # Add table data
    pdf.set_font('Arial', '', 10)
    for row in rows[1:]:
        for cell in row:
            pdf.cell(col_width, 6, cell, 1)
        pdf.ln()

def create_pdf(generated_sections):
    try:
        # Initialize PDF
        pdf = PDF()
        pdf.set_margins(20, 20, 20)
        
        # Title page
        pdf.add_page()
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 20, 'Study Protocol', align='C', ln=True)
        pdf.ln(20)
        
        # Add date
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Generated: {time.strftime("%B %d, %Y")}', align='C', ln=True)
        
        # Table of contents
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Table of Contents', ln=True)
        pdf.ln(5)
        
        # TOC entries with page numbers
        pdf.set_font('Arial', '', 12)
        toc_pages = {}
        current_page = pdf.page_no() + 1
        
        for section in generated_sections:
            section_title = section.replace('_', ' ').title()
            toc_pages[section] = current_page
            
            # Add TOC entry with dots
            dots = '.' * (50 - len(section_title))
            pdf.cell(0, 8, f'{section_title} {dots} {current_page}', ln=True)
            current_page += 1
        
        # Content pages
        for section, content in generated_sections.items():
            pdf.add_page()
            
            # Section heading
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, section.replace('_', ' ').title(), ln=True)
            pdf.ln(5)
            
            # Process content
            pdf.set_font('Arial', '', 11)
            paragraphs = content.split('\n')
            
            for para in paragraphs:
                if para.strip():
                    if para.startswith('<table'):
                        # Convert HTML table to PDF table
                        rows = extract_table_data(para)
                        if rows:
                            create_pdf_table(pdf, rows)
                            pdf.ln(5)
                    elif para.startswith('```mermaid'):
                        # Skip mermaid diagrams in PDF for now
                        continue
                    else:
                        # Handle italic text
                        parts = para.split('*')
                        for i, part in enumerate(parts):
                            if part.strip():
                                pdf.set_font('Arial', 'I' if i % 2 else '', 11)
                                pdf.multi_cell(0, 5, part.strip())
                        pdf.ln(3)
                else:
                    pdf.ln(5)
        
        return pdf
        
    except Exception as e:
        logger.error(f"Error creating PDF: {str(e)}")
        raise Exception(f"Failed to create PDF document: {str(e)}")

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
                        
                        # Generate and download PDF
                        try:
                            pdf = create_pdf(generated_sections)
                            temp_pdf = 'temp/protocol.pdf'
                            pdf.output(temp_pdf)
                            
                            with open(temp_pdf, 'rb') as f:
                                pdf_data = f.read()
                                st.sidebar.download_button(
                                    label="📥 Download PDF",
                                    data=pdf_data,
                                    file_name="protocol.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                            
                            # Cleanup PDF file
                            os.remove(temp_pdf)
                            
                        except Exception as e:
                            logger.error(f"Error creating PDF: {str(e)}")
                            st.sidebar.warning("⚠️ PDF generation failed. Please try DOCX format.")
                        
                        # Cleanup DOCX file
                        os.remove(temp_docx)
                        
                    except Exception as e:
                        logger.error(f"Error preparing downloads: {str(e)}")
                        st.sidebar.error("Error preparing downloads. Please try again.")
                        
    except Exception as e:
        logger.error(f"Error in navigator: {str(e)}")
        st.error(f"An error occurred: {str(e)}")
