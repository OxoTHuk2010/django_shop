from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from orders.models import Order


class JwtAuthApiTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username="jwt-user", password="pass123456")
        User.objects.create_user(username="jwt-other", password="pass123456")
        Order.objects.create(user=self.user, shipping_address="JWT st 1", total_price="10.00")

    def test_token_obtain_pair_returns_access_and_refresh(self):
        response = self.client_api.post(
            "/api/token/",
            {"username": "jwt-user", "password": "pass123456"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("access", payload)
        self.assertIn("refresh", payload)

    def test_token_refresh_returns_new_access(self):
        obtain = self.client_api.post(
            "/api/token/",
            {"username": "jwt-user", "password": "pass123456"},
            format="json",
        )
        refresh_token = obtain.json()["refresh"]
        response = self.client_api.post("/api/token/refresh/", {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_protected_endpoint_rejects_without_token(self):
        response = self.client_api.get("/api/orders/")
        self.assertEqual(response.status_code, 401)

    def test_protected_endpoint_allows_with_bearer_token(self):
        token_response = self.client_api.post(
            "/api/token/",
            {"username": "jwt-user", "password": "pass123456"},
            format="json",
        )
        access = token_response.json()["access"]
        self.client_api.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        response = self.client_api.get("/api/orders/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["results"][0]["shipping_address"], "JWT st 1")
