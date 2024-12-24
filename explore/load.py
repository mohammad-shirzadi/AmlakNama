#loadfile
# Auto-generated `LayerMapping` dictionary for MTehran model
from pathlib import Path
from django.contrib.gis.utils import LayerMapping
from .models import MahalatTehran



mtehran_mapping = {
    'name_mahal': 'NAME_MAHAL',
    'reg_no': 'reg_no',
    'shape_le_1': 'Shape_Le_1',
    'shape_area': 'Shape_Area',
    'geom': 'MULTIPOLYGON',
}

Mahalat_Tehran = Path(__file__).resolve().parent.parent/"updateData"/"shp"/"StaticShape"/"Mahalat_Tehran.shp"

def run(verbose=True):
    MahalatTehran.objects.filter().delete()
    lm = LayerMapping(MahalatTehran,Mahalat_Tehran,mtehran_mapping,transform=False)
    lm.save(strict=True, verbose=verbose)
    

