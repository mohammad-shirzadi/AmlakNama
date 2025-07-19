from django.contrib import admin
from updateData.models import propertyModel

from .services import makeshape

class propertyModelAdmin(admin.ModelAdmin):
    list_display = ["case_id","landuse","ptype", 
                    "area", "price",'mortgage', 
                    'rent', "mahale", "date_time",'lat','lon']
    
    search_fields = ["case_id","landuse","ptype", 
                     "area", "price",'mortgage', 
                     'rent', "mahale","exp", 
                     "date_time",'lat','lon']
    
    list_filter = ["landuse","ptype", "date_time"]

    actions = [makeshape]


admin.site.register(propertyModel,propertyModelAdmin)
