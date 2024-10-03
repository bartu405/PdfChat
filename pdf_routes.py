from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
from pdf_processing import extract_pdf_text
from logging_config import logger
from retry_logic import generate_response_from_model
from models import ChatRequest
from cache import get_cached_response, cache_response

pdf_router = APIRouter()

pdf_storage = {}


@pdf_router.post("/v1/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    logger.info("Received request to upload PDF.")

    # Log the details of the uploaded file
    logger.debug(
        f"Uploaded file details: filename={file.filename}, content_type={file.content_type}")

    if file.content_type != "application/pdf":
        logger.warning("Invalid file type uploaded.")
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDFs are allowed.")

    try:
        pdf_id = str(uuid.uuid4())
        logger.info(f"Starting PDF text extraction for file: {file.filename}")
        pdf_text, page_count = extract_pdf_text(file)
        pdf_storage[pdf_id] = {
            "filename": file.filename,
            "text": pdf_text,
            "page_count": page_count
        }
        logger.info(f"PDF successfully processed and stored with ID: {pdf_id}")
        return {"pdf_id": pdf_id}
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error processing PDF: {str(e)}")


@pdf_router.post("/v1/chat/{pdf_id}")
async def chat_with_pdf(pdf_id: str, request: ChatRequest):
    logger.info(f"Received chat request for PDF ID: {pdf_id}")

    if pdf_id not in pdf_storage:
        logger.warning(f"PDF not found: {pdf_id}")
        raise HTTPException(status_code=404, detail="PDF not found.")

    if not request.query.strip():
        logger.warning(f"Empty query received for PDF ID: {pdf_id}")
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    cached_response = get_cached_response(request.query)
    if cached_response:
        logger.info(f"Serving cached response for query: {request.query}")
        return {"response": cached_response}

    try:
        pdf_data = pdf_storage[pdf_id]
        pdf_text = pdf_data["text"]
        response_text = generate_response_from_model(pdf_text, request.query)
        cache_response(request.query, response_text)
        return {"response": response_text}
    except Exception as e:
        logger.error(
            f"Error generating response for PDF ID {pdf_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error generating response: {str(e)}")
