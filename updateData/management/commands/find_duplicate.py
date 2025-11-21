from django.core.management import BaseCommand
from updateData.models import propertyModel

class Command(BaseCommand):    
    def handle(self,*args, **kwarg):
        duplicates = []
        all_data = propertyModel.objects.all()
        links = [(data.link[-8:], data.case_id) for data in all_data]
        links.sort()
        for i in range(len(links)-1):
            if links[i][0] == links[i+1][0]:
                duplicates.append(links[i])
        print(duplicates ,end=", ")
        print("\n" + 100*"-")
        if input('delete all duplicates?? Yes/[n] ') == 'Yes':
            for duplicate in duplicates:
                case_ = propertyModel.objects.filter(case_id=duplicate[1]).first()
                if case_:
                    case_.delete()
                    print(duplicate)