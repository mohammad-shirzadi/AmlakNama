from django.urls import path, include
from django.contrib import admin
from . import views


urlpatterns = [
    path("",views.homeAPI.as_view(), name='home'),
    path("index",views.homeAPI.as_view(), name='home'),
    path("explore", views.explore, name='explore'),
    path("contactus", views.contactus, name='contactus'),
]