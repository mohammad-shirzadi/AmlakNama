from celery import shared_task
from .celery import app
from updateData.services import Property


@shared_task
def periodic_updatedata():
    prop = Property()
    prop.update('res', 'buy')
    prop.update('res', 'rent')
    prop.update('resland', 'buy')
    prop.update('com', 'buy')
    prop.update('com', 'rent')

@app.task
def updatedata(land_typs):
    for land_typ in land_typs:
        prop = Property()
        (land, typ) = land_typ.split('-')
        prop.update(land, typ)
