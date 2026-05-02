from django.contrib.auth.models import User
from rest_framework import serializers

from orders.cart import cart_snapshot
from orders.models import Order, OrderItem
from products.models import Product
from reviews.models import Review


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name")


class UserPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, min_length=8)
    new_password = serializers.CharField(write_only=True, min_length=8)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "slug", "description", "price", "stock", "category_id")


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "product", "user", "rating", "comment", "created_at")
        read_only_fields = ("user",)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ("product", "product_name", "quantity", "price")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "status", "total_price", "shipping_address", "created_at", "items")
        read_only_fields = ("status", "total_price", "created_at")


class CartItemInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class CartSnapshotSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.DictField())
    total = serializers.DecimalField(max_digits=10, decimal_places=2)

    @staticmethod
    def from_session(session):
        return cart_snapshot(session)
