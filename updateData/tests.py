from django.test import TestCase

import datetime
import os
import requests
from  bs4 import BeautifulSoup
import time
import re

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

# Create your tests here.

def log(a):
    global LOG
    LOG = str(datetime.datetime.today())+ ':   ' + a + '\n'
    with open('log.txt', 'a') as logfile:
        logfile.write(LOG)
    return LOG

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

def buyPrice(driver, Plink):
    driver.get(Plink)
    time.sleep(5)
    soup1 = BeautifulSoup(driver.page_source, 'html.parser')
    prices = soup1.find_all('div', class_ = "kt-base-row kt-base-row--large kt-unexpandable-row")
    price = None
    Area = None
    for a in prices:
        p = re.search(r'\d[\d\u066C]*',a.get_text())
        if not p:
            pass
        elif re.match(r'۱{1,3}(٬۱{3})+$', p.group().replace('\u066C', '')):
            log(Plink + ' have wrong price')
            return [None, None]
        elif "قیمت هر متر" in a.get_text():
            p = p.group().replace('\u066C', '')
            price = int(p)
        elif "متراژ" in a.get_text():
            p = p.group().replace('\u066C', '')
            Area = int(p)
    return [price, Area]

def rentPrice(driver, Plink):
    driver.get(Plink)
    time.sleep(5)
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
            print(p)
            if p and re.match(r'۱{1,3}(٬۱{3})+$', p.group()):
                log(Plink + ' have wrong price')
                return None
            elif p:
                m = float(p.group().split(' ')[0])*unit
            else:
                m = 0
        
            if x == 3:
                mortgage=m
            elif x == 4:
                rent=m
        return [int(mortgage), int(rent)]   
    elif not style:
        for a in prices: 
            p = re.search(r'\d[\d\u066C]*',a.get_text())
            print(p)
            if p and re.match(r'۱{1,3}(٬۱{3})+$', p.group()):
                log(Plink + ' have wrong price')
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
        return [int(mortgage), int(rent)]

def getprice(landuse, Ptype, driver, Plink ):
    match(landuse, Ptype):
        case('res', 'buy'):
            return buyPrice(driver, Plink)
        case('com', 'buy'):
            return buyPrice(driver, Plink)
        case('resland', 'buy'):
            return buyPrice(driver, Plink)
        case('res', 'rent'):
            return rentPrice(driver, Plink)
        case('com', 'rent'):
            driver.get(Plink)
            time.sleep(5)
            soup1 = BeautifulSoup(driver.page_source, 'html.parser')
            if 'اجارهٔ دفاتر صنعتی، کشاورزی و تجاری' in soup1.find_all('span', class_= "kt-breadcrumbs__action-text")[2]:
                log(Plink + 'indasterial Case')
                return None
            return rentPrice(driver, Plink)




driver = start_driver()

Plink = """
    https://divar.ir/v/%D8%A7%D9%82%D8%AF%D8%B3%DB%8C%D9%87-%DB%B1%DB%B6%DB%B0%D9%85%D8%AA%D8%B1-%DB%B3-%D8%AE-%D8%A8%D8%B1%D8%AC-%D8%A8%D8%A7%D8%BA/wZ7tpn77
"""


m = getprice('res', 'rent', driver, Plink)

print(m)
driver.quit()