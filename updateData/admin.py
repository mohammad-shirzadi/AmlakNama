from django.contrib import admin
from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from updateData.models import propertyModel
from explore.models import MTPPolygon
from django.contrib.admin import AdminSite
from django.http import HttpResponse
from updateData import views
#from updateData.models import pointshp


import geopandas
import shapely
import matplotlib.pyplot as plt
import datetime
import sqlite3


@admin.action(description='create shpfiles')
def makeshape(modeladmin, request, queryset):
    #deffine point
    def log(a):
        global LOG
        LOG = str(datetime.datetime.today())+ ':   ' + a + '\n'
        with open('log.txt', 'a') as logfile:
            logfile.write(LOG)
        return LOG

    def create_point(queryset):
        all_data = queryset
    
        case_id = []
        landuse = []
        ptype = []
        price = []
        area = []
        Cyear = []
        mortgage = []
        rent = [] 
        lat = []
        lon = []
        mahale = []
        exp = []
        link = []
        date_time = []
        points = []
        for data in all_data:
            case_id.append(data.case_id)
            landuse.append(data.landuse)
            ptype.append(data.ptype)
            price.append(data.price)
            area.append(data.area)
            Cyear.append(data.Cyear)
            mortgage.append(data.mortgage)
            rent.append(data.rent) 
            lat.append(data.lat)
            lon.append(data.lon)
            mahale.append(data.mahale)
            exp.append(data.exp)
            link.append(data.link)
            date_time.append(data.date_time)
            point = shapely.geometry.Point(data.lon,data.lat)
            points.append(point)
        ATable = {
            'caseid': case_id,
            'landuse': landuse,
            'ptype': ptype,
            'price': price,
            'area': area,
            'Cyear': Cyear,
            'mortgage' : mortgage,
            'rent' : rent,
            'lat' : lat,
            'lon' : lon,
            'mahale' : mahale,
            'exp' : exp,
            'link' : link,
            'date_time' : date_time
        }

        pointgdf = geopandas.GeoDataFrame(ATable, geometry = points, crs='EPSG:4326')

        pointgdf.to_crs(epsg =32639, inplace = True)
        pointgdf.to_file(r'updateData/shp/points.shp')
        return pointgdf
    
    def geoprocsseing(pointgdf):
        #deffine polygon
        mahalat = geopandas.read_file(r'updateData/shp/StaticShape/Mahalat_Tehran.shp')
        ## TODO Validate joined data and delete wrong featuresh
    
        joined = mahalat.sjoin(pointgdf)
        def f(x):
            try:
                if x.name in ['lat','lon','index_right','Shape_Le_1','Shape_Area']:
                    return None
                elif x.name == 'caseid':
                    return len(x)
                elif x.name in ['lu','typ']:
                    y = list(x)
                    return y[0]
                else:
                    return x.mean()
            except:
                return None  
        polymean = joined.dissolve(["NAME_MAHAL","landuse","ptype","reg_no"],f,False)
        polymean['FID']=range(0,len(polymean))
        polymean.set_index('FID',inplace=True)     
        polymean.to_file(r"updateData/shp/polymean.shp")
        gdf = geopandas.read_file(r'updateData/shp/polymean.shp')
        Fgdf = gdf.drop(['Shape_Le_1','Shape_Area','index_righ','caseid','area', 'Cyear','lat', 'lon', 'mahale', 'exp', 'link', 'date_time'],axis=1)
        Fgdf.to_file(r"updateData/shp/polymean.shp")
        log(r"updateData/shp/polymean.shp is Created")
        return polymean
    
    def Insert(verbose=True):
        MTP_mapping = {
            "name_mahal" : "NAME_MAHAL",
            "landuse" : "landuse",
            "ptype" : "ptype",
            "reg_no" : "reg_no",
            "price" : "price", 
            "mortgage" : "mortgage",
            "rent" : "rent",
            "geom" : 'MULTIPOLYGON',
        }
        MTP_shp = Path(__file__).resolve().parent.parent/"updateData"/"shp"/"polymean.shp"

        MTPPolygon.objects.all().delete()
        lm = LayerMapping(MTPPolygon,MTP_shp,MTP_mapping,transform=False)
        lm.save(strict=True, verbose=verbose)


    geoprocsseing(create_point(queryset))
    Insert()


class propertyModelAdmin(admin.ModelAdmin):
    list_display = ["case_id","landuse","ptype", "area", "price",'mortgage', 'rent', "mahale", "date_time"]
    search_fields = ["case_id","landuse","ptype", "area", "price",'mortgage', 'rent', "mahale","exp", "date_time"]
    list_filter = ["landuse","ptype", "date_time"]
    actions = [makeshape]
    #def get_urls(self):
    #    from django.urls import path
    #    urls = super().get_urls()
    #    urls += [path('admin/updateData/propertymodel/updatePg/', self.updatePg, name='update')]
    #    return urls
    #def updatePg(self, request):
    #    from django.http import HttpResponse
    #    return HttpResponse('This is a custom view in admin.')
#






admin.site.register(propertyModel,propertyModelAdmin)
