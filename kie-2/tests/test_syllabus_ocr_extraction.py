import base64
import io
import unittest
from fastapi.testclient import TestClient
import pypdf

from app.main import app
from app.services.pdf_extract_service import get_pdf_extract_service


def create_sample_pdf_bytes(content_text: str) -> bytes:
    """Helper to create a valid in-memory PDF with text content using pypdf."""
    from pypdf import PdfWriter

    writer = PdfWriter()
    # Add a page
    writer.add_blank_page(width=612, height=792)
    # pypdf can write metadata or streams
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()


class TestSyllabusOCRExtraction(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.pdf_service = get_pdf_extract_service()

    def test_json_text_mode_backward_compatibility(self):
        """Mode 1: Verify existing JSON text payload extraction works seamlessly."""
        payload = {
            "syllabus_id": "syl_text_001",
            "text": (
                "Unit 1: Foundations of Zoology and Animal Taxonomy\n"
                "- Principles of Classification\n"
                "- Invertebrate Body Plans\n"
                "Unit 2: Cell Biology and Genetics\n"
                "- Cell Organelles\n"
                "- Mendelian Inheritance\n"
            ),
        }
        resp = self.client.post("/api/v1/kie/syllabus/extract", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("subjects", data)
        self.assertGreaterEqual(len(data["subjects"]), 1)
        for s in data["subjects"]:
            self.assertTrue(len(s["name"]) > 0)
            self.assertTrue(len(s["topics"]) > 0)

    def test_json_base64_mode(self):
        """Mode 2: Verify Base64-encoded PDF in JSON payload."""
        pdf_bytes = create_sample_pdf_bytes("Sample syllabus")
        b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

        payload = {
            "syllabus_id": "syl_b64_001",
            "file_base64": b64_pdf,
            "filename": "biology_syllabus.pdf",
        }
        resp = self.client.post("/api/v1/kie/syllabus/extract", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("subjects", data)
        self.assertGreaterEqual(len(data["subjects"]), 1)

    def test_multipart_file_upload_pdf(self):
        """Mode 3: Verify direct multipart PDF upload to /api/v1/kie/syllabus/extract-file."""
        pdf_bytes = create_sample_pdf_bytes("Unit 1: Principles of Management\nPlanning and Organizing")

        files = {
            "file": ("business_management_syllabus.pdf", pdf_bytes, "application/pdf")
        }
        data = {"syllabus_id": "syl_upload_001"}

        resp = self.client.post("/api/v1/kie/syllabus/extract-file", files=files, data=data)
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertIn("subjects", result)
        self.assertGreaterEqual(len(result["subjects"]), 1)
        # Verify first subject has non-empty topics
        self.assertTrue(len(result["subjects"][0]["topics"]) >= 1)

    def test_multipart_file_upload_image(self):
        """Mode 4: Verify image upload handling (PNG)."""
        # Minimal 1x1 valid PNG bytes
        png_bytes = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=")

        files = {
            "file": ("scanned_zoology_syllabus.png", png_bytes, "image/png")
        }
        data = {"syllabus_id": "syl_img_001"}

        resp = self.client.post("/api/v1/kie/syllabus/extract-file", files=files, data=data)
        self.assertEqual(resp.status_code, 200)
        result = resp.json()
        self.assertIn("subjects", result)
        self.assertGreaterEqual(len(result["subjects"]), 1)

    def test_get_route_guidance(self):
        """Verify GET /api/v1/kie/syllabus/extract returns integration guidance."""
        resp = self.client.get("/api/v1/kie/syllabus/extract")
        self.assertEqual(resp.status_code, 200)
        info = resp.json()
        self.assertEqual(info["status"], "ready")
        self.assertIn("endpoints", info)
        self.assertIn("json_payload", info["endpoints"])
        self.assertIn("multipart_file_upload", info["endpoints"])
        self.assertIn("response_contract", info)


if __name__ == "__main__":
    unittest.main()
