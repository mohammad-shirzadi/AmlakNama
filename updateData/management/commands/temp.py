from updateData.models import propertyModel
from updateData.services import Property, cards, log

import requests

from django.core.management import BaseCommand
from updateData.models import propertyModel

class Command(BaseCommand):    
    def handle(self, *args, **kwarg):
        check_need_cases = propertyModel.objects.filter(price__lte=999)
        for check_need_case in check_need_cases:
            try:
                print(f"link: {check_need_case.link[-8:]}, price: {check_need_case.price}")
                #if input("countinue?([Yes]/n) ") == "n":
                #    break
                property_case = Property(check_need_case.link, check_need_case.landuse, check_need_case.ptype) 
                resp = property_case.update(field=['price'])
                print(resp)
            except Exception:
                    continue