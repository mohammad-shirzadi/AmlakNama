from updateData.models import propertyModel
from updateData.services import Property, log

from django.core.management import BaseCommand
from updateData.models import propertyModel

class Command(BaseCommand):    
    def handle(self, *args, **kwarg):
        check_need_cases = propertyModel.objects.filter(price__lte=999)
        property_case = False

        for check_need_case in check_need_cases:
            try:
                print(f"token: {check_need_case.link[-8:]}, price: {check_need_case.price}, rent: {check_need_case.rent}, mortgage: {check_need_case.mortgage}")
                property_case = Property(check_need_case.link[-8:], check_need_case.landuse, check_need_case.ptype) 
                property_case.load(field=['price'])
                print(f"token: {property_case.token}, price: {property_case.price}, rent: {property_case.rent}, mortgage: {property_case.mortgage}")
                resp = property_case.update()
                print(resp)
                print('\n')

            except Exception as exc:
                print(exc)
                if property_case:
                    if '404' in str(exc) or 'industry-agriculture-business' in str(exc):
                        propertycase = propertyModel.objects.get(link__iendswith= property_case.token)
                        propertycase.delete()

                    elif input('do you want to delete this case? [y]/n ') != 'n':
                        propertycase = propertyModel.objects.get(link__iendswith= property_case.token)
                        propertycase.delete()
                    print(f'land-type: [{property_case.landuse}-{property_case.ptype}], message: deleted., token: {property_case.token}')
                continue
