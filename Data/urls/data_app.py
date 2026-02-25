from django.urls import path 
from ..views.data_app import AppDataAPIView

urlpatterns = [
    path('app-data/', AppDataAPIView.as_view(), name='app-data'),
    path('app-data/<int:id>/',AppDataAPIView.as_view(), name='app-data-detail'),
]
