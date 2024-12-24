from django.urls import path, include
from django.contrib import admin
from . import views


urlpatterns = [
    path("",views.home, name='home'),
    path("index",views.home, name='home'),
    path("explore", views.explore, name='explore'),
    path("contactus", views.contactus, name='contactus'),
]