from django.urls import path
from ..views.cron_domain import CronDomainStatusAPIView,ActiveDomainCronAPIView,DeactiveDomainCronAPIView

urlpatterns = [
    path('cron/check-domains/', CronDomainStatusAPIView.as_view()),
    path('cron/active-domains/', ActiveDomainCronAPIView.as_view()),
    path('cron/deactive-domains/', DeactiveDomainCronAPIView.as_view()),
]