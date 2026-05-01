from django.urls import path

from .views import AddToCartView, CartUpdateView, CartView, CheckoutView

urlpatterns = [
    path("cart/", CartView.as_view(), name="cart"),
    path("cart/add/<int:product_id>/", AddToCartView.as_view(), name="add-to-cart"),
    path("cart/update/<int:product_id>/", CartUpdateView.as_view(), name="cart-update"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
]