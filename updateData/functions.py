from updateData.models import propertyModel

from selenium import webdriver
#from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.chrome.options import Options
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager

import datetime
import os
import requests
from  bs4 import BeautifulSoup
import time
import re



LOG = ''

def log(a):
    global LOG
    LOG = str(datetime.datetime.today())+ ':   ' + a + '\n'
    with open('log.txt', 'a') as logfile:
        logfile.write(LOG)
    return LOG

def not_duplicate(output):

    landuse = output['landuse']
    ptype = output['ptype']
    price = output['price']
    area = output['Area']
    Cyear = output['CYear']
    mortgage = output['mortgage']
    rent = output['rent']
    lat = repr(output['lat'])
    lon = repr(output['lon'])
    mahale = output['mahale']
    exp = output['exp']
    link = output['link']
    date_time = output['date_time']

    result = propertyModel.objects.filter(
        landuse=landuse, 
        ptype=ptype, 
        price=price, 
        area=area, 
        Cyear=Cyear, 
        mortgage=mortgage, 
        rent=rent, 
        lat=lat, 
        lon=lon, 
        mahale=mahale, 
        exp=exp, 
        link=link, 
        date_time=date_time
    )
    
    if result:
        return False
    else:
        return True
    
def insert(output):

    landuse = output['landuse']
    ptype = output['ptype']
    price = output['price']
    area = output['Area']
    Cyear = output['CYear']
    mortgage = output['mortgage']
    rent = output['rent']
    lat = repr(output['lat'])
    lon = repr(output['lon'])
    mahale = output['mahale']
    exp = output['exp']
    link = output['link']
    date_time = output['date_time']

    try:
        propertyModel.objects.create(
            landuse=landuse, 
            ptype=ptype, 
            price=price, 
            area=area, 
            Cyear=Cyear, 
            mortgage=mortgage, 
            rent=rent, 
            lat=lat, 
            lon=lon, 
            mahale=mahale, 
            exp=exp, 
            link=link, 
            date_time=date_time
        )

    except Exception as error:
        log(str(error)+"---"+ str(output))
    
def start_driver():
    #if os.path.isfile(r"chromedriver.txt"):
    #    with open(r"chromedriver.txt", 'r') as file:
    #        PathChromeDriverManager = file.read().strip()
    #else:
    #    PathChromeDriverManager = ChromeDriverManager().install()
    #    with open(r"chromedriver.txt", 'w') as file:
    #        file.write(PathChromeDriverManager)
    #chrome_options = Options()
    #chrome_options.headless = True
    #service = Service(PathChromeDriverManager)
    #driver = webdriver.Chrome(options= chrome_options,service=service)

    if os.path.isfile(r"ECD.txt"):
        with open(r"ECD.txt", 'r') as file:
            PathECDM = file.read().strip()
    else:
        PathECDM = EdgeChromiumDriverManager().install()
        with open(r"ECD.txt", 'w') as file:
            file.write(PathECDM)
    edge_options = Options()
    edge_options.add_argument("--headless=new")
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--window-size=1920x1080")
    service = Service(PathECDM)
    driver = webdriver.Edge(options=edge_options, service=service)
    return driver

def PropertyCases(url, n=10):
    for i in range(n):
        divar = requests.get(url)
        if divar.status_code == 200:
            soup = BeautifulSoup(divar.content, 'html.parser')
            Pcases = soup.find_all('a', class_ = "unsafe-kt-post-card__action")
            if Pcases:
                log('in %i try, Pcases found' % i)
                return Pcases
            else:
                log('in %i try, Pcases not found' % i)
        else:
            log('in %i try, Pcases not found (status code: %s)' % (i, divar.status_code))
        time.sleep(10)

    raise ReferenceError('status_code is not 200 or Pcases not found after %d tries' % n)

def get_exp(soup1):
    explink = soup1.find_all('h1', class_ = "kt-page-title__title kt-page-title__title--responsive-sized")[0].get_text()
    explink = explink
    return explink

#def get_loc(driver):
#    try:
#        pic = WebDriverWait(driver,10).until(
#            EC.element_to_be_clickable((By.CLASS_NAME, "image-dbbad"))
#        )
#    except:
#        log('map pic not found')
#        return None
#    pic.click()
#    try: 
#        link_element = WebDriverWait(driver, 10).until(
#            EC.presence_of_element_located((By.CSS_SELECTOR, ".map-cm__button"))
#        )
#        link = link_element.get_attribute("href")
#    except:
#        log("balad links not found")
#        return None
#    (lat,long) = re.search(r"latitude=(\d*\.\d*)&longitude=(\d*\.\d*)", link).groups()
#    x_y =[float(lat),float(long)]
#    return x_y
#

def get_loc(driver):
    pr_data = str(driver.page_source)
    lat_ = re.search(r'.*"latitude":(\d*\.\d*).*', pr_data)
    long_ = re.search(r'.*"longitude":(\d*\.\d*).*', pr_data)
    x_y = None
    if lat_ and long_ :
        (lat,) = lat_.groups()
        (long,) = long_.groups()
        x_y =[float(lat),float(long)]
    return x_y

def buyPrice(driver):
    soup1 = BeautifulSoup(driver.page_source, 'html.parser')
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

def rentPrice(driver):
    soup1 = BeautifulSoup(driver.page_source, 'html.parser')
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


def update(landuse , ptype):
    log('update(%s, %s) is run'% (landuse,ptype))
    match (landuse, ptype):
        case ('res','buy'):
            insert_counter = 0
            url = 'https://divar.ir/s/tehran/buy-apartment'   # just appartment, not villa 
            Pcases = PropertyCases(url)
            log('get'+ str(len(Pcases)) +' Pcasses')
            for Pcase in Pcases:
                Area = ''
                CYear = ''
                XY = []
                exp = ''
                mahale = ''
                mortgage = 0.0
                price = 0.0
                rent = 0.0                
                Plink = 'https://divar.ir'+ Pcase.get('href')
                driver = start_driver()
                driver.get(Plink)
                time.sleep(5)
                #get_price
                p_a = buyPrice(driver)
                price = p_a[0]
                #get_loc
                XY =get_loc(driver)
                trying = 0
                while trying < 3 and not XY:
                    log('intrying %i x-y not founded.' %trying)
                    trying += 1
                    driver.get(Plink)
                    time.sleep(5)
                    XY = get_loc(driver)
                    if trying > 0 and not XY:
                        d_tmp = start_driver()
                        d_tmp.get(Plink)
                        time.sleep(5)
                        XY = get_loc(d_tmp)
                        d_tmp.quit()

                if not XY:
                    log(Plink + ' have no loc')
                    driver.quit()
                    continue
                if not price:
                    log(Plink + ' have no price')
                    driver.quit()
                    continue
                lat, long = XY
                #get_Area & CYear
                soup1 = BeautifulSoup(driver.page_source, 'html.parser')
                a = soup1.find_all('table', class_ = "kt-group-row")[0]
                d = a.get_text('thead').split('thead')
                Area = d[3]
                CYear = d[4]
                #get_mahale
                mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                mahale = mahale_text.get_text().split("\u060C")[1]
                #get_exp
                exp = get_exp(soup1)
                #output
                output = {
                    'landuse': landuse,
                    'ptype' : ptype,
                    'price' : price,
                    'Area': int(Area),
                    'CYear': CYear , 'mortgage': 0,
                    'rent': 0,
                    'lat': lat,
                    'lon' : long,
                    'mahale': mahale,
                    'exp': exp,
                    'link' : Plink,
                    'date_time' : datetime.datetime.today()
                }
                if not_duplicate(output):
                    insert(output)
                    insert_counter = insert_counter + 1
                    log('Case '+ str(Pcases.index(Pcase)+1) +'/'+ str(len(Pcases)) +  " & "+ str(insert_counter) + " Case inserted")
                else: 
                    log(Plink + ' is duplicate')
                driver.quit()
            log(landuse+', '+ptype+' UPDATED!')
        case ('res', 'rent'):
            insert_counter = 0
            url = 'https://divar.ir/s/tehran/rent-residential'
            Pcases = PropertyCases(url)
            log('get'+ str(len(Pcases)) +' Pcasses')
            for Pcase in Pcases:
                Area = ''
                CYear = ''
                XY = []
                exp = ''
                mahale = ''
                mortgage = 0.0
                price = 0.0
                rent = 0.0
                FArea = None
                F = None
                Plink = 'https://divar.ir'+ Pcase.get('href')
                driver = start_driver()
                driver.get(Plink)
                time.sleep(10)
                #get_mortgage, rent, area, yeare
                mortgage, rent = rentPrice(driver)
                soup1 = BeautifulSoup(driver.page_source, 'html.parser')                
                style = soup1.find_all('input' , class_= "kt-range-slider__input")
                if style:
                    prices = soup1.find_all('td' , class_= 'kt-group-row-item kt-group-row-item__value kt-group-row-item--info-row')
                    Area = prices[0].get_text()
                    CYear = prices[1].get_text()
                elif not style:
                    FArea = soup1.find_all("table", class_= "kt-group-row")[0]
                    F = FArea.get_text('p').split('p')
                    for i in range(len(F)):
                        if 'متراژ' in F[i]:
                            Area = F[int(i+ (len(F)/2))]
                        elif 'ساخت' in F[i]:
                            CYear = F[int(i+ (len(F)/2))]
                if mortgage is None and rent is None:
                    log(Plink + ' have wrong price')
                    continue
                mortgage = int(mortgage)
                rent = int(rent)
                price = (mortgage + (rent*30))/int(Area)
                #get_loc
                XY = get_loc(driver)
                if not XY:
                    log(Plink + ' have no loc')
                    continue
                lat, long = XY
                #get_mahale1
                mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                mahale = mahale_text.get_text().split("\u060C")[1]
                #get_exp
                exp = get_exp(soup1)
                
                #output
                output = {
                    'landuse': landuse,
                    'ptype' : ptype,
                    'price' : price,
                    'Area': int(Area),
                    'CYear': CYear, 
                    'mortgage': mortgage, 
                    'rent': rent,
                    'lat': lat, 
                    'lon' : long,
                    'mahale': mahale, 
                    'exp': exp,
                    'link' : Plink,
                    'date_time' : datetime.datetime.today()
                }
                
                if not_duplicate(output):
                    insert(output)
                    insert_counter = insert_counter + 1
                    log('Case '+ str(Pcases.index(Pcase)+1) +'/'+ str(len(Pcases)) +  " & "+ str(insert_counter) + " Case inserted")
                else: 
                    log(Plink + ' is duplicate')
            driver.quit()
            log(landuse+', '+ptype+' UPDATED!')       
        case ('resland', 'buy'):
            insert_counter = 0
            url = 'https://divar.ir/s/tehran/buy-old-house'
            Pcases = PropertyCases(url)
            log('get'+ str(len(Pcases)) +' Pcasses')
            for Pcase in Pcases:
                Area = ''
                CYear = ''
                XY = []
                exp = ''
                mahale = ''
                price = 0.0
                Plink = 'https://divar.ir'+ Pcase.get('href')
                driver = start_driver()
                driver.get(Plink)
                time.sleep(10)
                #get_price, area
                soup1 = BeautifulSoup(driver.page_source, 'html.parser')
                price, Area = buyPrice(driver)
                if not price:
                    log(Plink + ' have no price')
                    continue
                #get_loc
                XY = get_loc(driver)
                if not XY:
                    log(Plink + ' have no loc')
                    continue
                lat, long = XY
                #get_mahale
                mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                mahale = mahale_text.get_text().split("\u060C")[1]
                #get_exp
                exp = get_exp(soup1)
                #output
                output = {
                    'landuse': landuse, 
                    'ptype' : ptype, 
                    'price' : price, 
                    'Area': int(Area), 
                    'CYear': 0, 
                    'mortgage': 0, 
                    'rent': 0, 
                    'lat': lat, 
                    'lon' : long, 
                    'mahale': mahale, 
                    'exp': exp, 
                    'link' : Plink, 
                    'date_time' : datetime.datetime.today()
                }
                if not_duplicate(output):
                    insert(output)
                    insert_counter = insert_counter + 1
                    log('Case '+ str(Pcases.index(Pcase)+1) +'/'+ str(len(Pcases)) +  " & "+ str(insert_counter) + " Case inserted")
                else: 
                    log(Plink + ' is duplicate')
            driver.quit()
            log(landuse+', '+ptype+' UPDATED!')
        case ('com', 'buy'):
            insert_counter = 0
            url = 'https://divar.ir/s/tehran/buy-commercial-property'
            Pcases = PropertyCases(url)
            log('get'+ str(len(Pcases)) +' Pcasses')
            for Pcase in Pcases:
                Area = ''
                CYear = ''
                XY = []
                exp = ''
                mahale = ''
                price = 0.0
                Plink = 'https://divar.ir'+ Pcase.get('href')
                driver = start_driver()
                driver.get(Plink)
                time.sleep(10)
                #get_price
                p_a = buyPrice(driver)
                price = p_a[0]
                if not price:
                    log(Plink + ' have no price') 
                    continue
                #get_loc
                XY = get_loc(driver)
                if not XY:
                    log(Plink + ' have no loc')
                    continue
                lat, long = XY
                #get_Area & CYear
                soup1 = BeautifulSoup(driver.page_source, 'html.parser')
                a = soup1.find_all('table', class_ = "kt-group-row")[0]
                d = a.get_text('thead').split('thead')
                Area = d[3]
                CYear = d[4]
                #get_mahale
                mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                mahale = mahale_text.get_text().split("\u060C")[1]
                mahale = mahale
                
                #get_exp
                exp = get_exp(soup1)
                #output
                output = {
                    'landuse': landuse,
                    'ptype' : ptype ,
                    'price' : price, 
                    'Area': int(Area) , 
                    'CYear': CYear , 
                    'mortgage': 0 , 
                    'rent': 0 , 
                    'lat': lat , 
                    'lon' : long , 
                    'mahale': mahale , 
                    'exp': exp, 
                    'link' : Plink , 
                    'date_time' : datetime.datetime.today()
                }
                if not_duplicate(output):
                    insert(output)
                    insert_counter = insert_counter + 1
                    log('Case '+ str(Pcases.index(Pcase)+1) +'/'+ str(len(Pcases)) +  " & "+ str(insert_counter) + " Case inserted")
                else: 
                    log(Plink + ' is duplicate')
            driver.quit()
            log(landuse+', '+ptype+' UPDATED!')
        case ('com', 'rent'):
            insert_counter = 0
            url = 'https://divar.ir/s/tehran/rent-commercial-property'
            Pcases = PropertyCases(url)
            log('get'+ str(len(Pcases)) +' Pcasses')
            for Pcase in Pcases:
                Area = ''
                CYear = ''
                XY = []
                exp = ''
                mahale = ''
                mortgage = 0.0
                price = 0.0
                rent = 0.0
                Plink = 'https://divar.ir'+ Pcase.get('href')
                driver = start_driver()
                driver.get(Plink)
                time.sleep(10)
                mortgage, rent = rentPrice(driver)
                soup1 = BeautifulSoup(driver.page_source, 'html.parser')
                if 'اجارهٔ دفاتر صنعتی، کشاورزی و تجاری' in soup1.find_all('span', class_= "kt-breadcrumbs__action-text")[2]:
                    log(Plink + 'indasterial Case')
                    continue
               #get_price & get_Area & get_CYear
                style = soup1.find_all('input' , class_= "kt-range-slider__input")
                if style:
                    prices = soup1.find_all('td' , class_= 'kt-group-row-item kt-group-row-item__value kt-group-row-item--info-row')
                    Area = prices[0].get_text()
                    CYear = prices[1].get_text()
                elif not style :
                    FArea = soup1.find_all("table", class_= "kt-group-row")[0]
                    F = FArea.get_text('p').split('p')
                    for i in range(len(F)):
                        if 'متراژ' in F[i]:
                            Area = F[int(i+ (len(F)/2))]
                        elif 'ساخت' in F[i]:
                            CYear = F[int(i+ (len(F)/2))]
                if mortgage is None and rent is None:
                    log(Plink + ' have no price')
                    continue
                mortgage = int(mortgage)
                rent = int(rent)
                price = (mortgage + (rent*30))/int(Area)
                #get_loc
                XY = get_loc(driver)
                if not XY:
                    log(Plink + ' have no loc')
                    continue
                lat , long = XY
                #get_mahale1
                mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                mahale = mahale_text.get_text().split("\u060C")[1]
                #get_exp
                exp = get_exp(soup1)
                #output
                output = {
                    'landuse': landuse,
                    'ptype' : ptype,
                    'price' : price,
                    'Area': int(Area),
                    'CYear': CYear,
                    'mortgage': mortgage, 
                    'rent': rent,
                    'lat': lat,
                    'lon' : long, 
                    'mahale': mahale,
                    'exp': exp,
                    'link' : Plink,
                    'date_time' : datetime.datetime.today()
                }
                if not_duplicate(output):
                    insert(output)
                    insert_counter = insert_counter + 1
                    log('Case '+ str(Pcases.index(Pcase)+1) +'/'+ str(len(Pcases)) +  " & "+ str(insert_counter) + " Case inserted")
                else: 
                    log(Plink + ' is duplicate')
            driver.quit()
            log(landuse+', '+ptype+' UPDATED!')
        case _ :
            raise ValueError('input argument is wrong')                

def cdt(lu, typ):
    if propertyModel.objects.filter(landuse=lu,ptype= typ):
        count = propertyModel.objects.filter(landuse=lu, ptype=typ).count()
        lastupdate = propertyModel.objects.filter(landuse=lu ,ptype=typ).last().date_time
    else:
        count = 0
        lastupdate = "بروز رسانی نشده"
    return [count, lastupdate]
