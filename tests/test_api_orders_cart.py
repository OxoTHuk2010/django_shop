from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from orders.cart import add_to_cart
from orders.models import Order
from products.models import Category, Product


class CartApiTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.category = Category.objects.create(name="Cart API", slug="cart-api")
        self.product = Product.objects.create(
            name="Cart Product",
            slug="cart-product",
            description="cart product description",
            price="11.00",
            category=self.category,
            stock=7,
        )

    def test_add_update_remove_cart_item(self):
        add_response = self.client_api.post("/api/cart/", {"product_id": self.product.id, "quantity": 2}, format="json")
        self.assertEqual(add_response.status_code, 201)
        self.assertEqual(add_response.json()["items"][0]["quantity"], 2)

        patch_response = self.client_api.patch(
            "/api/cart/", {"product_id": self.product.id, "quantity": 3}, format="json"
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.json()["items"][0]["quantity"], 3)

        delete_response = self.client_api.delete(f"/api/cart/?product_id={self.product.id}")
        self.assertEqual(delete_response.status_code, 204)

        get_response = self.client_api.get("/api/cart/")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["items"], [])

    def test_delete_cart_with_invalid_product_id_returns_400(self):
        response = self.client_api.delete("/api/cart/?product_id=abc")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "product_id must be integer")


class OrdersApiTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username="order-user", password="pass123456")
        self.other_user = User.objects.create_user(username="other-user", password="pass123456")
        self.category = Category.objects.create(name="Order API", slug="order-api")
        self.product = Product.objects.create(
            name="Order Product",
            slug="order-product",
            description="order product description",
            price="9.50",
            category=self.category,
            stock=4,
        )

    def test_order_create_requires_authentication(self):
        response = self.client_api.post("/api/orders/", {"shipping_address": "Main st 1"}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_order_create_fails_when_cart_empty(self):
        self.client_api.force_authenticate(self.user)
        response = self.client_api.post("/api/orders/", {"shipping_address": "Main st 1"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Cart is empty")

    def test_order_create_from_cart_and_cancel(self):
        self.client_api.force_authenticate(self.user)
        session = self.client_api.session
        add_to_cart(session, self.product.id, 2)
        session.save()

        create_response = self.client_api.post("/api/orders/", {"shipping_address": "Main st 1"}, format="json")
        self.assertEqual(create_response.status_code, 201)
        order_id = create_response.json()["id"]
        self.assertEqual(create_response.json()["status"], Order.Status.PENDING)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

        cancel_response = self.client_api.post(f"/api/orders/{order_id}/cancel/")
        self.assertEqual(cancel_response.status_code, 200)
        self.assertEqual(cancel_response.json()["status"], Order.Status.CANCELLED)

    def test_user_cannot_cancel_foreign_order(self):
        foreign_order = Order.objects.create(user=self.other_user, shipping_address="X", total_price="1.00")
        self.client_api.force_authenticate(self.user)
        response = self.client_api.post(f"/api/orders/{foreign_order.id}/cancel/")
        self.assertEqual(response.status_code, 404)
