"""
URL configuration for app_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.http import JsonResponse
from django.urls import path, include
from data.views.index import home 
from django.contrib import admin

def test_view(request):
    return JsonResponse({"message": "Test successful!"})

def home_view(request):
    return JsonResponse({"message": "Welcome to My Django Project!"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('data.urls')),
    path('test/', test_view),  # Ye test endpoint hai
    path("", home, name="home"),
]
