from celery import shared_task
from updateData.services import makeshape

@shared_task
def MakeShape(modeladmin, request, queryset):
    return makeshape(modeladmin, request, queryset)


