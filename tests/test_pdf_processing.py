import unittest
from unittest.mock import patch, MagicMock

from fastapi import HTTPException
from pdf_processing import extract_pdf_text


class TestPDFProcessing(unittest.TestCase):

    @patch("pdfplumber.open")
    def test_extract_pdf_text_success(self, mock_pdf_open):
        # Mock the PDF object and its behavior
        mock_pdf = MagicMock()
        mock_pdf.pages = [MagicMock(), MagicMock()]  # Simulate 2 pages
        mock_pdf.pages[0].extract_text.return_value = "Page 1 text."
        mock_pdf.pages[1].extract_text.return_value = "Page 2 text."
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        # Call the function
        text, page_count = extract_pdf_text(mock_pdf)

        # Assert the results
        self.assertEqual(text, "Page 1 text.Page 2 text.")
        self.assertEqual(page_count, 2)

    @patch("pdfplumber.open")
    def test_extract_pdf_text_error(self, mock_pdf_open):
        # Simulate an error when opening a PDF
        mock_pdf_open.side_effect = Exception("Error opening PDF")

        with self.assertRaises(HTTPException) as context:
            extract_pdf_text(MagicMock())

        # Check the exact error message and status code
        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail,
                         "Error extracting text from PDF.")

    @patch("pdfplumber.open")
    def test_extract_pdf_text_empty_pdf(self, mock_pdf_open):
        # Mock an empty PDF (no pages)
        mock_pdf = MagicMock()
        mock_pdf.pages = []
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        # Call the function
        text, page_count = extract_pdf_text(mock_pdf)

        # Assert the results
        self.assertEqual(text, "")
        self.assertEqual(page_count, 0)


if __name__ == "__main__":
    unittest.main()
