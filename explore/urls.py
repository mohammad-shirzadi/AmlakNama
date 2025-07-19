from django.urls import path
from . import views


urlpatterns = [
    path("",views.homeAPI.as_view(), name='home'),
    path("index",views.homeAPI.as_view(), name='home'),
    path("explore", views.exploreAPI.as_view(), name='explore'),
    path("contactus", views.contactusAPI.as_view(), name='contactus'),
]