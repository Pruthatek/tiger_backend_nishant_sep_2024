# urls.py

from django.urls import path
from .views import *
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    # path('login/', UserLoginView.as_view(), name='login'),
    path('login/request-otp/', RequestOTPView.as_view(), name='request-otp'),
    path('login/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('users/', UserDetailView.as_view(), name='user-list'),
    path('roles/', RoleMasterListView.as_view(), name='role-list'),
    path('roles/<int:pk>/', RoleMasterDetailView.as_view(), name='role-detail'),
]
