from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from products.models import Product

from .cart import add_to_cart, cart_snapshot, update_cart_item
from .forms import CheckoutForm
from .services import CheckoutError, create_order_from_session_cart


class CartView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "orders/cart.html", cart_snapshot(request.session))


class AddToCartView(View):
    def post(self, request: HttpRequest, product_id: int) -> HttpResponse:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        quantity = max(1, int(request.POST.get("quantity", 1)))
        if quantity > product.stock:
            messages.error(request, "Requested quantity exceeds stock")
            return redirect(product.get_absolute_url())
        add_to_cart(request.session, product_id, quantity)
        messages.success(request, "Product added to cart")
        return redirect("cart")


class CartUpdateView(View):
    def post(self, request: HttpRequest, product_id: int) -> HttpResponse:
        quantity = int(request.POST.get("quantity", 1))
        update_cart_item(request.session, product_id, quantity)
        return redirect("cart")


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = cart_snapshot(request.session)
        context["form"] = CheckoutForm()
        return render(request, "orders/checkout.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            context = cart_snapshot(request.session)
            context["form"] = form
            return render(request, "orders/checkout.html", context)
        try:
            order = create_order_from_session_cart(
                user=request.user,
                session=request.session,
                shipping_address=form.cleaned_data["shipping_address"],
            )
        except CheckoutError as exc:
            messages.error(request, str(exc))
            return redirect("checkout")

        messages.success(request, f"Order #{order.id} created")
        return redirect("account")