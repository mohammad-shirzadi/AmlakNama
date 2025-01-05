#-*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .functions import log, update,cdt



@staff_member_required
def updatePg(request):
    #TODO create variable that show the upadate is running and stope whene html closed(?!)


    def logreader():
        with open("log.txt",'r') as file:
            logtxt = file.readlines()
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
            try:
                update('res','rent')
                context['log'] = "update('res','rent') is done"
            except Exception as erore:
                log(erore+'-')

        if request.POST.get('res-buy'):
            try:
                update('res','buy')
                context['log'] = "update('res','buy') is done"
            except Exception as erore:
                log(erore+'-')

        if request.POST.get('resland-buy'):
            try:
                update('resland','buy')
                context['log'] = "update('resland','buy') is done"
            except Exception as erore:
                log(erore+'-')

        if request.POST.get('com-rent'):        
            try:
                update('com','rent')
                context['log'] = "update('com','rent') is done"
            except Exception as erore:
                log(erore+'-')

        if request.POST.get('com-buy'):
            try:
                update('com','buy')
                context['log'] = "update('com','buy') is done"
            except Exception as erore:
                log(erore+'-')

    elif request.method == 'GET':
        pass

    return render(request,'admin/updatePg.html', context)


