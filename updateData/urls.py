from django.urls import path
from . import views

urlpatterns = [
    path("updatePg/",views.updateData_API.as_view(), name='update' ),
    #path("updatePg/stop",views.stop_updatePg, name='stop_update')
]