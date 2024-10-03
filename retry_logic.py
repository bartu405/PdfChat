from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests
import google.generativeai as genai
from fastapi import HTTPException
from logging_config import logger
from dotenv import load_dotenv
import os


load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type(
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
)
def generate_response_from_model(pdf_text: str, query: str):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    try:
        response = model.generate_content(f"{pdf_text}\n\nUser query: {query}")
        return response.text
    except requests.exceptions.Timeout:
        logger.error("Timeout occurred while connecting to the Gemini API.")
        raise HTTPException(
            status_code=504, detail="Gemini API request timed out."
        )
    except requests.exceptions.ConnectionError:
        logger.error(
            "Connection error occurred while connecting to the Gemini API."
        )
        raise HTTPException(
            status_code=502, detail="Error connecting to Gemini API."
        )
    except requests.HTTPError as e:
        if e.response.status_code == 429:
            logger.error("Rate limit exceeded on Gemini API.")
            raise HTTPException(
                status_code=429, detail="Rate limit exceeded, please try again later."
            )
        else:
            logger.error(f"HTTP error: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Internal server error while processing the request."
            )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Internal server error while processing the request."
        )
