from django.contrib.gis.db import models
from django.db import models as nongismodel


class MahalatTehran(models.Model):
    name_mahal = models.CharField(max_length=50)
    reg_no = models.IntegerField()
    shape_le_1 = models.FloatField()
    shape_area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326)


class MTPPolygon(models.Model):
    landuse = models.CharField(max_length=10)
    ptype= models.CharField(max_length=10)
    price = models.BigIntegerField()
    mortgage = models.BigIntegerField(default=0)
    rent = models.BigIntegerField(default=0)
    name_mahal = models.CharField(max_length=50)
    reg_no = models.IntegerField()
    geom = models.MultiPolygonField(srid=4326)


class masages(nongismodel.Model):
    name = nongismodel.CharField('نام')
    email = nongismodel.EmailField("ایمیل")
    txtmasages = nongismodel.CharField("پیام")