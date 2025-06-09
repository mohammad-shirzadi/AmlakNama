#-*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .services import log, update,cdt
import threading


def threaded_update(lu,typ):
    try:
        update('res','rent')
        log(f"update('{lu}', '{typ}') is done")
    except Exception as erore:
        log(str(erore)+'-')

@staff_member_required
def updatePg(request):
    #TODO create variable that show the upadate is running and stope whene html closed(?!)


    def logreader():
        with open("log",'r') as file:
            logtxt = file.readlines()
            if not logtxt: 
                logtxt = ['']
            return logtxt[-1]


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

    if request.method == "POST" and request.POST.get('a'):
        return JsonResponse({'log': logreader()})
    
    if request.method == 'POST':
        if request.POST.get('res-rent'):
            threading.Thread(target=threaded_update,args=('res','rent')).start()
        if request.POST.get('res-buy'):
            threading.Thread(target=threaded_update,args=('res','buy')).start()
        if request.POST.get('resland-buy'):
            threading.Thread(target=threaded_update,args=('resland','buy')).start()
        if request.POST.get('com-rent'):        
            threading.Thread(target=threaded_update,args=('com','rent')).start()
        if request.POST.get('com-buy'):
            threading.Thread(target=threaded_update,args=('com','buy')).start()
    elif request.method == 'GET':
        pass

    return render(request,'admin/updatePg.html', context)


