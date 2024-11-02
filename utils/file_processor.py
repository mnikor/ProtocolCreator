import logging
import io
from typing import Optional
import docx
import PyPDF2

logger = logging.getLogger(__name__)

def process_file_content(uploaded_file) -> str:
    """Process uploaded file content based on file type"""
    try:
        file_type = uploaded_file.type
        content = ""
        
        # Process text files
        if file_type == "text/plain":
            content = uploaded_file.getvalue().decode("utf-8")
            
        # Process Word documents    
        elif "document" in file_type:
            doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
            # Extract text from each paragraph including runs
            content = "\n".join(
                "".join(run.text for run in paragraph.runs)
                for paragraph in doc.paragraphs
                if any(run.text.strip() for run in paragraph.runs)
            )
            
        # Process PDF files    
        elif file_type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            content = "\n".join(
                page.extract_text().strip()
                for page in pdf_reader.pages
                if page.extract_text().strip()
            )
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
            
        # Validate extracted content
        if not content.strip():
            raise ValueError("No content could be extracted from file")
            
        return content.strip()
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise Exception(f"Error processing file: {str(e)}")
