from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CartAPIView, OrderViewSet, ProductReviewView, ProductViewSet, UserRegisterAPIView

router = DefaultRouter()
router.register("products", ProductViewSet, basename="api-products")
router.register("orders", OrderViewSet, basename="api-orders")

urlpatterns = [
    path("", include(router.urls)),
    path("users/register/", UserRegisterAPIView.as_view(), name="api-user-register"),
    path("cart/", CartAPIView.as_view(), name="api-cart"),
    path("products/<int:product_id>/reviews/", ProductReviewView.as_view(), name="api-product-reviews"),
]