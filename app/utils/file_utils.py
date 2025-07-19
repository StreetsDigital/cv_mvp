import logging
import PyPDF2
import docx
from typing import Optional
from io import BytesIO

logger = logging.getLogger(__name__)

class FileProcessor:
    """File processing utilities for CV uploads"""
    
    @staticmethod
    def extract_text_from_file(file_content: bytes, file_type: str) -> Optional[str]:
        """Extract text from uploaded file based on type"""
        try:
            if file_type.lower() == 'pdf':
                return FileProcessor._extract_from_pdf(file_content)
            elif file_type.lower() in ['docx', 'doc']:
                return FileProcessor._extract_from_docx(file_content)
            elif file_type.lower() == 'txt':
                return FileProcessor._extract_from_txt(file_content)
            else:
                logger.warning(f"Unsupported file type: {file_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_type} file: {str(e)}")
            return None
    
    @staticmethod
    def _extract_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            raise
    
    @staticmethod
    def _extract_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            docx_file = BytesIO(file_content)
            doc = docx.Document(docx_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            raise
    
    @staticmethod
    def _extract_from_txt(file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8').strip()
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                return file_content.decode('latin-1').strip()
            except Exception as e:
                logger.error(f"Error extracting TXT text: {str(e)}")
                raise
    
    @staticmethod
    def validate_file_size(file_content: bytes, max_size_mb: int = 5) -> bool:
        """Validate file size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return len(file_content) <= max_size_bytes
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: list) -> bool:
        """Validate file type based on extension"""
        if '.' not in filename:
            return False
        
        file_extension = filename.rsplit('.', 1)[1].lower()
        return file_extension in [ext.lower() for ext in allowed_types]