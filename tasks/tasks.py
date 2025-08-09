from celery import shared_task
from updateData.services import update


@shared_task
def updatedata():
    update('res', 'buy')
    update('res', 'rent')
    update('resland', 'buy')
    update('com', 'buy')
    update('com', 'rent')
