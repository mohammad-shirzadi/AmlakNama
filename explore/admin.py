from django.contrib.gis import admin
from django.contrib import admin as normaladmin
from explore.models import MahalatTehran, MTPPolygon, masages

class MahalatTehranAdmin(admin.GISModelAdmin):
    list_display = ["name_mahal","reg_no"]

class MTPPolygonAdmin(admin.GISModelAdmin):
    list_display = ["landuse","ptype","name_mahal", "price", "reg_no"]

class massage(normaladmin.ModelAdmin):
    list_display = ["name","email","txtmasages"]

# Register your models here.
#admin.site.register(pointshp, admin.ModelAdmin)
admin.site.register(MahalatTehran, MahalatTehranAdmin)
admin.site.register(MTPPolygon, MTPPolygonAdmin)
normaladmin.site.register(masages,massage)


