#-*- coding: UTF-8 -*-

from django.shortcuts import render
from .services import createmap,message

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
    class messageSeerializer(serializers.ModelSerializer):
        class meta:
            model = masages
            field = "__all__"
            
    def get(self, request):
        m = ''    
        context = {
            "Page" : 3,
            "m" : m
        }
        return render(request, 'explore/contactus.html', context)

    def post(self, request):
        dataserialized = self.messageSeerializer(data=request.data)
        dataserialized.is_valid(raise_exception=True)

        try:
            response = message(
                name=dataserialized.validated_data.get('name'),
                email=dataserialized.validated_data.get('email'),
                txtmessage=dataserialized.validated_data.get('txtmessage')
            )
        except:
            response = "مشکلی به وجود آمده!  پیام ارسال نشد"

        context = {
            "Page" : 3,
            "m" : response
        }
        return render(request, 'explore/contactus.html', context)

