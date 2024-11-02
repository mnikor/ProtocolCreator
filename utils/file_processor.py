import logging
import io
from typing import Optional
import docx
import PyPDF2

logger = logging.getLogger(__name__)

def process_file_content(uploaded_file) -> Optional[str]:
    """Process uploaded file content based on file type"""
    try:
        file_type = uploaded_file.type
        
        # Process text files
        if file_type == "text/plain":
            return uploaded_file.getvalue().decode("utf-8")
            
        # Process Word documents
        elif "document" in file_type:
            doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
        # Process PDF files
        elif file_type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            return "\n".join([page.extract_text() for page in pdf_reader.pages])
            
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
            
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise Exception(f"Error processing file: {str(e)}")
