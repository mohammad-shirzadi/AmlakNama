#-*- coding: UTF-8 -*-

from django.shortcuts import render
from .services import createmap
from  explore.models import masages

from rest_framework.views import APIView




LU = 'res'
TYP = 'buy'
REG = 0
I = "CartoDB positron"
ALLTILE = ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"]


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


class exploreAPI(APIView):
    def get(self, request):
        pass

    def post(self, request):
        pass


class contactusAPI(APIView):
    
    def get(self, request):
        m = ''    
        context = {
            "Page" : 3,
            "m" : m
        }
        return render(request, 'explore/contactus.html', context)

    def post(self, request):
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

