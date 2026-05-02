from django.contrib.auth.models import User
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.cart import add_to_cart, update_cart_item
from orders.models import Order
from orders.services import CheckoutError, create_order_from_session_cart
from products.models import Product
from reviews.models import Review

from .permissions import IsOwnerOrReadOnly
from .serializers import (
    CartItemInputSerializer,
    CartSnapshotSerializer,
    OrderSerializer,
    ProductSerializer,
    ReviewSerializer,
    UserRegisterSerializer,
)


class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.none()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related("category").order_by("-created_at")
    serializer_class = ProductSerializer
    filterset_fields = ("category",)
    search_fields = ("name", "description")
    ordering_fields = ("price", "popularity", "created_at")


@extend_schema_view(
    create=extend_schema(
        summary="Create order from session cart",
        request=inline_serializer(
            name="CreateOrderRequest",
            fields={"shipping_address": serializers.CharField()},
        ),
        examples=[
            OpenApiExample(
                "Create order request",
                value={"shipping_address": "Main street 1"},
                request_only=True,
            ),
            OpenApiExample(
                "Empty cart error",
                value={"detail": "Cart is empty"},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    ),
    cancel=extend_schema(
        summary="Cancel own order",
        responses={200: OrderSerializer, 400: OpenApiResponse(description="Order cannot be cancelled")},
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user).prefetch_related("items").order_by("-created_at")

    def create(self, request, *args, **kwargs):
        shipping_address = request.data.get("shipping_address", "")
        if not shipping_address:
            return Response({"shipping_address": ["This field is required."]}, status=400)
        try:
            order = create_order_from_session_cart(
                user=request.user, session=request.session, shipping_address=shipping_address
            )
        except CheckoutError as exc:
            return Response({"detail": str(exc)}, status=400)
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status not in {Order.Status.PENDING, Order.Status.PAID}:
            return Response({"detail": "Order cannot be cancelled"}, status=400)
        order.status = Order.Status.CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(order).data)


@extend_schema_view(
    get=extend_schema(summary="List reviews for product"),
    post=extend_schema(
        summary="Create review after purchase",
        examples=[
            OpenApiExample(
                "Review payload",
                value={"rating": 5, "comment": "Excellent"},
                request_only=True,
            ),
            OpenApiExample(
                "Purchase required error",
                value={"detail": "Purchase required before review"},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    ),
)
class ProductReviewView(APIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, product_id: int):
        queryset = Review.objects.filter(product_id=product_id).select_related("user")
        return Response(ReviewSerializer(queryset, many=True).data)

    def post(self, request, product_id: int):
        serializer = ReviewSerializer(data={**request.data, "product": product_id})
        serializer.is_valid(raise_exception=True)
        if not Order.objects.filter(user=request.user, items__product_id=product_id).exists():
            return Response({"detail": "Purchase required before review"}, status=400)
        review, created = Review.objects.update_or_create(
            product_id=product_id,
            user=request.user,
            defaults={
                "rating": serializer.validated_data["rating"],
                "comment": serializer.validated_data["comment"],
            },
        )
        response_serializer = ReviewSerializer(review)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


@extend_schema_view(
    get=extend_schema(summary="Get cart snapshot"),
    post=extend_schema(
        summary="Add item to cart",
        examples=[
            OpenApiExample(
                "Add item payload",
                value={"product_id": 1, "quantity": 2},
                request_only=True,
            )
        ],
    ),
    patch=extend_schema(summary="Update cart item quantity"),
    delete=extend_schema(
        summary="Remove item from cart",
        examples=[
            OpenApiExample(
                "Missing product_id",
                value={"detail": "product_id is required"},
                response_only=True,
                status_codes=["400"],
            ),
            OpenApiExample(
                "Invalid product_id",
                value={"detail": "product_id must be integer"},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    ),
)
class CartAPIView(APIView):
    serializer_class = CartItemInputSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(CartSnapshotSerializer.from_session(request.session))

    def post(self, request):
        serializer = CartItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        add_to_cart(request.session, serializer.validated_data["product_id"], serializer.validated_data["quantity"])
        return Response(CartSnapshotSerializer.from_session(request.session), status=status.HTTP_201_CREATED)

    def patch(self, request):
        serializer = CartItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_cart_item(
            request.session, serializer.validated_data["product_id"], serializer.validated_data["quantity"]
        )
        return Response(CartSnapshotSerializer.from_session(request.session))

    def delete(self, request):
        product_id = request.query_params.get("product_id")
        if not product_id:
            return Response({"detail": "product_id is required"}, status=400)
        try:
            parsed_product_id = int(product_id)
        except (TypeError, ValueError):
            return Response({"detail": "product_id must be integer"}, status=400)
        update_cart_item(request.session, parsed_product_id, 0)
        return Response(status=status.HTTP_204_NO_CONTENT)
