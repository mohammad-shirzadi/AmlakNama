#-*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from .services import logreader, cdt, status_reader
from tasks.tasks import updatedata
#import threading

from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated



class updateData_API(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
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
            "inlog" : logreader()
        }

        return render(request,'admin/updatePg.html',context)

    def post(self, request):
        if request.POST.get('land_typ'):
            land_types = request.POST.getlist('land_typ')
            updatedata.delay(land_types) # type: ignore
            
            #for land_typ in land_types:
            #    [land, typ] = land_typ.split('-')
            #   update(land, typ)
                
                #threading.Thread(target=ThradedUpdate, args=(land,typ)).start()
            return render(request,'admin/updatePg.html')
        
        elif request.POST.get('LogKey'):
            return JsonResponse({'log': logreader()})   
        
        elif request.POST.get('PCStatus'):
            return JsonResponse({'PCStatus': status_reader()})
        

