import pdfplumber
import re
from logging_config import logger
from fastapi import HTTPException


def clean_text(text):
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespaces
    return text


def extract_pdf_text(uploaded_pdf):
    """Extracts text and metadata from a PDF file, with cleaning."""
    try:
        with pdfplumber.open(uploaded_pdf.file) as pdf:
            # Extract text from each page of the PDF and concatenate it
            full_text = ''.join([page.extract_text()
                                for page in pdf.pages if page.extract_text()])

            # Clean the extracted text
            cleaned_text = clean_text(full_text)

            # Get the total page count
            page_count = len(pdf.pages)

        return cleaned_text, page_count

    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error extracting text from PDF.")
