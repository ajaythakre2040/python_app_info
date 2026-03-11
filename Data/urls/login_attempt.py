from django.urls import path
from ..views.login_attempt import UnblockUserAPIView

urlpatterns = [
    path("admin/unblock-user/", UnblockUserAPIView.as_view(), name="unblock-user"),
]