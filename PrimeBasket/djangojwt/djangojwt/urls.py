
from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from myapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register/',RegisterView.as_view(),name="auth_register"),
    path('api/auth/login/',LoginView.as_view(),name="auth_login"),
    path('api/dashboard/',DashboardView.as_view(),name="dashboard"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/reset-password/', ResetPasswordView.as_view(), name='auth_reset_password'),
    path('api/shop/', include('shop.urls')),
]
