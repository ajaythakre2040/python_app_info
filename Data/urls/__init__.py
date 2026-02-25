from .auth_urls import urlpatterns as auth_data_urls
from .domain_data import urlpatterns as domain_data_urls
from .data_app import urlpatterns as data_app_urls
from .user import urlpatterns as user_urls

urlpatterns = (auth_data_urls + domain_data_urls + data_app_urls + user_urls)