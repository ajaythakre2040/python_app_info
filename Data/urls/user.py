from django.urls import path
from ..views.user import UserAPIView

urlpatterns = [
    path('users/', UserAPIView.as_view(), name='user-list-create'),         
    path('users/<int:id>/', UserAPIView.as_view(), name='user-detail-update'),   
]