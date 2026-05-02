from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient


class UserApiTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(
            username="user-api",
            password="pass123456",
            email="user@example.com",
        )

    def test_user_me_requires_auth(self):
        response = self.client_api.get("/api/users/me/")
        self.assertEqual(response.status_code, 401)

    def test_user_me_get_and_patch(self):
        self.client_api.force_authenticate(self.user)

        get_response = self.client_api.get("/api/users/me/")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["username"], "user-api")

        patch_response = self.client_api.patch(
            "/api/users/me/",
            {"first_name": "Ivan", "last_name": "Petrov"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.json()["first_name"], "Ivan")
        self.assertEqual(patch_response.json()["last_name"], "Petrov")

    def test_change_password_requires_correct_old_password(self):
        self.client_api.force_authenticate(self.user)
        response = self.client_api.post(
            "/api/users/change-password/",
            {"old_password": "bad-pass", "new_password": "newpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("old_password", response.json())

    def test_change_password_success(self):
        self.client_api.force_authenticate(self.user)
        response = self.client_api.post(
            "/api/users/change-password/",
            {"old_password": "pass123456", "new_password": "newpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["detail"], "Password changed")

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))
