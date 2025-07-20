#-*- coding: UTF-8 -*-

from django.shortcuts import render
from .services import createmap
from  explore.models import masages

from rest_framework.views import APIView
from rest_framework import serializers




class homeAPI(APIView):
        
    class paramSerializer(serializers.Serializer):
        land = serializers.CharField(required= False, max_length = 8,default='res')
        typ = serializers.CharField(required= False,max_length = 4, default='buy')
        reg = serializers.IntegerField(required= False, default=0)
        bgmp = serializers.CharField(required= False, default='CartoDB positron')


    def get(self, request):
        print(request.query_params)
        data = self.paramSerializer(data=request.query_params)
        data.is_valid(raise_exception=True)
        map = createmap(
            lu=data.validated_data.get('land'),
            typ=data.validated_data.get('typ'),
            reg=data.validated_data.get('reg'),
            tile=data.validated_data.get('bgmp')
            )

        return render(request, 'explore/index.html', map)




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

