import io
import PyPDF2
from docx import Document
import pandas as pd

def read_file_content(uploaded_file):
    """Process uploaded files based on their extension"""
    if uploaded_file is None:
        return None

    file_type = uploaded_file.type
    content = None

    try:
        if file_type == "application/pdf":
            content = read_pdf(uploaded_file)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            content = read_docx(uploaded_file)
        elif file_type == "text/plain":
            content = uploaded_file.getvalue().decode("utf-8")
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        return content
    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")

def read_pdf(file):
    """Extract text from PDF file"""
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.getvalue()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def read_docx(file):
    """Extract text from DOCX file"""
    doc = Document(io.BytesIO(file.getvalue()))
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text
