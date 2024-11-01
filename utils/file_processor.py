import logging
from docx import Document
import PyPDF2

logger = logging.getLogger(__name__)

def read_file_content(file):
    '''Read content from uploaded file'''
    try:
        # Get file extension
        file_name = file.name.lower()

        if file_name.endswith('.txt'):
            # Read text file
            return str(file.read(), 'utf-8')

        elif file_name.endswith('.docx'):
            # Read DOCX using python-docx
            doc = Document(file)
            return '\n'.join(paragraph.text for paragraph in doc.paragraphs)

        elif file_name.endswith('.pdf'):
            # Read PDF using PyPDF2
            pdf = PyPDF2.PdfReader(file)
            return '\n'.join(page.extract_text() for page in pdf.pages)

        else:
            raise ValueError(f"Unsupported file format: {file_name}")

    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        raise
