from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping

from explore.models import MahalatTehran
from pathlib import Path


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        MTP_mapping = {
            "name_mahal" : "NAME_MAHAL",
            "reg_no" : "reg_no",
            "shape_le_1" : "Shape_Le_1", 
            "shape_area" : "Shape_Area",
            "geom" : 'MULTIPOLYGON',
        }
        MTP_shp = Path(__file__).resolve().parent.parent.parent.parent/"updateData"/"shp"/"StaticShape"/"Mahalat_Tehran.shp"

        MahalatTehran.objects.all().delete()
        lm = LayerMapping(MahalatTehran,MTP_shp,MTP_mapping,transform=False)
        lm.save(strict=True, verbose=True)