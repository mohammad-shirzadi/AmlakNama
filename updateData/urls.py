from django.urls import path
from . import views

urlpatterns = [
    path("updatePg/",views.updatePg, name='update' ),
]