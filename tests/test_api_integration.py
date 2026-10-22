import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_pages_render_html(self):
        for route in ["/", "/host", "/play"]:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200)
            self.assertIn("text/html", res.headers["content-type"])
            self.assertIn("Zoho Recruit", res.text)

    def test_network_ip_endpoint(self):
        res = self.client.get("/api/network-ip")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("ip", data)
        self.assertIn("port", data)
        self.assertIn("join_url", data)

    def test_registration_and_export_flow(self):
        reg_payload = {
            "room_code": "ZR_INT_TEST",
            "full_name": "Valentina Martinez",
            "email": "valentina@cun.edu.co",
            "role_or_area": "Coordinadora de Seleccion",
            "nickname": "ValenRecruit",
            "avatar": "quantum_ai"
        }
        res = self.client.post("/api/register", json=reg_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("player_id", data)

        # Test export CSV
        export_res = self.client.get("/api/session/ZR_INT_TEST/export")
        self.assertEqual(export_res.status_code, 200)
        self.assertIn("text/csv", export_res.headers["content-type"])
        self.assertIn("Valentina Martinez", export_res.text)

if __name__ == "__main__":
    unittest.main()
