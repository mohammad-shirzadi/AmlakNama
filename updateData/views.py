#-*- coding: UTF-8 -*-

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from updateData.models import propertyModel
from django.contrib.admin.views.decorators import staff_member_required
#from django.middleware.csrf import CsrfViewMiddleware


#___________________________________

from selenium import webdriver
#from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.chrome.options import Options
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from  bs4 import BeautifulSoup
import requests

import re
import time
import os
import datetime

#___________________________________________________




def index(request):
    context = {}
    return render(request, 'updateData/index.html', context)


LOG = ''

@staff_member_required
def updatePg(request):
    #TODO create variable that show the upadate is running and stope whene html closed(?!)
    #TODO cheang the log save file
    def log(a):
        global LOG
        LOG = str(datetime.datetime.today())+ ':   ' + a + '\n'
        with open('log.txt', 'a') as logfile:
            logfile.write(LOG)
        return LOG
    
    print(LOG)

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

        result = propertyModel.objects.filter(landuse=landuse, type=type, price=price, area=area, Cyear=Cyear, mortgage=mortgage, rent=rent, lat=lat, lon=lon, mahale=mahale, exp=exp, link=link, date_time=date_time)
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
            propertyModel.objects.create(landuse=landuse, type=type, price=price, area=area, Cyear=Cyear, mortgage=mortgage, rent=rent, lat=lat, lon=lon, mahale=mahale, exp=exp, link=link, date_time=date_time)
        except Exception as error:
            log(str(error)+"---"+ str(output))
            pass

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

        if os.path.isfile(r"/home/mohammad/CS50P/propertyprice/ECD.txt"):
            with open(r"/home/mohammad/CS50P/propertyprice/ECD.txt", 'r') as file:
                PathECDM = file.read().strip()
        else:
            PathECDM = EdgeChromiumDriverManager().install()
            with open(r"/home/mohammad/CS50P/propertyprice/ECD.txt", 'w') as file:
                file.write(PathECDM)
 
        edge_options = Options()
        edge_options.headless = True
        edge_options.add_argument("--headless=new")  # اضافه کردن حالت headless جدید
        edge_options.add_argument("--disable-gpu")  # غیرفعال‌سازی GPU
        edge_options.add_argument("--window-size=1920x1080")  # تنظیم سایز پنجره
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
                    pass
            else:
                pass
        raise ReferenceError('status_cod is not 200')

    def get_exp(soup1):
        explink = soup1.find_all('h1', class_ = "kt-page-title__title kt-page-title__title--responsive-sized")[0].get_text()
        explink = explink
        return explink

    def get_loc(soup1):
        baladlinks = soup1.find_all('a', class_ = "map-cm__attribution map-cm__button")  
        if baladlinks : 
            baladlink = baladlinks[0]
            baladlink = baladlink.get('href')
            (lat,long) = re.search(r"latitude=(\d*\.\d*)&longitude=(\d*\.\d*)", baladlink).groups()
            x_y =[float(lat),float(long)]
            return x_y
        else:
            x_y = None
            log(f" not have lat,long argument")
            return x_y

    def update(landuse , type):
        log('update(%s, %s) is run'% (landuse,type))
        match (landuse, type):
            case ('res','buy'):
                try:
                    insert_counter = 0
                    url = 'https://divar.ir/s/tehran/buy-apartment'# just appartment, not villa 
                    Pcases = PropertyCases(url)
                    log('get'+ str(len(Pcases)) +' Pcasses')
                    if Pcases:
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
                            log('driver get links')
                            Ppage = driver.page_source
                            soup1 = BeautifulSoup(Ppage, 'html.parser')
                            log('soap1 is deffined')
                            #get_price
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
                            if price:
                                #get_loc
                                XY = get_loc(soup1)
                                if XY:
                                    lat, long = XY[0], XY[1]
                                    #get_Area & CYear
                                    FArea = soup1.find_all('table', class_ = "kt-group-row")
                                    if len(FArea) == 2:
                                        a = FArea[0]
                                        d = a.get_text('thead').split('thead')
                                        Area = d[3]
                                        CYear = d[4]
                                    #get_mahale
                                    mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                                    mahale = mahale_text.get_text().split("\u060C")[1]
                                    mahale = mahale
                                    #get_exp
                                    exp = get_exp(soup1)
                                    output = {'landuse': landuse , 'type' : type , 'price' : price, 'Area': int(Area) , 'CYear': CYear , 'mortgage': 0 , 'rent': 0 , 'lat': lat , 'lon' : long , 'mahale': mahale , 'exp': exp, 'link' : Plink , 'date_time' : datetime.datetime.today()}
                                    if not_duplicate(output):
                                        insert(output)
                                        insert_counter = insert_counter + 1
                                        log(str(insert_counter) + " Case inserted"+ " & "+'Case '+ str(Pcases.index(Pcase)+1) + 'th inserted')
                                    else: 
                                        log(Plink + ' is duplicate')
                                else:
                                    log(Plink + ' have no loc')
                            else:
                                log(Plink + ' have no price')
                        driver.quit()
                        log(landuse+', '+type+' UPDATED!')
                    else:
                        pass
                except Exception:
                    log(str(Exception) + Plink)
            case ('res', 'rent'):
                try:
                    insert_counter = 0
                    url = 'https://divar.ir/s/tehran/rent-residential'
                    Pcases = PropertyCases(url)
                    log('get'+ str(len(Pcases)) +' Pcasses')
                    if Pcases:
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
                            log('driver get links')
                            Ppage = driver.page_source
                            soup1 = BeautifulSoup(Ppage, 'html.parser')
                            log('soap1 is deffined')
                            #get_price & get_Area & get_CYear
                            prices = soup1.find_all('div', class_ = "kt-base-row kt-base-row--large kt-unexpandable-row")
                            if not soup1.find_all('input' , class_= "kt-range-slider__input"):
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
                            if price and price>0:
                                XY = get_loc(soup1)
                                if XY:
                                    lat , long = XY[0],XY[1]
                                    #get_mahale1
                                    mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                                    mahale = mahale_text.get_text().split("\u060C")[1]
                                    mahale = mahale 
                                    #get_exp
                                    exp = get_exp(soup1)
                                    output = {'landuse': landuse , 'type' : type , 'price' : price, 'Area': int(Area) , 'CYear': CYear , 'mortgage': mortgage , 'rent': rent , 'lat': lat , 'lon' : long , 'mahale': mahale , 'exp': exp, 'link' : Plink , 'date_time' : datetime.datetime.today()}
                                    if not_duplicate(output):
                                        insert(output)
                                        insert_counter = insert_counter + 1
                                        log(str(insert_counter) + " Case inserted"+ " & "+'Case '+ str(Pcases.index(Pcase)+1) + 'th inserted')
                                    else: 
                                        log(Plink + ' is duplicate')
                                else:
                                    log(Plink + ' have no loc')
                            else:
                                log(Plink + ' have no price')
                        driver.quit()
                        log(landuse+', '+type+' UPDATED!')
                    else:
                        pass
                except Exception:
                    log(str(Exception) + Plink)
            case ('resland', 'buy'):
                try:
                    insert_counter = 0
                    url = 'https://divar.ir/s/tehran/buy-old-house'
                    Pcases = PropertyCases(url)
                    log('get'+ str(len(Pcases)) +' Pcasses')
                    if Pcases:
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
                            log('driver get links')
                            Ppage = driver.page_source
                            soup1 = BeautifulSoup(Ppage, 'html.parser')
                            log('soap1 is deffined')
                            #get_price
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

                            log(Plink)
                            if price:
                                #get_loc
                                XY = get_loc(soup1)
                                if XY:
                                    lat, long = XY[0], XY[1]
                                    #get_Area & CYear
                                    #get_mahale
                                    mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                                    mahale = mahale_text.get_text().split("\u060C")[1]
                                    mahale = mahale
                                    #get_exp
                                    exp = get_exp(soup1)
                                    output = {'landuse': landuse , 'type' : type , 'price' : price, 'Area': int(Area) , 'CYear': 0 , 'mortgage': 0 , 'rent': 0 , 'lat': lat , 'lon' : long , 'mahale': mahale , 'exp': exp, 'link' : Plink , 'date_time' : datetime.datetime.today()}
                                    if not_duplicate(output):
                                        insert(output)
                                        insert_counter = insert_counter + 1
                                        log(str(insert_counter) + " Case inserted"+ " & "+'Case '+ str(Pcases.index(Pcase)+1) + 'th inserted')
                                    else: 
                                        log(Plink + ' is duplicate')
                                else:
                                    log(Plink + ' have no loc')
                            else:
                                log(Plink + ' have no price')
                        driver.quit()
                        log(landuse+', '+type+' UPDATED!')
                    else:
                        pass
                except Exception:
                    log(str(Exception) + Plink)
            case ('com', 'buy'):
                try:
                    insert_counter = 0
                    url = 'https://divar.ir/s/tehran/buy-commercial-property'
                    Pcases = PropertyCases(url)
                    log('get'+ str(len(Pcases)) +' Pcasses')
                    if Pcases:
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
                            log('driver get links')
                            Ppage = driver.page_source
                            soup1 = BeautifulSoup(Ppage, 'html.parser')

                            log('soap1 is deffined')
                            #get_price
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
                            if price:
                                #get_loc
                                XY = get_loc(soup1)
                                if XY:
                                    lat, long = XY[0], XY[1]
                                    #get_Area & CYear
                                    FArea = soup1.find_all('table', class_ = "kt-group-row")
                                    a = FArea[0]
                                    d = a.get_text('thead').split('thead')
                                    Area = d[3]
                                    CYear = d[4]
                                    #get_mahale
                                    mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                                    mahale = mahale_text.get_text().split("\u060C")[1]
                                    mahale = mahale
                                    #get_exp
                                    exp = get_exp(soup1)
                                    output = {'landuse': landuse , 'type' : type , 'price' : price, 'Area': int(Area) , 'CYear': CYear , 'mortgage': 0 , 'rent': 0 , 'lat': lat , 'lon' : long , 'mahale': mahale , 'exp': exp, 'link' : Plink , 'date_time' : datetime.datetime.today()}
                                    if not_duplicate(output):
                                        insert(output)
                                        insert_counter = insert_counter + 1
                                        log(str(insert_counter) + " Case inserted"+ " & "+'Case '+ str(Pcases.index(Pcase)+1) + 'th inserted')
                                    else: 
                                        log(Plink + ' is duplicate')
                                else:
                                    log(Plink + ' have no loc')
                            else:
                                log(Plink + ' have no price') 
                        driver.quit()
                        log(landuse+', '+type+' UPDATED!')
                    else:
                        pass
                except Exception:
                    log(str(Exception) + Plink)
            case ('com', 'rent'):
                try:
                    insert_counter = 0
                    url = 'https://divar.ir/s/tehran/rent-commercial-property'
                    Pcases = PropertyCases(url)
                    log('get'+ str(len(Pcases)) +' Pcasses')
                    if Pcases:
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
                            log('driver get links')
                            Ppage = driver.page_source
                            soup1 = BeautifulSoup(Ppage, 'html.parser')
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
                                if price and price>0:
                                    XY = get_loc(soup1)
                                    if XY:
                                        lat , long = XY[0],XY[1]
                                        #get_mahale1
                                        mahale_text = soup1.find_all('div', class_ = "kt-page-title__subtitle kt-page-title__subtitle--responsive-sized")[0]
                                        mahale = mahale_text.get_text().split("\u060C")[1]
                                        mahale = mahale
                                        #get_exp
                                        exp = get_exp(soup1)
                                        output = {'landuse': landuse , 'type' : type , 'price' : price, 'Area': int(Area) , 'CYear': CYear , 'mortgage': mortgage , 'rent': rent , 'lat': lat , 'lon' : long , 'mahale': mahale , 'exp': exp, 'link' : Plink , 'date_time' : datetime.datetime.today()}
                                        if not_duplicate(output):
                                            insert(output)
                                            insert_counter = insert_counter + 1
                                            log(str(insert_counter) + " Case inserted"+ " & "+'Case '+ str(Pcases.index(Pcase)+1) + 'th inserted')
                                        else: 
                                            log(Plink + ' is duplicate')
                                    else:
                                        log(Plink + ' have no loc')
                                else:
                                    log(Plink + ' have no price')
                        driver.quit()
                        log(landuse+', '+type+' UPDATED!')
                    else:
                        pass
                except Exception:
                    log(str(Exception) + Plink)
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
    
    context = {
        "count_res_rent" : cdt('res','rent')[0],
        "lastupdateRR" : cdt('res','rent')[1],
        "count_res_buy" : cdt('res','buy')[0],
        "lastupdateRB" : cdt('res','buy')[1],
        "count_resland_buy" : cdt('resland','buy')[0],
        "lastupdateRlB" : cdt('resland','buy')[1],
        "count_com_buy" : cdt('com','buy')[0],
        "lastupdateCB" : cdt('com','buy')[1],
        "count_com_rent" : cdt('com','rent')[0],
        "lastupdateCR" : cdt('com','rent')[1],
        "inlog" : LOG
    }
    print(request.POST)
    if request.method == "POST" and request.POST.get('a'):
        return JsonResponse({'log': LOG})
    
    if request.method == 'POST':
        if request.POST.get('res-rent'):
            update('res','rent')
            context['log'] = "update('res','rent') is done"

        if request.POST.get('res-buy'):
            update('res','buy')
            context['log'] = "update('res','buy') is done"

        if request.POST.get('resland-buy'):
            update('resland','buy')
            context['log'] = "update('resland','buy') is done"

        if request.POST.get('com-rent'):        
            update('com','rent')
            context['log'] = "update('com','rent') is done"

        if request.POST.get('com-buy'):
            update('com','buy')
            context['log'] = "update('com','buy') is done"

    elif request.method == 'GET':
        pass

    return render(request,'admin/updatePg.html', context)



#@staff_member_required
#def update(request):
#    pass