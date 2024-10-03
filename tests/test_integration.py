import unittest
from fastapi.testclient import TestClient
from main import app
from pdf_routes import pdf_storage 
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import os

client = TestClient(app)

# Function to create a more complex PDF with text, image, and table


def generate_test_pdf(filename):
    """Generates a complex test PDF with text, a simulated image (rectangle), and a table."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Add some text
    c.drawString(100, height - 100,
                 "This is a test PDF with text, a table, and a simulated image.")

    # Draw a rectangle to simulate an image
    c.setStrokeColor(colors.black)
    c.setFillColor(colors.lightgrey)
    # Simulated image (a rectangle)
    c.rect(100, height - 250, 200, 150, fill=True)

    # Save the canvas so we can add a table
    c.save()

    # Create a table and append it to the same PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    # Data for the table
    data = [
        ["Header 1", "Header 2", "Header 3"],
        ["Row 1, Col 1", "Row 1, Col 2", "Row 1, Col 3"],
        ["Row 2, Col 1", "Row 2, Col 2", "Row 2, Col 3"],
    ]

    # Create the table with some styling
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))

    elements.append(table)
    doc.build(elements)


class TestIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Generate the test PDF before running tests
        generate_test_pdf("test_pdf.pdf")

    @classmethod
    def tearDownClass(cls):
        # Clean up the test PDF after all tests are done
        os.remove("test_pdf.pdf")

    def setUp(self):
        # Clear PDF storage before each test
        pdf_storage.clear()

    def test_pdf_upload_success(self):
        # Simulate uploading a valid PDF file
        with open("test_pdf.pdf", "rb") as file:
            response = client.post("/v1/pdf", files={"file": file})

        # Assert the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert that the PDF ID is returned in the response
        data = response.json()
        self.assertIn("pdf_id", data)

        # Assert that the PDF was stored correctly
        pdf_id = data["pdf_id"]
        self.assertIn(pdf_id, pdf_storage)

    def test_invalid_file_type_upload(self):
        # Simulate uploading an invalid file type
        with open("test_file.txt", "w") as f:
            f.write("This is a test file.")

        with open("test_file.txt", "rb") as file:
            response = client.post("/v1/pdf", files={"file": file})

        # Assert a 400 Bad Request is returned
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()[
                "detail"], "Invalid file type. Only PDFs are allowed."
        )

    def test_chat_with_pdf_success(self):
        # First, upload a PDF to the API
        with open("test_pdf.pdf", "rb") as file:
            upload_response = client.post("/v1/pdf", files={"file": file})

        pdf_id = upload_response.json()["pdf_id"]

        # Simulate a chat request
        chat_payload = {"query": "What is the content of this PDF?"}
        response = client.post(f"/v1/chat/{pdf_id}", json=chat_payload)

        # Assert the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Assert the API returns a valid response
        data = response.json()
        self.assertIn("response", data)

    def test_pdf_not_found(self):
        # Simulate a chat request with a non-existent PDF ID
        chat_payload = {"query": "What is the content of this PDF?"}
        response = client.post(
            "/v1/chat/non_existent_pdf_id", json=chat_payload)

        # Assert the response is 404 Not Found
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "PDF not found.")

    def test_empty_query(self):
        # First, upload a PDF to the API
        with open("test_pdf.pdf", "rb") as file:
            upload_response = client.post("/v1/pdf", files={"file": file})

        pdf_id = upload_response.json()["pdf_id"]

        # Simulate a chat request with an empty query
        chat_payload = {"query": ""}
        response = client.post(f"/v1/chat/{pdf_id}", json=chat_payload)

        # Assert the response is 400 Bad Request
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Query cannot be empty")

    """ def test_upload_corrupt_pdf(self):
        # Create a dummy corrupt PDF (just random bytes)
        with open("corrupt_pdf.pdf", "wb") as f:
            f.write(b"This is not a valid PDF format")

        with open("corrupt_pdf.pdf", "rb") as file:
            response = client.post("/v1/pdf", files={"file": file})

        # Assert that a 500 Internal Server Error is returned
        self.assertEqual(response.status_code, 500)

        # Assert that the error message contains the expected message
        self.assertIn(
            "Error reading PDF file", response.json()["detail"]
        )

        # Clean up the corrupt PDF file
        os.remove("corrupt_pdf.pdf") """

    def test_large_query_chat(self):
        # Upload a valid PDF first
        with open("test_pdf.pdf", "rb") as file:
            upload_response = client.post("/v1/pdf", files={"file": file})

        pdf_id = upload_response.json()["pdf_id"]

        # Simulate a large query
        large_query = "a" * 12000  # A very long query string

        chat_payload = {"query": large_query}
        response = client.post(f"/v1/chat/{pdf_id}", json=chat_payload)

        # Assert that a response is still valid
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json())


if __name__ == '__main__':
    unittest.main()
