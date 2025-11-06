from celery import shared_task
from .celery import app
from updateData.services import cards


@shared_task
def periodic_updatedata():
    for landuse in ['res', 'com', 'resland']:
        for ptype in ['buy','rent']:
            card = cards(landuse=landuse, ptype=ptype)
            card.update()

@app.task
def updatedata(land_typs):
    for land_typ in land_typs:
        (land, typ) = land_typ.split('-')
        card = cards(landuse=land, ptype=typ)
        card.update()
