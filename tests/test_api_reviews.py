from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from orders.models import Order, OrderItem
from products.models import Category, Product
from reviews.models import Review


class ProductReviewsApiTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username="review-api-user", password="pass123456")
        self.category = Category.objects.create(name="Review API", slug="review-api")
        self.product = Product.objects.create(
            name="Review Product",
            slug="review-product",
            description="review product description",
            price="12.00",
            category=self.category,
            stock=8,
        )

    def test_review_create_requires_authentication(self):
        response = self.client_api.post(
            f"/api/products/{self.product.id}/reviews/",
            {"rating": 5, "comment": "Great"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_review_create_requires_purchase(self):
        self.client_api.force_authenticate(self.user)
        response = self.client_api.post(
            f"/api/products/{self.product.id}/reviews/",
            {"rating": 5, "comment": "Great"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Purchase required before review")

    def test_review_rating_validation_bounds(self):
        self.client_api.force_authenticate(self.user)
        order = Order.objects.create(user=self.user, shipping_address="A", total_price="12.00")
        OrderItem.objects.create(order=order, product=self.product, quantity=1, price="12.00")

        low_rating = self.client_api.post(
            f"/api/products/{self.product.id}/reviews/",
            {"rating": 0, "comment": "Too low"},
            format="json",
        )
        self.assertEqual(low_rating.status_code, 400)
        self.assertIn("rating", low_rating.json())

        high_rating = self.client_api.post(
            f"/api/products/{self.product.id}/reviews/",
            {"rating": 6, "comment": "Too high"},
            format="json",
        )
        self.assertEqual(high_rating.status_code, 400)
        self.assertIn("rating", high_rating.json())

    def test_second_review_updates_existing_record(self):
        self.client_api.force_authenticate(self.user)
        order = Order.objects.create(user=self.user, shipping_address="A", total_price="12.00")
        OrderItem.objects.create(order=order, product=self.product, quantity=1, price="12.00")

        first = self.client_api.post(
            f"/api/products/{self.product.id}/reviews/",
            {"rating": 4, "comment": "Good"},
            format="json",
        )
        self.assertEqual(first.status_code, 201)
        self.assertEqual(Review.objects.count(), 1)

        second = self.client_api.post(
            f"/api/products/{self.product.id}/reviews/",
            {"rating": 5, "comment": "Excellent"},
            format="json",
        )
        self.assertEqual(second.status_code, 200)
        self.assertEqual(Review.objects.count(), 1)

        review = Review.objects.get(product=self.product, user=self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Excellent")

