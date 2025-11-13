from django.core.management import BaseCommand
from updateData.models import propertyModel

import geopandas
import shapely


class Command(BaseCommand):    
    def handle(self,*args, **kwarg):
        all_data = propertyModel.objects.all()
        mahalat_tehran = geopandas.read_file(
            r'updateData/shp/StaticShape/Mahalat_Tehran.shp')

        case_id = []
        landuse = []
        property_type = []
        metric_price = []
        creation_year = []
        create_datetime = []
        points = []
        
        for data in all_data:
            case_id.append(data.case_id)
            landuse.append(data.landuse)
            property_type.append(data.ptype)
            metric_price.append(data.price)
            creation_year.append(data.Cyear)
            create_datetime.append(data.date_time)
            point = shapely.geometry.Point(data.lon,data.lat)
            points.append(point) 

        attribute_table = {
            'caseid': case_id, 'landuse': landuse, 'ptype': property_type,
            'mtrprice': metric_price,    'cyear': creation_year,
            'crdatetime' : create_datetime
        }

        pointgdf = geopandas.GeoDataFrame(
            attribute_table, geometry=points, crs='EPSG:4326')
        pointgdf.to_crs(epsg =32639, inplace = True)
        joined_point = mahalat_tehran.sjoin(pointgdf)
        joined_point.drop(["Shape_Le_1","Shape_Area"], inplace=True, axis=1)
        joined_point.set_index('caseid', inplace=True)
        joined_point.to_file(r"updateData/management/commands/shape_files/joined_poligon.shp")
        
#        landuses = ['res', 'resland', 'com']
#        typs = ['rent', 'buy']
#        reg_noms = range(1,23)
#        for lu in landuses:
#            for typ in typs:
#                for reg in reg_noms:
#                    if lu == 'resland' and typ == 'rent':
#                        continue
#                    joined_point.query(f"landuse == {lu} and ptype == {typ} and reg_no == {reg}")
#                    if joined_point.empty:
#                        continue
#
#