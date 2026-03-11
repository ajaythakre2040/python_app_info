from .auth_urls import urlpatterns as auth_data_urls
from .domain_data import urlpatterns as domain_data_urls
from .data_app import urlpatterns as data_app_urls
from .user import urlpatterns as user_urls
from .cron_domain import urlpatterns as cron_domain_urls
from .login_attempt import urlpatterns as login_attempt_urls

urlpatterns = (auth_data_urls + domain_data_urls + data_app_urls + user_urls+ cron_domain_urls+ login_attempt_urls)