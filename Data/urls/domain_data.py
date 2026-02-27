from django.urls import path
from ..views.domain_data import TotalUserHistoryAPIView,ActiveUserListAPIView,DeactiveUserListAPIView

urlpatterns = [
    # total user history #
     path('users/total-history/', TotalUserHistoryAPIView.as_view(), name='total-user-history'),

     # active user history #
     path('users/active/', ActiveUserListAPIView.as_view(), name='active-user-history'),

     # deative user history #
     path('users/deactive/', DeactiveUserListAPIView.as_view(), name='deactive-user-history'),

]