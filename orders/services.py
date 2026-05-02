from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction

from orders.cart import clear_cart, get_cart
from orders.models import Order, OrderItem
from products.models import Product


class CheckoutError(Exception):
    pass


def _send_checkout_notifications(order: Order) -> None:
    subject = f"Order #{order.id} created"
    body = (
        f"Order #{order.id} was created.\n"
        f"User: {order.user.username}\n"
        f"Total: {order.total_price}\n"
        f"Address: {order.shipping_address}\n"
    )

    recipients: list[str] = []
    if order.user.email:
        recipients.append(order.user.email)
    admin_email = getattr(settings, "ORDER_ADMIN_EMAIL", "admin@example.com")
    if admin_email:
        recipients.append(admin_email)

    if recipients:
        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@myshop.local"),
            recipient_list=recipients,
            fail_silently=True,
        )


@transaction.atomic
def create_order_from_session_cart(*, user: User, session: dict, shipping_address: str) -> Order:
    cart = get_cart(session)
    if not cart:
        raise CheckoutError("Cart is empty")

    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.select_for_update().filter(id__in=product_ids, is_active=True)
    by_id = {p.id: p for p in products}

    order = Order.objects.create(user=user, shipping_address=shipping_address)
    total = Decimal("0.00")

    for pid, qty in cart.items():
        product = by_id.get(int(pid))
        if not product:
            raise CheckoutError(f"Product {pid} not found")
        if qty > product.stock:
            raise CheckoutError(f"Insufficient stock for {product.name}")

        product.stock -= qty
        product.popularity += qty
        product.save(update_fields=["stock", "popularity", "updated_at"])

        OrderItem.objects.create(order=order, product=product, quantity=qty, price=product.price)
        total += product.price * qty

    order.total_price = total
    order.save(update_fields=["total_price"])
    clear_cart(session)
    _send_checkout_notifications(order)
    return order