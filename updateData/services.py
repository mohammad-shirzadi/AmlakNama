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


class Property:    

    def set_soup1(self):
        self.soup1 = BeautifulSoup(self.page_source, 'html.parser')
    
    def get_loc(self,pg_source=None) -> list[float] | None:
        _pg_source = self.page_source if pg_source is None else pg_source
        pr_data = str(_pg_source)
        lat_ = re.search(r'"latitude"\s*:\s*"?(?P<lat>\d+\.?\d*)"?', pr_data)
        long_ = re.search(r'"longitude"\s*:\s*"?(?P<long>\d+\.?\d*)"?', pr_data)
        if lat_ and long_:
            lat = float(lat_.groups()[0])
            long = float(long_.groups()[0])
            return [lat,long]
        return None
    
    def has_map(self) -> bool:
        img = self.soup1.find_all('img', alt='موقعیت مکانی')
        if img:
            return True
        else:
            return False

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

    def get_PropertyCases(self, url, retry=RETRY):
        _Pcases = None
        while retry > 0:
            divar = requests.get(url)
            if divar.status_code == 200:
                soup = BeautifulSoup(divar.text, 'html.parser')
                _Pcases = soup.find_all('a', class_="kt-post-card__action")
                if _Pcases:
                    self.Pcases = _Pcases
                    break
                else:
                    log('_Pcases not found. status code: %i.' %(divar.status_code))    
            else:
                log('_Pcases not found. status code: %i.' %(divar.status_code))
                time.sleep(2)
                retry -= 1
        if not _Pcases:
            log("Pcases not founded after retries.")
            raise Exception("Pcases not founded after retries.")

    def get_Pcases(self):
        global RETRY_SLEEP_TIME
        driver = start_driver()
        driver.get(self.link)
        time.sleep(RETRY_SLEEP_TIME)
        self.page_source = driver.page_source
        driver.quit()

    def get_output(self):
        output = {
            'landuse': self.landuse, 'ptype' : self.ptype, 'price' : self.price,
            'area': self.area,         'Cyear': self.Cyear,     'mortgage': self.mortgage,
            'rent': self.rent,         'lat': self.lat,       'lon' : self.lon,
            'mahale': self.mahale,       'exp': self.exp,       'link' : self.link,
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

        #### TODO no need to create like below add **output
        try:
            propertyModel.objects.create(**self.get_output())

        except Exception as error:
            log(f'[{self.landuse}- {self.ptype}] - in insert step errore: {str(error)} -- {str(self.get_output())}.')
            raise Exception

    def retry_get_data(self, function, retry=RETRY, driver=DRIVER):
        global RETRY_SLEEP_TIME
        ret = retry
        if driver:
            while retry > 0:
                try:
                    dr = start_driver()
                    dr.get(self.link)
                    time.sleep(int(RETRY_SLEEP_TIME))
                    tmp_pgs = dr.page_source
                    result = function(tmp_pgs)
                    dr.quit()
                    if result:
                        return result
                    else:
                        log('in retrying %i result not founded.' %(ret - retry + 1))
                        retry -= 1
                except Exception as ex:
                    log('in retry_get_data driver True: ' + str(ex) + self.link)
                    #raise Exception
                    continue
        else:
            while retry > 0:
                try:
                    r = requests.get(self.link)
                    result = function(r.content)
                    if result:
                        return result
                    else:
                        log('in retrying %i result not founded.' %(ret - retry + 1))
                        retry -= 1
                except Exception as ex:
                    log('in retry_get_data driver False: ' + str(ex) + self.link)
                    #raise Exception
                    continue



    def update(self, _landuse, _ptype):
        grdict = {}
        insert_counter = 0
        #### create class to loger

        for grand_dict in GRAND_DICT:
            if grand_dict["landuse"] == _landuse and grand_dict["ptype"] == _ptype:
                self.landuse = _landuse
                self.ptype = _ptype
                grdict = grand_dict
        
        log('update(%s, %s) is run.'% (self.landuse,self.ptype))
        self.get_PropertyCases(grdict['url'])
        log(f'[{self.landuse}- {self.ptype}] - get {str(len(self.Pcases))} Pcasses')
        for Pcase in self.Pcases:
            try:
                self.link = 'https://divar.ir'+ Pcase.get('href')
                self.get_Pcases()
                self.set_soup1()

                if not self.page_source:
                    self.retry_get_data(self.get_Pcases, driver=False)
                if not self.page_source:
                    log(f'[{self.landuse}- {self.ptype}] - PcaseRespons is not availabe.')
                    continue
                
                if not self.has_map():
                    log(f'[{self.landuse}- {self.ptype}] - {self.link} - has map is false.')
                    continue

                xy = self.get_loc(self)
                
                #retry
                if not xy:
                    xy = self.retry_get_data(self.get_loc)
                if not xy:
                    log(f'[{self.landuse}- {self.ptype}] - {self.link} - have no loc')
                    continue


                self.mortgage = self.rent = data = 0
                if 'buy_price' in grdict['find_key']:
                    if grdict['find_key']['buy_price'] == 'price':
                        d1 = d2 = ""
                        self.get_buyPrice()
                        opt = grdict['find_key']['findall']

                        d1 = (self.soup1.find_all(opt[0],class_ = opt[1]))
                        d2 = d1[opt[2]]
                        data = d2.get_text('thead').split('thead')

                        self.area = int(data[3])
                        self.Cyear = data[4]

                    elif grdict['find_key']['buy_price'] == 'price_area':
                        self.get_buyPrice()
                        self.Cyear = 0

                elif 'rent_price' in grdict['find_key']:
                    self.get_rentPrice()
                    opt = grdict['find_key']
                    
                    if 'اجارهٔ دفاتر صنعتی، کشاورزی و تجاری' in self.soup1.find_all('span', class_= "kt-breadcrumbs__action-text")[2]:
                        log(f'[{self.landuse}- {self.ptype}] - {self.link} - indasterial Case')
                        continue

                    style = self.soup1.find_all(opt['style_findall'][0] , class_= opt['style_findall'][1])
                    if style:
                        prices = self.soup1.find_all(opt['styled_findall'][0] , class_= opt['styled_findall'][1])
                        self.area = int(prices[0].get_text())
                        self.Cyear = prices[1].get_text()

                    elif not style:
                        FArea = self.soup1.find_all(opt['notstyled_findall'][0], class_= opt['notstyled_findall'][1])[opt['notstyled_findall'][2]]
                        F = FArea.get_text('p').split('p')

                        for i in range(len(F)):
                            if 'متراژ' in F[i]:
                                self.area = int(F[int(i+ (len(F)/2))])
                            elif 'ساخت' in F[i]:
                                self.Cyear = F[int(i+ (len(F)/2))]
                    
                    if self.mortgage is None and self.rent is None:
                        log(f'[{self.landuse}- {self.ptype}] - {self.link} - have no price')
                        continue
                    
                    self.price = int((self.mortgage + (self.rent*30.0)) / int(self.area))
                
                if not self.price:
                    log(f'[{self.landuse}- {self.ptype}] - {self.link} - have no price')
                    continue
                self.lat = repr(xy[0])
                self.lon = repr(xy[1])
                self.get_district()
                self.get_exp()
                self.date_time = timezone.now()

                if self.not_duplicate(propertyModel):
                    self.insert(propertyModel)
                    insert_counter = insert_counter + 1
                    log(f"[{self.landuse}- {self.ptype}] Case {str(self.Pcases.index(Pcase)+1)}/{str(len(self.Pcases))} & {str(insert_counter)} Case inserted")
                else: 
                    log(self.link + ' is duplicate')
                    
            except Exception as ex:
                log(str(ex)+self.link)
                raise Exception
            

        log(self.landuse+', '+self.ptype+' UPDATED!')





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


