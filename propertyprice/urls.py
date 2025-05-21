from django.contrib import admin
#from updateData.admin import updatesite
from django.urls import path , include
#from updateData.views import update 



urlpatterns = [
    path('/admin/updateData/propertymodel/',include("updateData.urls"), name='updateData'),
    path('',include("explore.urls"), name= 'explore'),
    path('admin/', admin.site.urls),
    ]


