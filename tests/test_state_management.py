import unittest
from fastapi import HTTPException
from pdf_routes import chat_with_pdf
from models import ChatRequest 
from pdf_routes import pdf_storage 
import asyncio


class TestPDFStateManagement(unittest.TestCase):
    def setUp(self):
        # Clean up the state before each test
        pdf_storage.clear()

    def test_add_pdf_to_storage(self):
        # Simulate adding a PDF to the storage
        pdf_id = "test_pdf_id"
        pdf_storage[pdf_id] = {
            "filename": "test.pdf",
            "text": "This is a test PDF.",
            "page_count": 2
        }

        # Check that the PDF was added correctly
        self.assertIn(pdf_id, pdf_storage)
        self.assertEqual(pdf_storage[pdf_id]["filename"], "test.pdf")
        self.assertEqual(pdf_storage[pdf_id]["text"], "This is a test PDF.")
        self.assertEqual(pdf_storage[pdf_id]["page_count"], 2)

    def test_retrieve_pdf_from_storage(self):
        # Add a sample PDF to storage
        pdf_id = "test_pdf_id"
        pdf_storage[pdf_id] = {
            "filename": "test.pdf",
            "text": "This is a test PDF.",
            "page_count": 2
        }

        # Simulate retrieving the PDF from storage
        retrieved_pdf = pdf_storage.get(pdf_id)

        # Assert the PDF was correctly retrieved
        self.assertIsNotNone(retrieved_pdf)
        self.assertEqual(retrieved_pdf["filename"], "test.pdf")
        self.assertEqual(retrieved_pdf["text"], "This is a test PDF.")
        self.assertEqual(retrieved_pdf["page_count"], 2)

    def test_pdf_not_found_in_storage(self):
        # Try retrieving a non-existent PDF
        pdf_id = "non_existent_pdf_id"
        with self.assertRaises(HTTPException) as context:
            asyncio.run(chat_with_pdf(pdf_id, ChatRequest(
                query="What is this document?")))

        # Assert the correct HTTPException is raised
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "PDF not found.")


if __name__ == '__main__':
    unittest.main()
