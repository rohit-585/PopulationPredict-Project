"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from demoapp.views import*


urlpatterns = [
    path("neerajpk1/", admin.site.urls),
    path('', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('verify/<uidb64>/<token>/', verify_email, name='verify_email'),
    path('please-verify/', please_verify, name='please_verify'),
    path('predict-form/',form_view, name='predict_form'),
    path('predict/', predict_view, name='predict'),
    path('map/', data_map_view, name='map-view'),
    




    
]
