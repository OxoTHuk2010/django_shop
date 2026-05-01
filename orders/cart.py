from decimal import Decimal
from typing import Any

from products.models import Product

CART_SESSION_KEY = "cart"


def get_cart(session: dict[str, Any]) -> dict[str, int]:
    return session.get(CART_SESSION_KEY, {})


def save_cart(session: dict[str, Any], cart: dict[str, int]) -> None:
    session[CART_SESSION_KEY] = cart
    session.modified = True


def add_to_cart(session: dict[str, Any], product_id: int, quantity: int) -> None:
    cart = get_cart(session)
    key = str(product_id)
    cart[key] = max(1, cart.get(key, 0) + quantity)
    save_cart(session, cart)


def update_cart_item(session: dict[str, Any], product_id: int, quantity: int) -> None:
    cart = get_cart(session)
    key = str(product_id)
    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity
    save_cart(session, cart)


def clear_cart(session: dict[str, Any]) -> None:
    save_cart(session, {})


def cart_snapshot(session: dict[str, Any]) -> dict[str, Any]:
    cart = get_cart(session)
    product_ids = [int(pid) for pid in cart.keys()]
    products = Product.objects.filter(id__in=product_ids, is_active=True)
    by_id = {p.id: p for p in products}

    items: list[dict[str, Any]] = []
    total = Decimal("0.00")
    for pid, quantity in cart.items():
        product = by_id.get(int(pid))
        if not product:
            continue
        subtotal = product.price * quantity
        total += subtotal
        items.append(
            {
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": quantity,
                "stock": product.stock,
                "subtotal": subtotal,
            }
        )

    return {"items": items, "total": total}