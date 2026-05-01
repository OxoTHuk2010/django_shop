from django.urls import path

from .views import (
    CustomAdminAddView,
    CustomAdminProductsView,
    GuidesRecipesView,
    ProductDetailView,
    ProductListView,
    ProductReviewCreateView,
)

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("products/", ProductListView.as_view(), name="products"),
    path("guides-recipes/", GuidesRecipesView.as_view(), name="guides-recipes"),
    path("shop-admin/products/", CustomAdminProductsView.as_view(), name="custom-admin-products"),
    path("shop-admin/add/", CustomAdminAddView.as_view(), name="custom-admin-add"),
    path("product/<slug:slug>/", ProductDetailView.as_view(), name="product-detail"),
    path("product/<slug:slug>/review/", ProductReviewCreateView.as_view(), name="product-review-create"),
]
