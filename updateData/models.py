#-*- CODING: UTF-8 -*-
from django.db import models



class propertyModel(models.Model):
    case_id = models.AutoField(primary_key=True,unique=True,editable=False)
    landuse = models.CharField(max_length=10)
    ptype= models.CharField(max_length=10)
    price = models.BigIntegerField("قیمت در ازا هر مترمربع")
    area = models.IntegerField("مساحت")
    Cyear = models.CharField("سال ساخت")
    mortgage = models.BigIntegerField("رهن")
    rent = models.BigIntegerField("اجاره")
    lat = models.FloatField()
    lon = models.FloatField()
    mahale = models.CharField("محله",max_length=100)
    exp = models.TextField("توضیحات",max_length=500)
    link = models.CharField(max_length=500)
    date_time = models.DateTimeField(max_length=500)
    shape = models.BooleanField(default=False)

    def __str__(self): # type: ignore
        output = {
            'landuse': self.landuse, 'ptype' : self.ptype, 'price' : self.price,
            'area': self.area,         'Cyear': self.Cyear,     'mortgage': self.mortgage,
            'rent': self.rent,         'lat': self.lat,       'lon' : self.lon,
            'mahale': self.mahale,       'exp': self.exp,       'link' : self.link[-8:],
            'date_time' : self.date_time
        }
        return str(output)
    def location(self):
        return [str(self.lon)+', '+ str(self.lat)] 

