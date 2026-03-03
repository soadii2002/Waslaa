from django.urls import path
from waslaa_telecom.apps.users.views import RegisterView, LoginView, LogoutView, CustomerListView
from waslaa_telecom.apps.users.views import (
    RegisterView,
    LoginView,
    LogoutView,
    CustomerListView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]