from django.test import TestCase


class SmokeTests(TestCase):
    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_openapi_endpoints_available(self):
        schema_response = self.client.get("/api/schema/")
        self.assertEqual(schema_response.status_code, 200)
        self.assertIn("application/vnd.oai.openapi", schema_response["Content-Type"])

        docs_response = self.client.get("/api/docs/")
        self.assertEqual(docs_response.status_code, 200)

        redoc_response = self.client.get("/api/redoc/")
        self.assertEqual(redoc_response.status_code, 200)

    def test_openapi_schema_contains_core_paths(self):
        response = self.client.get("/api/schema/?format=json")
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        paths = schema.get("paths", {})

        self.assertIn("/api/products/", paths)
        self.assertIn("/api/orders/", paths)
        self.assertIn("/api/cart/", paths)
        self.assertIn("/api/token/", paths)
        self.assertIn("/api/token/refresh/", paths)
