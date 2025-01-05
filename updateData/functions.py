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
    type = output['type']
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
        type=type, 
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
    type = output['type']
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
            type=type, 
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
        raise Exception
    
def start_driver():

    #if os.path.isfile(r"/home/mohammad/CS50P/propertyprice/chromedriver.txt"):
    #    with open(r"/home/mohammad/CS50P/propertyprice/chromedriver.txt", 'r') as file:
    #        PathChromeDriverManager = file.read().strip()
    #else:
    #    PathChromeDriverManager = ChromeDriverManager().install()
    #    with open(r"/home/mohammad/CS50P/propertyprice/chromedriver.txt", 'w') as file:
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
            Pcases = soup.find_all('a', class_ = "kt-post-card__action")
            if Pcases:
                log('in %i try, Pcases found'%i)
                return Pcases
        else:
            log('in %i try, Pcasees not found'%i)
            time.sleep(5)

    raise ReferenceError('status_cod is not 200')

def get_exp(soup1):
    explink = soup1.find_all('h1', class_ = "kt-page-title__title kt-page-title__title--responsive-sized")[0].get_text()
    explink = explink
    return explink

def get_loc(driver,Plink):
    driver.get(Plink)
    try:
        pic = WebDriverWait(driver,10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "image-dbbad"))
        )
    except:
        log('map pic not found')
        return None
    pic.click()
    try: 
        link_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".map-cm__button"))
        )
        link = link_element.get_attribute("href")
    except:
        log("balad links not found")
        return None
    (lat,long) = re.search(r"latitude=(\d*\.\d*)&longitude=(\d*\.\d*)", link).groups()
    x_y =[float(lat),float(long)]
    return x_y

def update(landuse , type):
    log('update(%s, %s) is run'% (landuse,type))
    match (landuse, type):
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
                price = 0.0
                Plink = 'https://divar.ir'+ Pcase.get('href')
                driver = start_driver()
                driver.get(Plink)
                time.sleep(5)
                #get_price
                soup1 = BeautifulSoup(driver.page_source, 'html.parser')
                prices = soup1.find_all('div', class_ = "kt-base-row kt-base-row--large kt-unexpandable-row")
                for a in prices:
                    if "قیمت کل" in a.get_text():
                        p = re.search(r'\d[\d\u066C]*',a.get_text()).group()
                        if re.match('1+[\u066C+1+]+', p):
                            log(Plink + ' have wrong price')
                            break
                    elif "قیمت هر متر" in a.get_text():
                        p = re.search(r'\d[\d\u066C]*',a.get_text()).group()
                        if not re.match('1+[\u066C+1+]+', p):
                            p = p.replace('\u066C', '')
                            price = int(p)
                        else:
                            log(Plink + ' have wrong price')
                if not price:
                    log(Plink + ' have no price')
                    break
                #get_loc
                XY = get_loc(driver,Plink)
                if not XY:
                    log(Plink + ' have no loc')
                    break
                lat, long = XY[0], XY[1]
                #get_Area & CYear
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
                    'type' : type,
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
                    log(str(insert_counter) + " Case inserted"+ " & "+'Case '+ str(Pcases.index(Pcase)+1) + 'th inserted')
                else: 
                    log(Plink + ' is duplicate')
            driver.quit()
            log(landuse+', '+type+' UPDATED!')
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
                Plink = 'https://divar.ir'+ Pcase.get('href')
                driver = start_driver()
                driver.get(Plink)
                time.sleep(5)
                #get_mortgage, rent, area, yeare
                soup1 = BeautifulSoup(driver.page_source, 'html.parser')
                prices = soup1.find_all('div', class_ = "kt-base-row kt-base-row--large kt-unexpandable-row")
                if not soup1.find_all('input' , class_= "kt-range-slider__input"):
                    for a in prices: 
                        p = re.search(r'\d[\d\u066C]*',a.get_text())
                        if p and re.match('1+[\u066C+1+]+', p.group()):
                            log(Plink + ' have wrong price')
                            break
                        elif p and "ودیعه" in a.get_text():  
                            p = p.group().replace('\u066C', '')
                            mortgage = int(p)
                        elif p and "اجاره" in a.get_text():
                            p = p.group().replace('\u066C', '')
                            rent = int(p)
                        elif not p and "ودیعه" in a.get_text():
                                mortgage = 0
                        elif not p and "اجاره" in a.get_text():
                                rent = 0
                        elif (not p) and ("ودیعه" in a.get_text()) and ("اجاره" in a.get_text()):
                            pass
                    FArea = soup1.find_all("table", class_= "kt-group-row")[0]
                    F = FArea.get_text('p').split('p')
                    for i in range(len(F)):
                        if 'متراژ' in F[i]:
                            Area = F[int(i+ (len(F)/2))]
                        elif 'ساخت' in F[i]:
                            CYear = F[int(i+(len(F)/2))]
                elif soup1.find_all('input' , class_= "kt-range-slider__input"):
                    prices = soup1.find_all('td' , class_= 'kt-group-row-item kt-group-row-item__value kt-group-row-item--info-row')
                    Area = prices[0].get_text()
                    CYear = prices[1].get_text()
                    unit = 0
                    if 'میلیون' in prices[3].get_text():
                        unit = 1000000
                    elif 'میلیارد' in prices[3].get_text():
                        unit = 1000000000
                    elif 'هزار' in prices[3].get_text():
                        unit = 1
                    if re.search(r'(\d+\.*\d*)', prices[3].get_text()):
                        mortgage = float(re.search(r'(\d+\.*\d*)', prices[3].get_text()).group().split(' ')[0])*unit
                    else:
                        mortgage = 0
                    if 'میلیون' in prices[4].get_text():
                        unit = 1000000
                    elif 'میلیارد' in prices[4].get_text():
                        unit = 1000000000
                    elif 'هزار' in prices[4].get_text():
                        unit = 1
                    if re.search(r'(\d+\.*\d*)', prices[4].get_text()):
                        rent = float(re.search(r'(\d+\.*\d*)', prices[4].get_text()).group().split(' ')[0])*unit
                    else:
                        rent = 0
                price = (mortgage + (rent*30))/int(Area)
                if not price or price<0:
                    log(Plink + ' have wrong price')
                    break
                
                #get_loc
                XY = get_loc(driver,Plink)
                if not XY:
                    log(Plink + ' have no loc')
                    break
                lat , long = XY[0],XY[1]
                #get_mahale1
                mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                mahale = mahale_text.get_text().split("\u060C")[1]
                #get_exp
                exp = get_exp(soup1)
                
                #output
                output = {
                    'landuse': landuse,
                    'type' : type,
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
                    log(str(insert_counter) + " Case inserted"+ " & "+'Case '+ str(Pcases.index(Pcase)+1) + 'th inserted')
                else: 
                    log(Plink + ' is duplicate')
            driver.quit()
            log(landuse+', '+type+' UPDATED!')       
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
                time.sleep(5)
                #get_price, area
                soup1 = BeautifulSoup(driver.page_source, 'html.parser')
                prices = soup1.find_all('div', class_ = "kt-base-row kt-base-row--large kt-unexpandable-row")
                for a in prices:
                    if "قیمت کل" in a.get_text():
                        p = re.search(r'\d[\d\u066C]*',a.get_text()).group()
                        if re.match('1+[\u066C+1+]+', p):
                            log(Plink + ' have wrong price')
                            break
                    elif "قیمت هر متر" in a.get_text():
                        p = re.search(r'\d[\d\u066C]*',a.get_text()).group()
                        if not re.match('1+[\u066C+1+]+', p):
                            p = p.replace('\u066C', '')
                            price = int(p)
                        else:
                            log(Plink + ' have wrong price')
                    elif "متراژ" in a.get_text():
                        p = re.search(r'\d[\d\u066C]*',a.get_text()).group()
                        p = p.replace('\u066C', '')
                        Area = int(p)
                if not price:
                    log(Plink + ' have no price')
                    break
                #get_loc
                XY = get_loc(driver,Plink)
                if not XY:
                    log(Plink + ' have no loc')
                    break
                lat, long = XY[0], XY[1]
                #get_mahale
                mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                mahale = mahale_text.get_text().split("\u060C")[1]
                #get_exp
                exp = get_exp(soup1)
                #output
                output = {
                    'landuse': landuse, 
                    'type' : type, 
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
                    log(str(insert_counter) + " Case inserted"+ " & "+'Case '+ str(Pcases.index(Pcase)+1) + 'th inserted')
                else: 
                    log(Plink + ' is duplicate')
            driver.quit()
            log(landuse+', '+type+' UPDATED!')
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
                time.sleep(5)
                #get_price
                soup1 = BeautifulSoup(driver.page_source, 'html.parser')
                prices = soup1.find_all('div', class_ = "kt-base-row kt-base-row--large kt-unexpandable-row")
                for a in prices:
                    if "قیمت کل" in a.get_text():
                        p = re.search(r'\d[\d\u066C]*',a.get_text())
                        if p and re.match('1+[\u066C+1+]+', p.group()):
                            log(Plink + ' have wrong price')
                            break
                    elif "قیمت هر متر" in a.get_text():
                        p = re.search(r'\d[\d\u066C]*',a.get_text()).group()
                        if not re.match('1+[\u066C+1+]+', p):
                            p = p.replace('\u066C', '')
                            price = int(p)
                        else:
                            price = None
                            log(Plink + ' have wrong price')
                if not price:
                    log(Plink + ' have no price') 
                    break
                #get_loc
                XY = get_loc(driver,Plink)
                if not XY:
                    log(Plink + ' have no loc')
                lat, long = XY[0], XY[1]
                #get_Area & CYear
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
                    'type' : type ,
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
                    log(str(insert_counter) + " Case inserted"+ " & "+'Case '+ str(Pcases.index(Pcase)+1) + 'th inserted')
                else: 
                    log(Plink + ' is duplicate')

                
            driver.quit()
            log(landuse+', '+type+' UPDATED!')
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
                time.sleep(5)
                soup1 = BeautifulSoup(driver.page_source, 'html.parser')
                log('soap1 is deffined')
                if 'اجارهٔ دفاتر صنعتی، کشاورزی و تجاری' in soup1.find_all('span', class_= "kt-breadcrumbs__action-text")[2]:
                    log(Plink + 'indasterial Case')
                    pass
                else:
                    #get_price & get_Area & get_CYear
                    if not soup1.find_all('input' , class_= "kt-range-slider__input"):
                        prices = soup1.find_all('div', class_ = "kt-base-row kt-base-row--large kt-unexpandable-row")
                        for a in prices: 
                            p = re.search(r'\d[\d\u066C]*',a.get_text())
                            if p and re.match('1+[\u066C+1+]+', p.group()):
                                log(Plink + ' have wrong price')
                                break
                            elif not p and "ودیعه" in a.get_text() and "اجاره" in a.get_text():
                                pass
                            elif p and "ودیعه" in a.get_text():  
                                p = p.group().replace('\u066C', '')
                                mortgage = int(p)
                            elif not p and "ودیعه" in a.get_text():
                                    mortgage = 0
                            elif p and "اجاره" in a.get_text():
                                p = p.group().replace('\u066C', '')
                                rent = int(p)
                            elif not p and "اجاره" in a.get_text():
                                    rent = 0
                        FArea = soup1.find_all("table", class_= "kt-group-row")[0]
                        F = FArea.get_text('p').split('p')
                        for i in range(len(F)):
                            if 'متراژ' in F[i]:
                                Area = F[int(i+ (len(F)/2))]
                            elif 'ساخت' in F[i]:
                                CYear = F[int(i+(len(F)/2))]
                    elif soup1.find_all('input' , class_= "kt-range-slider__input"):
                        prices = soup1.find_all('td' , class_= 'kt-group-row-item kt-group-row-item__value kt-group-row-item--info-row')
                        Area = prices[0].get_text()
                        CYear = prices[1].get_text()
                        unit = 0
                        if 'میلیون' in prices[3].get_text():
                            unit = 1000000
                        elif 'میلیارد' in prices[3].get_text():
                            unit = 1000000000
                        elif 'هزار' in prices[3].get_text():
                            unit = 1
                        if re.search(r'(\d+\.*\d*)', prices[3].get_text()):
                            mortgage = float(re.search(r'(\d+\.*\d*)', prices[3].get_text()).group().split(' ')[0])*unit
                        else:
                            mortgage = 0
                        if 'میلیون' in prices[4].get_text():
                            unit = 1000000
                        elif 'میلیارد' in prices[4].get_text():
                            unit = 1000000000
                        elif 'هزار' in prices[4].get_text():
                            unit = 1
                        if re.search(r'(\d+\.*\d*)', prices[4].get_text()):
                            rent = float(re.search(r'(\d+\.*\d*)', prices[4].get_text()).group().split(' ')[0])*unit
                        else:
                            rent = 0
                    #get_loc
                    price = (mortgage + (rent*30))/int(Area)
                    if not price or price<0:
                        log(Plink + ' have no price')
                    XY = get_loc(driver,Plink)
                    if not XY:
                        log(Plink + ' have no loc')
                    lat , long = XY[0],XY[1]
                    #get_mahale1
                    mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                    mahale = mahale_text.get_text().split("\u060C")[1]
                    #get_exp
                    exp = get_exp(soup1)
                    #output
                    output = {
                        'landuse': landuse,
                        'type' : type,
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
                        log(str(insert_counter) + " Case inserted"+ " & "+'Case '+ str(Pcases.index(Pcase)+1) + 'th inserted')
                    else: 
                        log(Plink + ' is duplicate')
            driver.quit()
            log(landuse+', '+type+' UPDATED!')
        case _ :
            raise ValueError('input argument is wrong')                

def cdt(lu, typ):
    if propertyModel.objects.filter(landuse=lu,type= typ):
        count = propertyModel.objects.filter(landuse=lu, type=typ).count()
        lastupdate = propertyModel.objects.filter(landuse=lu ,type=typ).last().date_time
    else:
        count = 0
        lastupdate = "بروز رسانی نشده"
    return [count, lastupdate]
