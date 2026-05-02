from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.test.utils import override_settings
from rest_framework.test import APIClient

from orders.cart import add_to_cart
from orders.models import Order, OrderItem
from orders.services import CheckoutError, create_order_from_session_cart
from products.models import Category, Product
from reviews.models import Review


class CheckoutServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="buyer", password="pass123456")
        self.category = Category.objects.create(name="Hops Test", slug="hops-test")
        self.product = Product.objects.create(
            name="Citra Test",
            slug="citra-test",
            description="desc",
            price="5.00",
            category=self.category,
            stock=3,
        )

    def test_checkout_reduces_stock_and_creates_order(self):
        session = self.client.session
        add_to_cart(session, self.product.id, 2)
        order = create_order_from_session_cart(
            user=self.user, session=session, shipping_address="Main street 1"
        )
        self.product.refresh_from_db()
        self.assertEqual(order.total_price, self.product.price * 2)
        self.assertEqual(self.product.stock, 1)

    def test_checkout_fails_on_insufficient_stock(self):
        session = self.client.session
        add_to_cart(session, self.product.id, 10)
        with self.assertRaises(CheckoutError):
            create_order_from_session_cart(user=self.user, session=session, shipping_address="Main")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_checkout_sends_email_notifications(self):
        self.user.email = "buyer@example.com"
        self.user.save(update_fields=["email"])
        session = self.client.session
        add_to_cart(session, self.product.id, 1)
        create_order_from_session_cart(user=self.user, session=session, shipping_address="Main street 1")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Order #", mail.outbox[0].subject)


class ReviewConstraintTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reviewer", password="pass123456")
        self.category = Category.objects.create(name="Malts Test", slug="malts-test")
        self.product = Product.objects.create(
            name="Malt Test",
            slug="malt-test",
            description="desc",
            price="3.00",
            category=self.category,
            stock=10,
        )

    def test_review_requires_purchase(self):
        self.client.login(username="reviewer", password="pass123456")
        response = self.client.post(
            reverse("product-review-create", kwargs={"slug": self.product.slug}),
            {"rating": 5, "comment": "Great"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)

    def test_review_after_purchase_allowed(self):
        order = Order.objects.create(user=self.user, shipping_address="A", total_price="3.00")
        OrderItem.objects.create(order=order, product=self.product, quantity=1, price="3.00")
        self.client.login(username="reviewer", password="pass123456")
        self.client.post(
            reverse("product-review-create", kwargs={"slug": self.product.slug}),
            {"rating": 4, "comment": "Nice"},
        )
        self.assertEqual(Review.objects.count(), 1)


class ApiOwnershipTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user1 = User.objects.create_user(username="u1", password="pass123456")
        self.user2 = User.objects.create_user(username="u2", password="pass123456")
        self.order = Order.objects.create(user=self.user1, shipping_address="Addr", total_price="1.00")

    def test_user_sees_only_own_orders(self):
        self.client_api.force_authenticate(self.user2)
        response = self.client_api.get("/api/orders/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 0)
