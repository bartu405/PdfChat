import unittest
from fastapi.testclient import TestClient
from main import app
import os
from reportlab.pdfgen import canvas

client = TestClient(app)


class TestPDFUpload(unittest.TestCase):

    def test_invalid_file_type_upload(self):
        # Simulate uploading a non-PDF file (txt file)
        file_path = "test_file.txt"
        try:
            # Create the file
            with open(file_path, "w") as f:
                f.write("This is a test file.")

            # Open the file in binary mode for uploading
            with open(file_path, "rb") as file:
                response = client.post("/v1/pdf", files={"file": file})

            # Assert that a 400 Bad Request is returned
            self.assertEqual(response.status_code, 400)
            self.assertEqual(
                response.json()["detail"], "Invalid file type. Only PDFs are allowed.")

        finally:
            # Remove the file after the test
            if os.path.exists(file_path):
                os.remove(file_path)

    # Valid test
    def test_valid_pdf_upload(self):
        # Simulate uploading a valid PDF file
        file_path = "test_file.pdf"
        try:
            # Create a simple PDF file
            c = canvas.Canvas(file_path)
            c.drawString(100, 750, "This is a test PDF file.")
            c.save()

            # Open the file in binary mode for uploading
            with open(file_path, "rb") as file:
                response = client.post("/v1/pdf", files={"file": file})

            # Assert that the upload is successful
            self.assertEqual(response.status_code, 200)
            self.assertIn("pdf_id", response.json())

        finally:
            # Remove the file after the test
            if os.path.exists(file_path):
                os.remove(file_path)


if __name__ == "__main__":
    unittest.main()
