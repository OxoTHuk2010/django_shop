from django.contrib import admin
from django.db.models import Count, Sum

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_price", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    inlines = [OrderItemInline]

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        qs = self.get_queryset(request)
        extra_context["orders_count"] = qs.count()
        extra_context["total_revenue"] = qs.aggregate(revenue=Sum("total_price"))["revenue"] or 0
        extra_context["pending_orders"] = qs.filter(status=Order.Status.PENDING).count()
        extra_context["top_products"] = (
            OrderItem.objects.values("product__name").annotate(total_qty=Sum("quantity")).order_by("-total_qty")[:5]
        )
        extra_context["orders_by_status"] = qs.values("status").annotate(total=Count("id")).order_by("status")
        return super().changelist_view(request, extra_context=extra_context)