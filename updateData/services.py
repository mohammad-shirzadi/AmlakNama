from updateData.models import propertyModel
from django.contrib import admin
from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from explore.models import MTPPolygon
from django.utils import timezone

import logging
import os
import re
import requests
import time





DRIVER_BROWSER = os.environ.get('DRIVER_BROWSER',default='edge')
DRIVER_TIMEOUT = int(os.environ.get('DRIVER_TIMEOUT',default=30))
RETRY_SLEEP_TIME = int(os.environ.get('RETRY_SLEEP_TIME',default=10))
RETRY = int(os.environ.get('RETRY',default=3))
DRIVER = bool(os.environ.get('DRIVER', default=True))

GRAND_DICT = [
    {"landuse": "res",     "ptype": "buy",  "card_req_data": 'apartment-sell',  "update_status": "deactive"},
    {"landuse": "res",     "ptype": "rent", "card_req_data": 'apartment-rent',  "update_status": "deactive"},
    {"landuse": "resland", "ptype": "buy",  "card_req_data": 'plot-old',        "update_status": "deactive"},
    {"landuse": "com",     "ptype": "buy",  "card_req_data": 'commercial-sell', "update_status": "deactive"},
    {"landuse": "com",     "ptype": "rent", "card_req_data": 'commercial-rent', "update_status": "deactive"},
]


def dublecheck(retry=RETRY, retry_time_sleep=RETRY_SLEEP_TIME):
    def decorator(func):
        def wraper(self, *args, **kwargs):
            for i in range(retry):
                try:
                    time.sleep((retry_time_sleep)*(i))
                    result = func(self,*args,**kwargs)
                    return result
                except Exception as ex:
                    log(f"land-type: [{self.landuse}-{self.ptype}], error: {ex}, token: {self.token}")
                    if "429" not in str(ex):
                        break
            return False
        return wraper
    return decorator


class cards:
    def __init__(self,landuse, ptype) -> None:
        self.landuse = landuse
        self.ptype = ptype
        self.tokens_list = []
        self.cards_link = 'https://api.divar.ir/v8/postlist/w/search'
        for grand_dict in GRAND_DICT:
            if grand_dict["landuse"] == self.landuse and grand_dict["ptype"] == self.ptype:
                self.grdict = grand_dict
    
    @dublecheck()
    def get_tokens(self, token_num=24):
        url = self.cards_link
        loop_count = 0

        while len(self.tokens_list) <= token_num and loop_count <= 20:
            loop_count += 1
            self.data = {
                "city_ids": ["1"],
                "source_view": "CATEGORY",
                "disable_recommendation": False,
                "map_state": {
                    "camera_info": {
                    "bbox": {}
                    }
                },
                "search_data": {
                    "form_data": {"data": {"category": {"str": {"value": self.grdict['card_req_data']}}}},
                    "server_payload": {"@type": "type.googleapis.com/widgets.SearchData.ServerPayload",
                    "additional_form_data": {"data": {"sort": {"str": {"value": "sort_date"}}}}}
                }
                }
                  
            response = requests.post(url, json=self.data)
            if response.status_code != 200:
                log(f'get_tokens respondse.status_code: {response.status_code}')
                time.sleep(5)
                continue

            json_response = response.json()
            pagination_data = json_response['pagination']['data']
            self.data['pagination_data'] = pagination_data
            
            widgets = json_response["list_widgets"]
            #breakpoint()
            for widget in widgets:
                if ("data" in widget.keys() and "token" in widget['data'].keys()):
                    token = widget['data']['token']
                    property_token = Property(token, self.landuse, self.ptype)
                    if token not in self.tokens_list and not property_token.duplicate(propertyModel):
                        self.tokens_list.append(token)
                else:
                    raise Exception(f'The api response not incloud token and data.')
        result = len(self.tokens_list) if len(self.tokens_list) != 0 else None
        print(result)        
        return result

    def update(self, token_num=24):
        insert_counter = 0
        self.grdict['update_status'] = 'activated'
        log(f'land-type: [{self.landuse}-{self.ptype}], message: update cards is run.')

        if self.get_tokens(token_num) is None:
            raise Exception(f"land-type: [{self.landuse}-{self.ptype}], error: get_tokens not found.")

        for token in self.tokens_list:
            try:
                property_case = Property(token, self.landuse, self.ptype)

                if property_case.duplicate(propertyModel):
                    continue

                property_case.load('all')
                property_case.insert(propertyModel)
                insert_counter = insert_counter + 1
                log(f"land-type: [{self.landuse}-{self.ptype}], message: Valid inserted cases: {str(insert_counter)}, Total cases: {str(len(self.tokens_list))}.")

            except Exception as ex:
                log(f"land-type: [{self.landuse}-{self.ptype}], error: {str(ex)}, token: {token}")
                continue
                #raise Exception(str(ex)+property_case.property_link)

        self.grdict['update_status'] = 'deactivated'
        log(self.landuse + ', ' + self.ptype + ' UPDATED!')





class Property:
    def __init__(self, token:str, landuse:str, ptype:str):
        self.token:str = token
        self.landuse:str = landuse
        self.ptype:str = ptype
        self.property_link:str = f"https://divar.ir/v/{token}"

        self.map_section:dict = {}
        self.list_data_section:dict = {}
        self.lat = None
        self.lon = None
        self.Cyear:str = ''
        self.area:int = -1
        self.price:int = -1
        self.mortgage:int = -1
        self.rent:int = -1
        self.mahale:str = ''
        self.exp:str = ''
        self.date_time = None

    def __str__(self):
        return f"property case: {self.token}, landuse:{self.landuse}, ptype: {self.ptype}"
    
    def price_correction(self, price:str):
        if 'رایگان' in price:
            return 0
        for item in ['\u060C', '\u200f', 'تومان', ' ']:
            if item in price:
                price = price.replace(item, '').strip()
        res = int(price)       
        return res

    def is_valid(self) -> bool:
        validation = True
        if self.price in [0, -1]:
            validation = False
        if 0 < int(self.price) <= 99999:
            validation = False
        for price in [self.price, self.rent, self.mortgage]:
            if re.match('^1*$', str(price)):
                validation = False
            if str(price) in ['123456','1234567','12345678','123456789']:
                validation = False
        if validation is False:
            log(f"Api response not incloud valid price. price: {self.price} rent: {self.rent} mortgage: {self.mortgage}")    
        return validation

    @dublecheck()
    def get_property_data(self) -> bool|None:
        response = requests.get(f"https://api.divar.ir/v8/posts-v2/web/{self.token}")
        if response.status_code != 200:
            raise Exception(f"get_property_data respondse status_code: {response.status_code}") 
        
        json_response = response.json()
        if 'code' in json_response.keys() and 'message' in json_response.keys():
            if json_response["code"] == 5:
                raise Exception(f"This token is not valid or not found.")
            
        if 'analytics' in json_response.keys():
            analytics = json_response['analytics']
            if "industry-agriculture-business" in analytics['cat3']:
                raise Exception(f"This token is relate to industry-agriculture-business.")
                
        if 'sections' in json_response.keys():
            sections = json_response['sections']
            for section in sections:
                if section['section_name'] == 'LIST_DATA':
                    self.list_data_section = section

                elif section['section_name'] == 'MAP':
                    self.map_section = section
                
                elif section['section_name'] == 'TITLE':
                    self.title_section = section
            return True
        else:
            raise Exception(f"Api response not incloud property_data.")
           
    def get_loc(self) -> list[float] | None:
        if self.map_section:
            location = self.map_section['widgets'][0]['data']['location']
            if 'fuzzy_data' in location.keys():
                location_ = location['fuzzy_data']['point']
            elif 'exact_data' in location.keys():
                location_ = location['exact_data']['point']
            else:
                raise Exception(f'Unknown location type.')

            lat = float(location_['latitude'])
            long = float(location_['longitude'])
            self.lat = repr(lat)
            self.lon = repr(long)
        else:
            raise Exception(f"Api response not incloud map_section.") 

    def get_data(self) -> None:
        if self.list_data_section:
            widgets = self.list_data_section['widgets']
            for widget in widgets:
                if ('widget_type' in widget.keys() and widget['widget_type'] == 'GROUP_INFO_ROW'):
                    for item in widget['data']['items']:
                        if item['title'] == 'ساخت':
                            self.Cyear = item['value']
                        elif item['title'] == 'متراژ':
                            if ' متر' in item['value']:
                                item['value'] = item['value'].replace(' متر', '')
                            self.area = int(item['value'])
                
                elif('data' in widget.keys() and 'title' in widget['data'].keys() and 
                     widget['data']['title'] == 'متراژ'):
                    if ' متر' in widget['data']['value']:
                        widget['data']['value'] = widget['data']['value'].replace(' متر', '')
                    self.area = int(widget['data']['value'])

                elif ('widget_type' in widget.keys() and widget['widget_type'] == 'RENT_SLIDER'):
                    mortgage = widget['data']['credit']
                    mortgage = mortgage['value'] if 'value' in mortgage.keys() else str(0)
                    mortgage = self.price_correction(mortgage)
                    self.mortgage = int(mortgage)

                    rent = widget['data']['rent']
                    rent = rent['value'] if 'rent' in rent.keys() else str(0)
                    rent = self.price_correction(rent)
                    self.rent = int(rent)
                
                elif ('data' in widget.keys() and 'title' in widget['data'].keys() and 
                     widget['data']['title'] == 'ودیعه'):
                    mortgage = widget['data']['value']
                    mortgage = self.price_correction(mortgage)
                    self.mortgage = int(mortgage)

                elif ('data' in widget.keys() and 'title' in widget['data'].keys() and 
                     widget['data']['title'] == 'اجارهٔ ماهانه'):
                    rent = widget['data']['value']
                    rent = self.price_correction(rent)
                    self.rent = int(rent)

                elif ('data' in widget.keys() and 'title' in widget['data'].keys() and
                     widget['data']['title'] == 'قیمت هر متر'):
                    price = widget['data']['value']
                    price = self.price_correction(price)
                    self.price = int(price)
                    
            if self.mortgage != -1 and self.rent != -1 and self.area != -1:
                self.price = int(
                    (self.mortgage + (self.rent*30.0)) / int(self.area)
                    )
            if not self.is_valid():
                raise Exception(f"Api response not incloud valid price.")
        else:
            raise Exception(f"Api response not incloud list_data_section.")

    def get_exp(self):
        if self.title_section:
            widgets = self.title_section['widgets']
            for widget in widgets:
                if ('widget_type' in widget.keys() and
                     widget['widget_type'] == 'LEGEND_TITLE_ROW'):
                    self.exp = widget['data']['title']
                    title = widget['data']['subtitle']
                    mahale = title.split('،')[1]
                    self.mahale = mahale.strip()
        else:
            raise Exception(f'Api response not incloud the explain.')

    def get_output(self, only_defined:bool=False):
        self.is_valid()
        output = {
            'landuse': self.landuse, 'ptype' : self.ptype, 'price' : self.price,
            'area': self.area,         'Cyear': self.Cyear,     'mortgage': self.mortgage,
            'rent': self.rent,         'lat': self.lat,       'lon' : self.lon,
            'mahale': self.mahale,       'exp': self.exp,       'link' : self.property_link,
            'date_time' : self.date_time
        }
        if only_defined:
            defined_output = {}
            for key in output.keys():
                if (output[key] and output[key] != -1):
                    defined_output[key] = output[key]
            return defined_output
        return output

    def duplicate(self, propertyModel):
        duplicate = propertyModel.objects.filter(link__iendswith=self.token).exists()
        if duplicate:
            log(f"The {self.token} is duplicate.")
            return True
        else:
            return False


    def insert(self, propertyModel):
        try:
            if self.is_valid():
                propertyModel.objects.create(**self.get_output())
            else:
                raise Exception(f"Price is not valid.")
            
        except Exception as error:
            raise Exception(f'In insert step errore: {str(error)}-{str(self.get_output())}.')
    
    def load(self, field:list|str='all'):
        try:
            self.get_property_data()
            self.date_time = timezone.now()
            
            if field =='all' or 'loc' in field:
                self.get_loc()
                if not (self.lat or self.lon):
                    raise Exception(f'have no lat, long.')

            if field =='all' or 'price' in field:
                self.get_data()
                if not self.price:
                    raise Exception(f'have no price.')

            if field =='all' or 'other' in field:
                self.get_exp()
                    
        except Exception as error:
            raise Exception(f'{str(error)}')

    def delete(self):
        try:
            propertycase = propertyModel.objects.get(link__iendswith=self.token)
            propertycase.delete()
            log(f'case: \'{self.token}\' is deleted.')
            return 'Deleted!:('
        
        except Exception as error:
            raise Exception(f'{str(error)}.')

            
    def update(self):
        try:
            if self.is_valid():
                propertycase = propertyModel.objects.get(link__iendswith=self.token)
                output = self.get_output(only_defined=True)
                for item in output:
                    if item in propertycase.__dict__.keys():
                        propertycase.__dict__[item] = output[item]

                propertycase.save()
            else:
                raise Exception(f"Price is not valid.")

            log(f'last_case: {propertycase}\n{22*" "}updated_case: {output}\n{30*' '}case: \'{propertycase.link[-8:]}\' is updated.')
            return 'Updated!:)'
        
        except Exception as error:
            raise Exception(f'{str(error)}')

#LOG
logging.basicConfig(filename='log.log', level=logging.INFO, format='%(asctime)s: %(message)s')

def log(message):
    logging.info(message)

def logreader():
    land_typ_stat = []
    with open("log.log",'r') as file:
        logtxt = file.readlines()
        if not logtxt: 
            logtxt = ['']
        return logtxt[-1] + str(land_typ_stat)




def update_status(landuse, ptype, activat):    
    for grand_dict in GRAND_DICT:
        if grand_dict["landuse"] == landuse and grand_dict["ptype"] == ptype:
            grdict = grand_dict
            if activat == False:
                grdict['update_status'] = 'active'
            elif activat == True:
                grdict['update_status'] = 'deactive'

def status_reader():
    PCStatus = []
    for case in GRAND_DICT:
        PCStatus.append(case['landuse'] + '_' + case['ptype'] + ': ' + case['update_status'])
    return PCStatus

def cdt(lu: str, typ:str) -> list:
    if propertyModel.objects.filter(landuse=lu,ptype= typ):
        count = propertyModel.objects.filter(landuse=lu, ptype=typ).count()
        lastupdate = propertyModel.objects.filter(landuse=lu ,ptype=typ).last().date_time  # type: ignore
    else:
        count = 0
        lastupdate = "بروز رسانی نشده"
    return [count, lastupdate]

#def ThradedUpdate(land, typ):
#    try:
#        update(land, typ)
#        log(f"update('{land}','{typ}') is done")
#    except Exception as ex:
#        log(str(ex)+'----')
#        raise Exception
#

#MakeShape
@admin.action(description='create shpfiles')
def makeshape(modeladmin, request, queryset):
    import geopandas
    import shapely

    #DeffinePoint
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
            'caseid': case_id,     'landuse': landuse, 'ptype': ptype,
            'price': price,        'area': area,       'Cyear': Cyear,
            'mortgage' : mortgage, 'rent' : rent,      'lat' : lat,
            'lon' : lon,           'mahale' : mahale,  'exp' : exp,
            'link' : link,         'date_time' : date_time
        }

        pointgdf = geopandas.GeoDataFrame(ATable, geometry = points, crs='EPSG:4326')
        pointgdf.to_crs(epsg =32639, inplace = True)
        pointgdf.to_file(r'updateData/shp/points.shp')
        return pointgdf

    #DeffinePolygon
    def geoprocsseing(pointgdf):
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


