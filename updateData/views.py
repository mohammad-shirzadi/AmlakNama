#-*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .services import log, logreader, update, cdt, stop_update, STOPSIGN



@staff_member_required
def updatePg(request):
    #TODO create variable that show the upadate is running and stope whene html closed(?!) 
    global STOPSIGN

    if request.method == 'POST':
        log(request.POST)

        STOPSIGN = False

        if request.POST.get('LogKey'):
            return JsonResponse({'log': logreader()})
        
        if request.POST.get('res-rent'):
            try:
                update('res','rent')
                context['log'] = "update('res','rent') is done"
            except Exception as erore:
                log(str(erore)+'-')
        
        if request.POST.get('res-buy'):
            try:
                update('res','buy')
                context['log'] = "update('res','buy') is done"
            except Exception as erore:
                log(str(erore)+'-')

        if request.POST.get('resland-buy'):
            try:
                update('resland','buy')
                context['log'] = "update('resland','buy') is done"
            except Exception as erore:
                log(str(erore)+'-')

        if request.POST.get('com-rent'):        
            try:
                update('com','rent')
                context['log'] = "update('com','rent') is done"
            except Exception as erore:
                log(str(erore)+'-')

        if request.POST.get('com-buy'):
            try:
                update('com','buy')
                context['log'] = "update('com','buy') is done"
            except Exception as erore:
                log(str(erore)+'-')
    elif request.method == 'GET':
        STOPSIGN = False
        pass

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
    return render(request,'admin/updatePg.html', context)


def stop_updatePg(request):
    print(request.POST)
    if request.POST.get('stop'):
        stop_update()
        return render(request,'admin/updatePg.html')