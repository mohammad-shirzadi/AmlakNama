#-*- CODING: UTF-8 -*-
from django.db import models



class propertyModel(models.Model):
    case_id = models.AutoField(primary_key=True,unique=True,editable=False)
    landuse = models.CharField(max_length=10)
    ptype= models.CharField(max_length=10)
    price = models.IntegerField("قیمت در ازا هر مترمربع")
    area = models.IntegerField("مساحت")
    Cyear = models.CharField("سال ساخت")
    mortgage = models.IntegerField("رهن")
    rent = models.IntegerField("اجاره")
    lat = models.FloatField()
    lon = models.FloatField()
    mahale = models.CharField("محله",max_length=100)
    exp = models.TextField("توضیحات",max_length=500)
    link = models.CharField(max_length=500)
    date_time = models.DateTimeField(max_length=500)
    shape = models.BooleanField(default=False)

    def __str__(self):
        return str(self.area) + 'متری, ' + self.mahale + ', متری' + str(self.price) + 'میلیون'
    def location(self):
        return [str(self.lon)+', '+ str(self.lat)] 

