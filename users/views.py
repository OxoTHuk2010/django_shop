from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView

from orders.models import Order

from .forms import ProfileForm


class RegisterView(FormView):
    form_class = UserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = "users/account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__product")
            .order_by("-created_at")
        )
        context["orders"] = orders
        context["orders_count"] = orders.count()
        context["orders_total"] = orders.aggregate(total=Sum("total_price"))["total"] or 0
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("account")

    def get_object(self, queryset=None):
        return self.request.user


class ForgotPasswordView(TemplateView):
    template_name = "users/forgot_password.html"