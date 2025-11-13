import geopandas, numpy
from shapely import wkt
from  explore.models import masages

from explore.models import MTPPolygon, MahalatTehran


LANDUSE = "res"
PTYPE = "buy"
REG_NO = 0
TILEMAP = "CartoDB positron"



def createmap(lu,typ,reg,tile):    
    global LANDUSE, PTYPE, REG_NO, TILEMAP   
    if lu:
        LANDUSE = lu        
    if typ:
        PTYPE = typ    
    if reg:
        REG_NO = reg
    if tile:
        TILEMAP = tile
    
    if LANDUSE == 'resland' and PTYPE == "rent":
        PTYPE = 'buy'

    pqs = MTPPolygon.objects.all()
    data = []
    for r in pqs:
        data.append({
             "landuse": r.landuse,
             "ptype": r.ptype,
             "price": r.price,
             "mortgage": r.mortgage,
             "rent": r.rent,
             "NAME_MAHAL": r.name_mahal,
             "reg_no":r.reg_no,
             "geometry":wkt.loads(r.geom.wkt)
             })
    Pgdf = geopandas.GeoDataFrame(data=data,crs='EPSG:32639')

    tqs = MahalatTehran.objects.all()
    data = []
    for r in tqs:
        data.append({
             "NAME_MAHAL": r.name_mahal,
             "reg_no":r.reg_no,
             "shape_le_1": r.shape_le_1,
             "shape_area": r.shape_area,
             "geometry":wkt.loads(r.geom.wkt)
             })
    Tgdf = geopandas.GeoDataFrame(data=data,crs='EPSG:32639')

    #Pgdf = geopandas.read_file(r"updateData/shp/polymean.shp")
    #Tgdf = geopandas.read_file(r"updateData/shp/StaticShape/Mahalat_Tehran.shp")
    fieldR = ['NAME_MAHAL','price', 'mortgage', 'rent']
    fieldB = ['NAME_MAHAL','price']


    if REG_NO == 0:
        txt = ''
    elif REG_NO in range(1,23):
        txt = f'and reg_no == {REG_NO}'

    if PTYPE == 'buy':
        popupf = fieldB
    elif PTYPE == 'rent':
        popupf = fieldR

    mp = Pgdf.query(f'landuse == "{LANDUSE}" and ptype == "{PTYPE}"'+ txt)
    fmp = Pgdf.query(f'landuse == "{LANDUSE}" and ptype == "{PTYPE}"')

    m = mp.explore(
        column="price",  scheme='naturalbreaks',  legend=False,
        k=50,            tooltip=False,           popup=popupf,
        legend_kwds=dict(colorebar=False),        #name= l + '-' + t,
        tiles=TILEMAP,      zoom_control=False,      zoom=11
    )
    Tgdf.explore(
    m=m, color='None', tooltip=False, popup=['NAME_MAHAL'],
    style_kwds={
        'color':'Black',
        'weight': 1,
        }
    )
    
    m.save(r"explore/static/explore/map/myhtml.html")

    lr = list(mp.reg_no)
    ln = list(mp.NAME_MAHAL)
    lp = list(mp.price)
    regmeanprice = mp.pivot_table('price','reg_no')
    reglist = list(regmeanprice.index)
    regmean = []
    for i in range(len(regmeanprice.values.tolist())):
        regmean.append(regmeanprice.values.tolist()[i][0])
    maxp = numpy.max(lp)
    minp = numpy.min(lp)
    meanp = numpy.mean(lp)
    data = {
        "Page" : 1,
        'RegionList' : numpy.unique(lr),
        'RNList' : reglist,
        'RMList' : regmean,
        'FRegionList' : numpy.unique(list(fmp.reg_no)),
        'NameList' : ln,
        'PriceList' : lp,
        'MaxPrice' : "{:,}".format(int(maxp)),
        'NameMaxPrice' : ln[lp.index(maxp)],
        'MeanPrice' : "{:,}".format(int(meanp)),
        'MinPrice' : "{:,}".format(int(minp)),
        'NameMinPrice' : ln[lp.index(minp)],
        'lu' : LANDUSE,
        'typ' : PTYPE,
        'reg' : REG_NO,
        'Tiles' : ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"],
        'ActiveTile' : TILEMAP,
    }

    return data

def message(name, email, txtmessage):
    masages.objects.create(name=name,email=email,txtmasages=txtmessage,)
    return "پیام با موفقیت ارسال شد"