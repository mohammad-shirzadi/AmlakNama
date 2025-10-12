from celery import shared_task
from .celery import app
from updateData.services import update


@shared_task
def periodic_updatedata():
    update('res', 'buy')
    update('res', 'rent')
    update('resland', 'buy')
    update('com', 'buy')
    update('com', 'rent')

@app.task
def updatedata(land_typs):
    for land_typ in land_typs:
        (land, typ) = land_typ.split('-')
        update(land, typ)
