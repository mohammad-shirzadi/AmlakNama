#-*- coding: UTF-8 -*-

from django.shortcuts import render
import matplotlib.pyplot
from  explore.models import masages
import geopandas
import matplotlib
import folium
import numpy

LU = 'res'
TYP = 'buy'
REG = 0
I = "CartoDB positron"

def home(request):
    global LU , TYP , REG ,I
    Alltile = ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"]
     
    def createmap(lu='res',typ='buy',reg=0,tile="CartoDB positron"):
        Pgdf = geopandas.read_file(r"updateData/shp/polymean.shp")
        Tgdf = geopandas.read_file(r"updateData/shp/StaticShape/Mahalat_Tehran.shp")
        fieldR = ['NAME_MAHAL','price', 'mortgage', 'rent']
        fieldB = ['NAME_MAHAL','price']

        if reg == 0:
            txt = ''
        elif reg in range(1,23):
            txt = f'and reg_no == {reg}'
        if typ == 'buy':
            popupf = fieldB
        elif typ == 'rent':
            popupf = fieldR

        mp = Pgdf.query(f'landuse == "{lu}" and type == "{typ}"'+ txt)
        fmp = Pgdf.query(f'landuse == "{lu}" and type == "{typ}"')
    
        m = mp.explore(
            column="price",
            scheme='naturalbreaks',
            legend=False,
            k=50,
            tooltip=False,
            popup=popupf,
            legend_kwds=dict(colorebar=False),
            #name= l + '-' + t,
            tiles=tile,
            zoom_control=False,
            zoom=11
        )
        Tgdf.explore(
        m=m,
        color='None',
        tooltip=False,
        popup=['NAME_MAHAL'],
        style_kwds={
            'color':'Black',
            'weight': 1,
            }   
        )
        
        m.save(r"explore/static/explore/map/myhtml.html")

        lr = list(mp.reg_no)
        ln = list(mp.NAME_MAHAL)
        lp = list(mp.price)
        maxp = numpy.max(lp)
        minp = numpy.min(lp)
        meanp = numpy.mean(lp)
        d = {
            'RegionList' : numpy.unique(lr),
            'FRegionList' : numpy.unique(list(fmp.reg_no)),
            'NameList' : ln,
            'PriceList' : lp,
            'MaxPrice' : "{:,}".format(int(maxp)),
            'NameMaxPrice' : ln[lp.index(maxp)],
            'MeanPrice' : "{:,}".format(int(meanp)),
            'MinPrice' : "{:,}".format(int(minp)),
            'NameMinPrice' : ln[lp.index(minp)],
        }
        return d


    if request.method == "GET":
        createmap()
    elif request.method == "POST":
        if request.POST.get('res'):
            LU = 'res'
            createmap(lu=LU,typ=TYP,reg=REG,tile=I)
        elif request.POST.get('resland'):
            LU = 'resland'
            TYP = 'buy'
            createmap(lu=LU,typ=TYP,reg=REG,tile=I)
        elif request.POST.get('com'):
            LU = 'com'
            createmap(lu=LU,typ=TYP,reg=REG,tile=I)
        if request.POST.get('buy'):
            TYP = 'buy'
            createmap(lu=LU,typ=TYP,reg=REG,tile=I)
        elif request.POST.get('rent'):
            TYP = 'rent'
            if LU == "resland":
                LU = "res"
            createmap(lu=LU,typ=TYP,reg=REG,tile=I)
        if request.POST.get('reg'):
            REG = int(request.POST.get('reg'))
            createmap(lu=LU,typ=TYP,reg=REG,tile=I)
        if request.POST.get('bgmp') and request.POST.get('bgmp') in Alltile:
            I = request.POST.get('bgmp')
            createmap(lu=LU,typ=TYP,reg=REG,tile=I)       

    dt = createmap(lu=LU,typ=TYP,reg=REG,tile=I)
    
    #'RegionList' : lr,
    #'NameList' : ln,
    #'PriceList' : lp,
    #'MaxPrice' : maxp,
    #'MeanPrice' : meanp,
    #'MinPrice' : minp,

    context = {
        "Page" : 1,
        'RegionList' : dt['RegionList'],
        'FRegionList' : dt['FRegionList'],
        'NameList' : dt['NameList' ],
        'PriceList' : dt['PriceList'],
        'MaxPrice' : dt['MaxPrice' ],
        "NameMaxPrice" : dt['NameMaxPrice'],
        'MeanPrice' : dt['MeanPrice'],
        'MinPrice' : dt['MinPrice' ],
        'NameMinPrice' : dt['NameMinPrice'],
        'lu' : LU,
        'typ' : TYP,
        'reg' : REG,
        'Tiles' : Alltile,
        'ActiveTile' : I,
    }
    return render(request, 'explore/index.html', context)


def explore(request):
#TODO
    context = {
        "Page" : 2,

    }
   
    return render(request, 'explore/explore.html', context)



def contactus(request):
    m = ''
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        txtmassage = request.POST.get('massage')
        try:
            masages.objects.create(
                name=name,
                email=email,
                txtmasages=txtmassage,
            )
            m = "پیام با موفقیت ارسال شد"
        except:
            m = "مشکلی به وجود آمده!  پیام ارسال نشد"
    context = {
        "Page" : 3,
        "m" : m
    }
    return render(request, 'explore/contactus.html', context)

