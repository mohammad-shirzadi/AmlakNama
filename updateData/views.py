#-*- coding: UTF-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .services import log, logreader, update, cdt, stop_update, status_reader



@staff_member_required
def updatePg(request):
    #TODO create variable that show the upadate is running and stope whene html closed(?!) 

    if request.method == 'POST' and request.POST.get('land_typ'):
        land_types = request.POST.getlist('land_typ')
        for land_typ in land_types:
            [land, typ] = land_typ.split('-')
            try:
                update(land, typ)
                log(f"update('{land}','{typ}') is done")
            except Exception as ex:
                log(str(ex)+'----')
                raise Exception
        
    elif request.method == 'POST' and request.POST.get('LogKey'):
        return JsonResponse({'log': logreader()})   
    elif request.POST.get('PCStatus'):
        return JsonResponse({'PCStatus': status_reader()})

    elif request.method == 'GET':
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



@staff_member_required
def stop_updatePg(request):
    if request.POST.get('stop'):
        stop_update()
    return render(request,'admin/updatePg.html')