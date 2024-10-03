import unittest
from unittest.mock import patch, MagicMock
from pdf_routes import chat_with_pdf
from models import ChatRequest
from pdf_routes import pdf_storage
import asyncio
from fastapi import HTTPException


class TestGeminiIntegration(unittest.TestCase):
    def setUp(self):
        # Setup a sample PDF in storage
        self.pdf_id = "test_pdf_id"
        pdf_storage[self.pdf_id] = {
            "filename": "test.pdf",
            "text": "Sample PDF text.",
            "page_count": 1
        }

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_chat_with_pdf_success(self, mock_generate_content):
        # Mock the Gemini API response
        mock_response = MagicMock()
        mock_response.text = "Mocked Gemini API response."
        mock_generate_content.return_value = mock_response

        # Create a ChatRequest
        request = ChatRequest(query="What is the content?")

        # Call the async function
        response = asyncio.run(chat_with_pdf(self.pdf_id, request))
        self.assertEqual(response["response"], "Mocked Gemini API response.")

    def test_chat_with_pdf_pdf_not_found(self):
        # Create a ChatRequest
        request = ChatRequest(query="What is the content?")

        # Call the async function with a non-existent PDF ID
        with self.assertRaises(HTTPException) as context:
            asyncio.run(chat_with_pdf("invalid_pdf_id", request))

        # Assert that the status code is 404
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "PDF not found.")

    @patch('google.generativeai.GenerativeModel.generate_content')
    def test_chat_with_pdf_gemini_api_error(self, mock_generate_content):
        # Simulate an error from the Gemini API
        mock_generate_content.side_effect = Exception("Gemini API error")

        # Create a ChatRequest
        request = ChatRequest(query="What is the content?")

        # Call the async function
        with self.assertRaises(Exception) as context:
            asyncio.run(chat_with_pdf(self.pdf_id, request))

        self.assertIn("Error generating response", str(context.exception))

    def test_chat_with_pdf_empty_query(self):
        # Create an empty ChatRequest
        request = ChatRequest(query="")

        # Call the async function
        with self.assertRaises(HTTPException) as context:
            asyncio.run(chat_with_pdf(self.pdf_id, request))

        # Check that the status code is 400 and the message is correct
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "Query cannot be empty")


if __name__ == '__main__':
    unittest.main()
