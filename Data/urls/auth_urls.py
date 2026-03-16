from django.urls import path
from data.views.auth_system import RegisterAPIView, LoginAPIView,LogoutAPIView,ForceLogoutAPIView,ChangePasswordAPIView,ResetPasswordAPIView

urlpatterns = [
    path('register/user/', RegisterAPIView.as_view(), name='user-register'),
    path('login/user/', LoginAPIView.as_view(), name = 'user-login'),
    path('logout/user/', LogoutAPIView.as_view(), name = 'user-logout'),
    path("force-logout/user/", ForceLogoutAPIView.as_view(), name="force-logout"),
    path('change-password/user/', ChangePasswordAPIView.as_view(), name = 'user-changepassword'),
    path('reset-password/user/', ResetPasswordAPIView.as_view(), name = 'user-resetpassword'),
]
