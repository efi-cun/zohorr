import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestApiEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_pages_render_html(self):
        for route in ["/", "/host", "/play", "/login", "/admin"]:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200)
            self.assertIn("text/html", res.headers["content-type"])

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

    def test_admin_auth_and_roles(self):
        """Tests login, role segregation, and dashboard access."""
        # Test invalid login
        bad_login = self.client.post("/api/auth/login", json={"username": "admin", "password": "wrongpassword"})
        self.assertEqual(bad_login.status_code, 401)

        # Test valid admin login
        admin_login = self.client.post("/api/auth/login", json={"username": "admin", "password": "AdminCun2026*"})
        self.assertEqual(admin_login.status_code, 200)
        admin_data = admin_login.json()
        self.assertTrue(admin_data["success"])
        self.assertEqual(admin_data["user"]["role"], "admin")
        admin_token = admin_data["token"]

        # Test valid facilitator login
        facil_login = self.client.post("/api/auth/login", json={"username": "facilitador", "password": "Facilitador2026*"})
        self.assertEqual(facil_login.status_code, 200)
        facil_data = facil_login.json()
        self.assertEqual(facil_data["user"]["role"], "facilitator")
        facil_token = facil_data["token"]

        # Admin can access user management
        admin_users_res = self.client.get("/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
        self.assertEqual(admin_users_res.status_code, 200)
        self.assertGreaterEqual(len(admin_users_res.json()), 2)

        # Facilitator is forbidden from managing users
        facil_users_res = self.client.get("/api/admin/users", headers={"Authorization": f"Bearer {facil_token}"})
        self.assertEqual(facil_users_res.status_code, 403)

        # Both can access topics and stats
        stats_res = self.client.get("/api/admin/stats", headers={"Authorization": f"Bearer {facil_token}"})
        self.assertEqual(stats_res.status_code, 200)
        self.assertIn("total_topics", stats_res.json())

if __name__ == "__main__":
    unittest.main()
