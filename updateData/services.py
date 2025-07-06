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
from selenium import webdriver




DRIVER_BROWSER = os.environ.get('DRIVER_BROWSER',default='edge')
DRIVER_TIMEOUT = int(os.environ.get('DRIVER_TIMEOUT',default=30))
RETRY_SLEEP_TIME = int(os.environ.get('RETRY_SLEEP_TIME',default=5))
RETRY = int(os.environ.get('RETRY',default=3))


STOPSIGN = False
GRAND_DICT = [
    {"landuse":"res", "ptype":"buy", "url":"https://divar.ir/s/tehran/buy-apartment",
     "propertises":{'landuse':"res",'ptype':"buy",
                    'find_key':{"findall":['table',"kt-group-row",0], 'buy_price':'price'}
                    }},

    {"landuse":"com", "ptype":"buy","url":"https://divar.ir/s/tehran/buy-commercial-property",
     "propertises":{'landuse':"res",'ptype':"buy",
                    'find_key':{"findall":['table',"kt-group-row",0],'buy_price':'price' }
                    }},

    {"landuse":"resland", "ptype":"buy","url":"https://divar.ir/s/tehran/buy-old-house",
     "propertises":{'landuse':"res",'ptype':"buy",
                    'find_key':{"findall":['table',"kt-group-row",0],'buy_price':'price_area'}
                    }},

    {"landuse":"res", "ptype":"rent","url":"https://divar.ir/s/tehran/rent-residential",
     "propertises":{'landuse':"res",'ptype':"buy",
                    'find_key':{"style_findall":['input',"kt-range-slider__input"],
                                "styled_findall":['td','kt-group-row-item kt-group-row-item__value kt-group-row-item--info-row'],
                                "notstyled_findall":['table','kt-group-row',0],
                                'rent_price':'mortgage_rent'}
                    }},

    {"landuse":"com", "ptype":"rent","url":"https://divar.ir/s/tehran/rent-commercial-property",
     "propertises":{'landuse':"res",'ptype':"buy",
                    'find_key':{"style_findall":['input',"kt-range-slider__input"],
                                "styled_findall":['td','kt-group-row-item kt-group-row-item__value kt-group-row-item--info-row'],
                                "notstyled_findall":['table','kt-group-row',0],
                                'rent_price':'mortgage_rent'}
                    }},
]





#LOG
logging.basicConfig(filename='log', level=logging.INFO, format='%(asctime)s: %(message)s')
def log(message):
    logging.info(message)

def logreader():
    with open("log",'r') as file:
        logtxt = file.readlines()
        if not logtxt: 
            logtxt = ['']
        return logtxt[-1]

#SELENIUM_DRIVER
def start_driver(browser=DRIVER_BROWSER,DRIVER_TIMEOUT=60):
    if browser == 'chrome':

        from selenium.webdriver.chrome.service import Service as ch_Service
        from selenium.webdriver.chrome.options import Options as ch_Options
        from webdriver_manager.chrome import ChromeDriverManager

        if os.path.isfile(r"chromedriver.txt"):
            with open(r"chromedriver.txt", 'r') as file:
                PathChromeDriverManager = file.read().strip()
        else:
            PathChromeDriverManager = ChromeDriverManager().install()
            with open(r"chromedriver.txt", 'w') as file:
                file.write(PathChromeDriverManager)
        
        chrome_options = ch_Options()
        chrome_options.headless = True
        service = ch_Service(PathChromeDriverManager)
        driver = webdriver.Chrome(options= chrome_options,service=service)

    elif browser == 'edge':

        from selenium.webdriver.edge.options import Options as edg_Options
        from selenium.webdriver.edge.service import Service as edg_Service
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        
        if os.path.isfile(r"msedgedriver.txt"):
            with open(r"msedgedriver.txt", 'r') as file:
                PathECDM = file.read().strip()
        else:
            PathECDM = EdgeChromiumDriverManager().install()
            with open(r"msedgedriver.txt", 'w') as file:
                file.write(PathECDM)
        edge_options = edg_Options()
        edge_options.add_argument("--headless=new")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1920x1080")
        service = edg_Service(PathECDM)
        driver = webdriver.Edge(options=edge_options, service=service)
    
    driver.set_page_load_timeout(DRIVER_TIMEOUT)
    return driver


#GET_ADV_DATA
def get_loc(page_source):
    pr_data = str(page_source)
    lat_ = re.search(r'"latitude"\s*:\s*"?(?P<lat>\d+\.?\d*)"?', pr_data)
    long_ = re.search(r'"longitude"\s*:\s*"?(?P<long>\d+\.?\d*)"?', pr_data)
    x_y = None
    if lat_ and long_ :
        (lat,) = lat_.groups()
        (long,) = long_.groups()
        x_y =[float(lat),float(long)]
    return x_y

def get_buyPrice(page_source):
    soup1 = BeautifulSoup(page_source, 'html.parser')
    prices = soup1.find_all('div', class_ = "kt-base-row kt-base-row--large kt-unexpandable-row")
    price = None
    Area = None
    for a in prices:
        p = re.search(r'\d[\d\u066C]*',a.get_text())
        if not p:
            pass
        elif re.match(r'۱{1,3}(٬۱{3})+$', p.group().replace('\u066C', '')):
            return [None, None]
        elif "قیمت هر متر" in a.get_text():
            p = p.group().replace('\u066C', '')
            price = int(p)
        elif "متراژ" in a.get_text():
            p = p.group().replace('\u066C', '')
            Area = int(p)
    return [price, Area]

def get_rentPrice(page_source):
    soup1 = BeautifulSoup(page_source, 'html.parser')
    prices = soup1.find_all('div', class_ = "kt-base-row kt-base-row--large kt-unexpandable-row")
    mortgage = None
    rent = None
    style = soup1.find_all('input' , class_= "kt-range-slider__input")
    #get_mortgage, rent, area, yeare
    if style:
        unit = 0
        prices = soup1.find_all('td' , class_= 'kt-group-row-item kt-group-row-item__value kt-group-row-item--info-row')
        for x in [3,4]:
            if 'میلیون' in prices[x].get_text():
                unit = 1000000
            elif 'میلیارد' in prices[x].get_text():
                unit = 1000000000
            elif 'هزار' in prices[x].get_text():
                unit = 1

            p = re.search(r'(\d+\.*\d*)', prices[x].get_text())
            if p and re.match(r'۱{1,3}(٬۱{3})+$', p.group()):
                return [None, None]
            elif p:
                m = float(p.group().split(' ')[0])*unit
            else:
                m = 0
        
            if x == 3:
                mortgage=m
            elif x == 4:
                rent=m
        return [mortgage,rent]
    elif not style:
        for a in prices: 
            p = re.search(r'\d[\d\u066C]*',a.get_text())
            if p and re.match(r'۱{1,3}(٬۱{3})+$', p.group()):
                return [None, None]
            elif p and "ودیعه" in a.get_text():  
                p = p.group().replace('\u066C', '')
                mortgage = int(p)
            elif p and "اجاره" in a.get_text():
                p = p.group().replace('\u066C', '')
                rent = int(p)
            elif not p and "ودیعه" in a.get_text() and "اجاره" not in a.get_text():
                    mortgage = 0
            elif not p and "اجاره" in a.get_text() and "ودیعه" not in a.get_text():
                    rent = 0
        if mortgage == 0 and rent == 0:
            return [None, None]
    
        return [mortgage,rent]
    
def get_district(page_source):
    soup1 = BeautifulSoup(page_source, 'html.parser')
    mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
    mahale = mahale_text.get_text().split("\u060C")[1]
    return mahale

def get_exp(page_source):
    soup1 = BeautifulSoup(page_source, 'html.parser')
    explink = soup1.find_all('h1', class_ = "kt-page-title__title kt-page-title__title--responsive-sized")[0].get_text()
    explink = explink
    return explink

def get_PropertyCases(url):
    divar = requests.get(url)
    if divar.status_code == 200:
        soup = BeautifulSoup(divar.content, 'html.parser')
        Pcases = soup.find_all('a', class_="unsafe-kt-post-card__action")
        if Pcases:
            return Pcases
        else:
            log('Pcases not found. status code: %i.' %(divar.status_code))

def get_Pcases(Plink):
    r = requests.get(Plink)
    if r.status_code == 200:
        return r.content
    else:
        return None

def retry_get_data(function, Plink, retry=RETRY, driver=True):
    global STOPSIGN 
    result = None

    if driver:
        while retry > 0 and not result and not STOPSIGN:
            log('in retrying %i result not founded.' %(RETRY-retry))
            retry -= 1
            dr = start_driver()
            #log("retry driver started ...")
            try:
                dr.get(Plink)
                #log("retry get linked...")
                time.sleep(int(RETRY_SLEEP_TIME))
                #log(F'{RETRY_SLEEP_TIME}sec later')
                tmp_pgs = dr.page_source 
                result = function(tmp_pgs)
                dr.quit()
            except Exception as ex:
                log((ex, Plink))
                continue
    else:
        while retry > 0 and not result and not STOPSIGN:
            log('in retrying %i result not founded.' %(RETRY-retry))
            retry -= 1
            try:
                r = requests.get(Plink)
                result = function(r.content)
                #log(result)
            except Exception as ex:
                log((ex, Plink))
                continue

    return result


#INSERT_TO_DB
def not_duplicate(propertyModel,output):
    if propertyModel.objects.filter(
        landuse=output['landuse'], 
        ptype=output['ptype'], 
        price=output['price'], 
        area=output['Area'], 
        Cyear=output['CYear'], 
        mortgage=output['mortgage'], 
        rent=output['rent'], 
        lat=repr(output['lat']), 
        lon=repr(output['lon']), 
        mahale=output['mahale'], 
        exp=output['exp'], 
        link=output['link'], 
        date_time=output['date_time']
    ):
        return False
    else:
        return True

def insert(propertyModel,output):
    try:
        propertyModel.objects.create(
            landuse=output['landuse'], 
            ptype=output['ptype'], 
            price=output['price'], 
            area=output['Area'], 
            Cyear=output['CYear'], 
            mortgage=output['mortgage'], 
            rent=output['rent'], 
            lat=repr(output['lat']), 
            lon=repr(output['lon']), 
            mahale=output['mahale'], 
            exp=output['exp'], 
            link=output['link'], 
            date_time=output['date_time']
        )
    except Exception as error:
        log("in insert step errore: " + str(error) + "---" + str(output))
    

#GET_DATA_UPDATE
def update(landuse, ptype):
    global STOPSIGN 
    log('update(%s, %s) is run.'% (landuse,ptype))
    for grdict in GRAND_DICT:
        if grdict["landuse"] == landuse and grdict["ptype"] == ptype:
            if STOPSIGN:
                log('update(%s, %s) is stopped.'% (landuse,ptype))
                STOPSIGN=False
                return None
            field = grdict['propertises']
            insert_counter = 0
            Pcases = get_PropertyCases(grdict['url'])
            if not Pcases:
                #log('retrying to find Pcases started.')
                Pcases = retry_get_data(get_PropertyCases, grdict['url'],driver=False)
            if not Pcases:
                log("Pcases not founded after retrys.")
                continue
            log('get'+ str(len(Pcases)) +' Pcasses')

            for Pcase in Pcases:
                if STOPSIGN:
                    log('update(%s, %s) is stopped.'% (landuse,ptype))
                    STOPSIGN=False
                    return None
                try:
                    Plink = 'https://divar.ir'+ Pcase.get('href')
                    PcaseResponse = get_Pcases(Plink)
                    if not PcaseResponse:
                        #log('retring for get_pcases started.')
                        PcaseResponse = retry_get_data(get_Pcases, Plink, driver=False)
                    if not PcaseResponse:
                        log('PcaseRespons is not availabe.')
                        continue
                    page_source = PcaseResponse
                    xy = get_loc(page_source)

                    #retry
                    if not xy:
                        #log('get_loc retry is running...')
                        xy = retry_get_data(get_loc,Plink=Plink)
                    if not xy:
                        log(Plink + ' have no loc')
                        continue
                    #log('loc found...')

                    if 'buy_price' in field['find_key']:
                        rent = mortgage = 0
                        if field['find_key']['buy_price'] == 'price':
                            #log('get_buyprice running 1 ...')
                            price = get_buyPrice(page_source)[0]
                            #log('get_buyprice done 1 ...')
                            opt = field['find_key']['findall']
                            soup1 = BeautifulSoup(page_source, 'html.parser')
                            data = (soup1.find_all(opt[0],class_ = opt[1])[opt[2]]).get_text('thead').split('thead')
                            Area = data[3]
                            CYear = data[4]
                            #log('Area and CYear founded')

                        elif field['find_key']['buy_price'] == 'price_area':
                            #log('get_buyprice running 2 ...')
                            price, Area = get_buyPrice(page_source)
                            CYear = 0
                            #log('get_buyprice done 2 ...')

                    elif 'rent_price' in field['find_key']:
                        #log('get_rentprice running...')
                        mortgage, rent = get_rentPrice(page_source)
                        #log('get_rentprice done...')
                        soup1 = BeautifulSoup(page_source, 'html.parser')
                        opt = field['find_key']

                        if 'اجارهٔ دفاتر صنعتی، کشاورزی و تجاری' in soup1.find_all('span', class_= "kt-breadcrumbs__action-text")[2]:
                            log(Plink + 'indasterial Case')
                            continue

                        #get_price & get_Area & get_CYear
                        style = soup1.find_all(opt['style_findall'][0] , class_= opt['style_findall'][1])
                        if style:
                            #log('style founded...')
                            prices = soup1.find_all(opt['styled_findall'][0] , class_= opt['styled_findall'][1])
                            Area = prices[0].get_text()
                            CYear = prices[1].get_text()
                        elif not style:
                            #log('style not found...')
                            FArea = soup1.find_all(opt['notstyled_findall'][0], class_= opt['notstyled_findall'][1])[opt['notstyled_findall'][2]]
                            F = FArea.get_text('p').split('p')
                            for i in range(len(F)):
                                if 'متراژ' in F[i]:
                                    Area = F[int(i+ (len(F)/2))]
                                elif 'ساخت' in F[i]:
                                    CYear = F[int(i+ (len(F)/2))]
                        if mortgage is None and rent is None:
                            log(Plink + ' have no price')
                            continue
                        price = int((mortgage + (rent*30))/int(Area))
                        #log('price found')
                    if not price:
                        log(Plink + ' have no price')
                        continue

                    #log('get data done...')

                    output = {
                        'landuse': landuse,             'ptype' : ptype,        'price' : price,
                        'Area': int(Area),              'CYear': CYear ,        'mortgage': mortgage,
                        'rent': rent,                   'lat': xy[0],           'lon' : xy[1],
                        'mahale': get_district(page_source), 'exp': get_exp(page_source), 'link' : Plink,
                        'date_time' : timezone.now()
                    }
                    #log('output create...')
                    if not_duplicate(propertyModel,output):
                        insert(propertyModel,output)
                        insert_counter = insert_counter + 1
                        log(f"[{landuse}- {ptype}] Case {str(Pcases.index(Pcase)+1)}/{str(len(Pcases))} & {str(insert_counter)} Case inserted")
                    else: 
                        log(Plink + ' is duplicate')
                        
                except Exception as ex:
                    log((ex, Plink))
                    continue
                
            log(landuse+', '+ptype+' UPDATED!')

def cdt(lu, typ):
    if propertyModel.objects.filter(landuse=lu,ptype= typ):
        count = propertyModel.objects.filter(landuse=lu, ptype=typ).count()
        lastupdate = propertyModel.objects.filter(landuse=lu ,ptype=typ).last().date_time
    else:
        count = 0
        lastupdate = "بروز رسانی نشده"
    return [count, lastupdate]


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


#STOP UPDATE
def stop_update():
    global STOPSIGN
    STOPSIGN = True
    log("stop func is calling...")
