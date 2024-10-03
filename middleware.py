from fastapi import Request, HTTPException
from logging_config import logger

async def custom_error_handling_middleware(request: Request, call_next):
    logger.info(f"Received request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(
            f"Completed request: {request.method} {request.url} with status {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
