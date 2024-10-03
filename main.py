import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from middleware import custom_error_handling_middleware
from pdf_routes import pdf_router

load_dotenv()

app = FastAPI()

app.middleware("http")(custom_error_handling_middleware)

# Include the PDF-related routes
app.include_router(pdf_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
