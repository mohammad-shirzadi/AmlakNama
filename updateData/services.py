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
from  bs4 import BeautifulSoup



#DRIVER_BROWSER = 'edge'
#DRIVER_TIMEOUT = 30
#RETRY_SLEEP_TIME = 10
#RETRY = 3
#DRIVER = True

DRIVER_BROWSER = os.environ.get('DRIVER_BROWSER',default='edge')
DRIVER_TIMEOUT = int(os.environ.get('DRIVER_TIMEOUT',default=30))
RETRY_SLEEP_TIME = int(os.environ.get('RETRY_SLEEP_TIME',default=10))
RETRY = int(os.environ.get('RETRY',default=3))
DRIVER = bool(os.environ.get('DRIVER', default=True))

GRAND_DICT = [
    {"landuse":"res", "ptype":"buy", "url":"https://divar.ir/s/tehran/buy-apartment",
    'find_key':{"findall":['table',"kt-group-row",0], 'buy_price':'price'},
    "update_status":"deactive" },
    {"landuse":"com", "ptype":"buy","url":"https://divar.ir/s/tehran/buy-commercial-property",
    'find_key':{"findall":['table',"kt-group-row",0],'buy_price':'price'},
    "update_status":"deactive" },
    {"landuse":"resland", "ptype":"buy","url":"https://divar.ir/s/tehran/buy-old-house",
    'find_key':{"findall":['table',"kt-group-row",0],'buy_price':'price_area'},
    "update_status":"deactive"},
    {"landuse":"res", "ptype":"rent","url":"https://divar.ir/s/tehran/rent-residential",
    'find_key':{"style_findall":['input',"kt-range-slider__input"],
                "styled_findall":['td','kt-group-row-item kt-group-row-item__value kt-group-row-item--info-row'],
                "notstyled_findall":['table','kt-group-row',0],
                'rent_price':'mortgage_rent'},
    "update_status":"deactive" },
    {"landuse":"com", "ptype":"rent","url":"https://divar.ir/s/tehran/rent-commercial-property",
    'find_key':{"style_findall":['input',"kt-range-slider__input"],
                "styled_findall":['td','kt-group-row-item kt-group-row-item__value kt-group-row-item--info-row'],
                "notstyled_findall":['table','kt-group-row',0],
                'rent_price':'mortgage_rent'},
    "update_status":"deactive" },
]


def dublecheck(driver=False, retry=RETRY, retry_time_sleep=RETRY_SLEEP_TIME):
    def decorator(func):
        def wraper(self, *args, **kwargs):
            result = func(self,*args,**kwargs)
            for i in range(retry):
                try:
                    if result is None:
                        self.refresh(driver=driver)
                        time.sleep((retry_time_sleep/retry*i))
                        result = func(self,*args,**kwargs)
                        log(('retry', result))
                    else:
                        return result
                except Exception as ex:
                    log(f"happend excepton in retries: {ex}")
                    continue
            return result
        return wraper
    return decorator




class cards:
    def __init__(self,landuse, ptype) -> None:
        self.landuse = landuse
        self.ptype = ptype
        self.cards_page_source = None
        for grand_dict in GRAND_DICT:
            if grand_dict["landuse"] == self.landuse and grand_dict["ptype"] == self.ptype:
                self.grdict = grand_dict
                self.cards_link = self.grdict['url']

    def refresh(self,driver: bool = False) -> None:
        if driver:
            dr = start_driver()
            dr.get(self.cards_link)
            tmp_pgs = dr.page_source
            dr.quit()
        else:
            r = requests.get(self.cards_link )
            if r.status_code == 200:
                tmp_pgs = r.text 
            else:
                raise Exception("status was not 200.")
        self.cards_page_source = tmp_pgs

    @dublecheck(False)
    def get_cards_page_source(self):
        if not self.cards_page_source:
            url = self.grdict['url']
            response = requests.get(url)
            if response.status_code == 200:
                self.cards_page_source = response.text
            else:
                self.cards_page_source = None
                return None
            
        soup = BeautifulSoup(self.cards_page_source, 'html.parser')
        self.cards = soup.find_all('a', class_="kt-post-card__action")

        if self.cards:
            return self.cards
        else:
            return None
        
    def update(self):
        insert_counter = 0
        log('update cards (%s, %s) is run.'% (self.landuse,self.ptype))

        if not self.get_cards_page_source():
            raise Exception("get_cards not found.")

        log(f'[{self.landuse}- {self.ptype}] - get {str(len(self.cards))} Pcasses')

        for Pcase in self.cards:
            try:
                link = 'https://divar.ir'+ Pcase.get('href')
                property_case = Property(link, self.landuse, self.ptype)
                
                property_case.get_pcase_page_source()
                if not property_case.pcase_page_source:
                    log(f'[{property_case.landuse}- {property_case.ptype}] - pcase_page_source is not availabe.')
                    continue
                
                if not property_case.has_map():
                    log(f'[{property_case.landuse}- {property_case.ptype}] - {property_case.property_link} - has map is false.')
                    continue

                if not property_case.get_loc():
                    log(f'[{property_case.landuse}- {property_case.ptype}] - {property_case.property_link} - have no loc')
                    continue

                property_case.mortgage = property_case.rent = data = 0

                if 'buy_price' in self.grdict['find_key']:
                    if self.grdict['find_key']['buy_price'] == 'price':
                        property_case.get_buyPrice()
                        opt = self.grdict['find_key']['findall']
                        d1 = (property_case.soup1.find_all(opt[0],class_ = opt[1]))
                        d2 = d1[opt[2]]
                        data = d2.get_text('thead').split('thead')
                        property_case.area = int(data[3])
                        property_case.Cyear = data[4]

                    elif self.grdict['find_key']['buy_price'] == 'price_area':
                        property_case.get_buyPrice()
                        property_case.Cyear = 0

                elif 'rent_price' in self.grdict['find_key']:
                    property_case.get_rentPrice()
                    opt = self.grdict['find_key']
                    
                    if 'اجارهٔ دفاتر صنعتی، کشاورزی و تجاری' in property_case.soup1.find_all('span', class_= "kt-breadcrumbs__action-text")[2]:
                        log(f'[{property_case.landuse}- {property_case.ptype}] - {property_case.property_link} - indasterial Case')
                        continue

                    style = property_case.soup1.find_all(opt['style_findall'][0] , class_= opt['style_findall'][1])
                    if style:
                        prices = property_case.soup1.find_all(opt['styled_findall'][0] , class_= opt['styled_findall'][1])
                        property_case.area = int(prices[0].get_text())
                        property_case.Cyear = prices[1].get_text()

                    elif not style:
                        FArea = property_case.soup1.find_all(opt['notstyled_findall'][0], class_= opt['notstyled_findall'][1])[opt['notstyled_findall'][2]]
                        F = FArea.get_text('p').split('p')

                        for i in range(len(F)):
                            if 'متراژ' in F[i]:
                                property_case.area = int(F[int(i+ (len(F)/2))])
                            elif 'ساخت' in F[i]:
                                property_case.Cyear = F[int(i+ (len(F)/2))]
                    
                    if property_case.mortgage is None and property_case.rent is None:
                        log(f'[{property_case.landuse}- {property_case.ptype}] - {property_case.property_link} - have no price')
                        continue
                    
                    property_case.price = int((property_case.mortgage + (property_case.rent*30.0)) / int(property_case.area))
                
                if not property_case.price:
                    log(f'[{property_case.landuse}- {property_case.ptype}] - {property_case.property_link} - have no price')
                    continue

                property_case.get_district()
                property_case.get_exp()
                property_case.date_time = timezone.now()

                if property_case.not_duplicate(propertyModel):
                    property_case.insert(propertyModel)
                    insert_counter = insert_counter + 1
                    log(f"[{self.landuse}- {self.ptype}] Case {str(self.cards.index(Pcase)+1)}/{str(len(self.cards))} & {str(insert_counter)} Case inserted")
                else: 
                    log(property_case.property_link + ' is duplicate')
                    
            except Exception as ex:
                log(str(ex)+property_case.property_link)
                continue
                #raise Exception(str(ex)+property_case.property_link)

        log(property_case.landuse+', '+property_case.ptype+' UPDATED!')





class Property:
    def __init__(self, property_link, landuse, ptype) -> None:
        self.property_link = property_link
        self.landuse = landuse
        self.ptype = ptype
        self.pcase_page_source = None
        self.soup1 = None
        self.lat = None
        self.long = None
        self.mortgage = None
        self.rent = None
        self.area = None
        self.Cyear = None

    def refresh(self,driver: bool = False) -> None:
        #breakpoint()
        if driver:
            dr = start_driver()
            time.sleep(5)
            dr.get(self.property_link)
            time.sleep(5)
            tmp_pgs = dr.page_source
            dr.quit()
        else:
            r = requests.get(self.property_link)
            if r.status_code == 200:
                tmp_pgs = r.text 
            else:
                raise Exception("status was not 200.")
        self.pcase_page_source = tmp_pgs

    @dublecheck(True)
    def get_pcase_page_source(self,retry_sleep_time=RETRY_SLEEP_TIME):
        if not self.pcase_page_source:
            driver = start_driver()
            driver.get(self.property_link)
            time.sleep(retry_sleep_time)
            self.pcase_page_source = driver.page_source
            driver.quit()
        if not self.pcase_page_source:
            return None
        self.soup1 = BeautifulSoup(self.pcase_page_source, 'html.parser')
        return self.soup1

    @dublecheck(False)
    def has_map(self) -> bool:
        img = self.soup1.find_all('img', alt='موقعیت مکانی')
        if img:
            return True
        else:
            return False
    
    @dublecheck(True)
    def get_loc(self,pg_source=None) -> list[float] | None:
        pr_data = str(self.pcase_page_source) if pg_source is None else pg_source
        lat_ = re.search(r'"latitude"\s*:\s*"?(?P<lat>\d+\.?\d*)"?', pr_data)
        long_ = re.search(r'"longitude"\s*:\s*"?(?P<long>\d+\.?\d*)"?', pr_data)
        log((lat_, long_))
        if lat_ and long_:
            lat = float(lat_.groups()[0])
            long = float(long_.groups()[0])
            self.lat = repr(lat)
            self.lon = repr(long)
            return [lat,long]
        return None
    
    def get_buyPrice(self) -> list | None:
        sections = self.soup1.find_all('div', class_ = "kt-base-row kt-base-row--large kt-unexpandable-row")

        for section in sections:
            num = re.search(r'\d[\d\u066C]*',section.get_text())
            if not num:
                pass

            elif re.match(r'۱{1,3}(٬۱{3})+$', num.group().replace('\u066C', '')):
                return [None, None]
            #####TODO getprice validation
            elif "قیمت هر متر" in section.get_text():
                num = num.group().replace('\u066C', '')
                self.price = int(num)
            elif "متراژ" in section.get_text():
                num= num.group().replace('\u066C', '')
                self.area = int(num)

    def get_rentPrice(self):
        mortgage, rent = None, None
        style = self.soup1.find_all('input' , class_= "kt-range-slider__input")

        #get_mortgage, rent, area, yeare
        if style:
            unit_converter = 0
            prices = self.soup1.find_all('td' , class_= 'kt-group-row-item kt-group-row-item__value kt-group-row-item--info-row')
            for x in [3,4]:
                
                if 'میلیارد' in prices[x].get_text():
                    unit_converter = 1000000000
                elif 'میلیون' in prices[x].get_text():
                    unit_converter = 1000000
                elif 'هزار' in prices[x].get_text():
                    unit_converter = 1
                
                p = re.search(r'(\d+\.*\d*)', prices[x].get_text())

                if p and re.match(r'۱{1,3}(٬۱{3})+$', p.group()):
                    m = self.rent = self.mortgage = None
                elif p:
                    m = float(p.group().split(' ')[0])*unit_converter
                else:
                    m = 0.0

                if x == 3:
                    self.mortgage=m
                elif x == 4:
                    self.rent=m

        elif not style:
            prices = self.soup1.find_all('div', class_ = "kt-base-row kt-base-row--large kt-unexpandable-row")
            for a in prices: 
                p = re.search(r'\d[\d\u066C]*',a.get_text())
                if p and re.match(r'۱{1,3}(٬۱{3})+$', p.group()):
                    self.rent = self.mortgage = None
                elif p and "ودیعه" in a.get_text():  
                    p = p.group().replace('\u066C', '')
                    self.mortgage = int(p)
                elif p and "اجاره" in a.get_text():
                    p = p.group().replace('\u066C', '')
                    self.rent = int(p)
                elif not p and "ودیعه" in a.get_text() and "اجاره" not in a.get_text():
                        self.mortgage = 0
                elif not p and "اجاره" in a.get_text() and "ودیعه" not in a.get_text():
                        self.rent = 0
            if mortgage == 0 and rent == 0:
                self.rent = self.mortgage = None
          
    def get_district(self):
        mahale_text = self.soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
        _mahale = mahale_text.get_text().split("\u060C")[1]
        self.mahale = _mahale

    def get_exp(self):
        explink = self.soup1.find_all('h1', class_ = "kt-page-title__title kt-page-title__title--responsive-sized")[0].get_text()
        explink = explink
        self.exp = explink

    def get_output(self):
        output = {
            'landuse': self.landuse, 'ptype' : self.ptype, 'price' : self.price,
            'area': self.area,         'Cyear': self.Cyear,     'mortgage': self.mortgage,
            'rent': self.rent,         'lat': self.lat,       'lon' : self.lon,
            'mahale': self.mahale,       'exp': self.exp,       'link' : self.property_link,
            'date_time' : self.date_time
        }
        return output

        #INSERT_TO_DB
    
    def not_duplicate(self, propertyModel):
        if propertyModel.objects.filter(**self.get_output()):
            return False
        else:
            return True

    def insert(self, propertyModel):
        try:
            propertyModel.objects.create(**self.get_output())

        except Exception as error:
            log(f'[{self.landuse}- {self.ptype}] - in insert step errore: {str(error)} -- {str(self.get_output())}.')
            raise Exception





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


#SELENIUM_DRIVER
def start_driver(browser=DRIVER_BROWSER, driver_timeout=DRIVER_TIMEOUT):
    if browser == 'chrome':
        from selenium.webdriver import Chrome as browserwebdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager as drivermanager
        _url = None
        _latest_release_url = None

    elif browser == 'edge':
        from selenium.webdriver import Edge as browserwebdriver
        from selenium.webdriver.edge.service import Service 
        from selenium.webdriver.edge.options import Options 
        from webdriver_manager.microsoft import EdgeChromiumDriverManager as drivermanager
        _url="https://msedgedriver.microsoft.com"
        _latest_release_url="https://msedgedriver.microsoft.com/LATEST_RELEASE"
 
    else:
        raise Exception("browser is not valid.")


    if os.path.isfile(f"{browser}_driver.txt"):
        with open(f"{browser}_driver.txt", 'r') as file:
            PathDriverManager = file.read().strip()
    else:
        with open(f"{browser}_driver.txt", 'w') as file:
            PathDriverManager = drivermanager(url=_url, latest_release_url=_latest_release_url).install() 
            file.write(PathDriverManager)

    options = Options() 
    options.page_load_strategy = 'eager'
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(PathDriverManager)
    driver = browserwebdriver(options=options, service=service) # type: ignore
    driver.set_page_load_timeout(driver_timeout)
    return driver


#GET_DATA_UPDATE

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


