from django.urls import path
from ..views.unblock_user import UnblockUserAPIView

urlpatterns = [
    path("admin/unblock-user/", UnblockUserAPIView.as_view(), name="unblock-user"),
]