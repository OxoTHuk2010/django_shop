from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal, InvalidOperation

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from orders.models import OrderItem
from reviews.models import Review

from .forms import ReviewForm
from .models import Category, Product


class ProductListView(ListView):
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12
    per_page_options = (12, 24, 48)

    def get_paginate_by(self, queryset):
        try:
            per_page = int(self.request.GET.get("per_page", self.paginate_by))
        except (TypeError, ValueError):
            return self.paginate_by
        if per_page not in self.per_page_options:
            return self.paginate_by
        return per_page

    def paginate_queryset(self, queryset, page_size):
        paginator = Paginator(queryset, page_size)
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1

        try:
            page_number = paginator.num_pages if page == "last" else int(page)
            page_obj = paginator.page(page_number)
        except (PageNotAnInteger, ValueError):
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return paginator, page_obj, page_obj.object_list, page_obj.has_other_pages()

    @staticmethod
    def _decimal_param(value):
        if not value:
            return None
        try:
            return Decimal(value)
        except (InvalidOperation, TypeError, ValueError):
            return None

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related("category")
        q = self.request.GET.get("q")
        category = self.request.GET.get("category")
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        sort = self.request.GET.get("sort")

        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if category:
            queryset = queryset.filter(category__slug=category)
        min_price_value = self._decimal_param(min_price)
        max_price_value = self._decimal_param(max_price)
        if min_price_value is not None:
            queryset = queryset.filter(price__gte=min_price_value)
        if max_price_value is not None:
            queryset = queryset.filter(price__lte=max_price_value)

        if sort == "price":
            queryset = queryset.order_by("price")
        elif sort == "-price":
            queryset = queryset.order_by("-price")
        elif sort == "popular":
            queryset = queryset.order_by("-popularity")
        elif sort == "new":
            queryset = queryset.order_by("-created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset.annotate(avg_rating=Avg("reviews__rating"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        preserved = self.request.GET.copy()
        preserved.pop("page", None)
        context["categories"] = Category.objects.order_by("name")
        context["per_page_options"] = self.per_page_options
        context["current_per_page"] = self.get_paginate_by(self.object_list)
        context["querystring_without_page"] = preserved.urlencode()
        return context


class ProductDetailView(DetailView):
    model = Product
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["review_form"] = ReviewForm()
        context["reviews"] = self.object.reviews.select_related("user").order_by("-created_at")
        return context


class ProductReviewCreateView(LoginRequiredMixin, View):
    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        has_purchased = OrderItem.objects.filter(order__user=request.user, product=product).exists()
        if not has_purchased:
            messages.error(request, "You can review only products that you purchased.")
            return redirect(product.get_absolute_url())

        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={
                    "rating": form.cleaned_data["rating"],
                    "comment": form.cleaned_data["comment"],
                },
            )
            messages.success(request, "Review saved")
        else:
            messages.error(request, "Invalid review data")
        return redirect(product.get_absolute_url())


class GuidesRecipesView(TemplateView):
    template_name = "products/guides_recipes.html"


class CustomAdminProductsView(TemplateView):
    template_name = "shop_admin/products.html"


class CustomAdminAddView(TemplateView):
    template_name = "shop_admin/add.html"
