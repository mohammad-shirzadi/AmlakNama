from django.core.management import BaseCommand
from updateData.models import propertyModel

class Command(BaseCommand):    
    def handle(self,*args, **kwarg):
        duplicates = []
        all_data = propertyModel.objects.all().order_by('link')
        links = [data.link[-8:] for data in all_data]
        for i in range(len(links)-1):
            if links[i] == links[i+1]:
                duplicates.append(links[i])
        for duplicate in duplicates:
            print(all_data[links.index(duplicate)].case_id,end=", ")
            print(30*'_')
        if input('delete all duplicates?? Yes/[n] ') == 'Yes':
            for duplicate in duplicates:
                caseid = all_data[links.index(duplicate)].case_id
                case_ = propertyModel.objects.filter(case_id=caseid).first()
                if case_:
                    case_.delete()
                    print(caseid)