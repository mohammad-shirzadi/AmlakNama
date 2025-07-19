#-*- coding: UTF-8 -*-

from rest_framework.views import APIView

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
ALLTILE = ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"]



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

    mp = Pgdf.query(f'landuse == "{lu}" and ptype == "{typ}"'+ txt)
    fmp = Pgdf.query(f'landuse == "{lu}" and ptype == "{typ}"')

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
    regmeanprice = mp.pivot_table('price','reg_no')
    reglist = list(regmeanprice.index)
    regmean = []
    for i in range(len(regmeanprice.values.tolist())):
        regmean.append(regmeanprice.values.tolist()[i][0])
    maxp = numpy.max(lp)
    minp = numpy.min(lp)
    meanp = numpy.mean(lp)
    d = {
        'RegionList' : numpy.unique(lr),
        'RNList' : reglist,
        'RMList' : regmean,
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



class homeAPI(APIView):
    
    global LU , TYP , REG ,I, ALLTILE
    
    def get(self, request):
        dt = createmap(lu=LU,typ=TYP,reg=REG,tile=I)
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
            'Tiles' : ALLTILE,
            'ActiveTile' : I,
            'RNList' : dt['RNList'],
            'RMList' : dt['RMList'],
        }
        
        return render(request, 'explore/index.html', context)

    def post(self, request):
        
        LU = request.POST.get('land') if request.POST.get('land') else 'res'
        TYP = request.POST.get('typ') if request.POST.get('typ') else 'buy'
        REG = int(request.POST.get('reg')) if request.POST.get('reg') else 0
        I = request.POST.get('bgmp') if request.POST.get('bgmp') else "CartoDB positron"
        
        if LU == 'resland' and TYP == "rent":
            TYP = 'buy'
        
        if not request.POST.get('bgmp') and request.POST.get('bgmp') in ALLTILE:
            I = "CartoDB positron"
        
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
            'Tiles' : ALLTILE,
            'ActiveTile' : I,
            'RNList' : dt['RNList'],
            'RMList' : dt['RMList'],
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

