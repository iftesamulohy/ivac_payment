from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # Render the login form
    path('api/login/', views.api_login, name='api_login'),  # API for login
    path('api/submit_otp/', views.submit_otp_api, name='api_submit_otp'),  # API for OTP submission
    path('add_payment_info/', views.add_payment_info, name='add_payment_info'),
]
