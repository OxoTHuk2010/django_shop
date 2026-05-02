from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase, override_settings

from products.models import Category, Product


class WebAuthFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="web-user", password="pass123456")

    def test_login_with_next_redirects_back(self):
        response = self.client.post(
            "/account/login/?next=/cart/",
            {"username": "web-user", "password": "pass123456"},
        )
        self.assertRedirects(response, "/cart/")

    def test_logout_requires_post(self):
        self.client.login(username="web-user", password="pass123456")
        response = self.client.get("/account/logout/")
        self.assertEqual(response.status_code, 405)

    def test_logout_post_returns_to_catalog(self):
        self.client.login(username="web-user", password="pass123456")
        response = self.client.post("/account/logout/")
        self.assertRedirects(response, "/")


class CatalogPaginationTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="UX Catalog", slug="ux-catalog")
        for idx in range(30):
            Product.objects.create(
                name=f"UX Product {idx}",
                slug=f"ux-product-{idx}",
                description="ux catalog item",
                price="5.00",
                category=self.category,
                stock=3,
            )

    def test_catalog_supports_per_page_and_preserves_filters(self):
        response = self.client.get("/?q=UX&sort=price&per_page=24")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["products"]), 24)
        self.assertContains(response, "per_page=24")
        self.assertContains(response, "sort=price")

    def test_catalog_invalid_query_params_fallback(self):
        response = self.client.get("/?min_price=bad&max_price=also-bad&per_page=999&page=bad")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["current_per_page"], 12)


class EnsureAdminUserCommandTests(TestCase):
    @override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
    def test_ensure_admin_user_from_environment(self):
        with self.settings():
            import os

            os.environ["DJANGO_SUPERUSER_USERNAME"] = "admin-check"
            os.environ["DJANGO_SUPERUSER_EMAIL"] = "admin@example.com"
            os.environ["DJANGO_SUPERUSER_PASSWORD"] = "adminpass123"
            try:
                call_command("ensure_admin_user")
            finally:
                os.environ.pop("DJANGO_SUPERUSER_USERNAME", None)
                os.environ.pop("DJANGO_SUPERUSER_EMAIL", None)
                os.environ.pop("DJANGO_SUPERUSER_PASSWORD", None)

        user = User.objects.get(username="admin-check")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("adminpass123"))
