from django.contrib.auth import views as auth_views
from django.urls import path

from .views import AccountView, ForgotPasswordView, RegisterView

urlpatterns = [
    path("account/register/", RegisterView.as_view(), name="register"),
    path("account/login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),
    path("account/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("account/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("account/", AccountView.as_view(), name="account"),
]