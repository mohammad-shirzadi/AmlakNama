import geopandas, numpy
from  explore.models import masages




def createmap(lu='res',typ='buy',reg=0,tile="CartoDB positron"):
    Pgdf = geopandas.read_file(r"updateData/shp/polymean.shp")
    Tgdf = geopandas.read_file(r"updateData/shp/StaticShape/Mahalat_Tehran.shp")
    fieldR = ['NAME_MAHAL','price', 'mortgage', 'rent']
    fieldB = ['NAME_MAHAL','price']

    if reg == 0:
        txt = ''
    elif reg in range(1,23):
        txt = f'and reg_no == {reg}'
    if typ == 'buy':
        popupf = fieldB
    elif typ == 'rent':
        popupf = fieldR

    mp = Pgdf.query(f'landuse == "{lu}" and ptype == "{typ}"'+ txt)
    fmp = Pgdf.query(f'landuse == "{lu}" and ptype == "{typ}"')

    m = mp.explore(
        column="price",
        scheme='naturalbreaks',
        legend=False,
        k=50,
        tooltip=False,
        popup=popupf,
        legend_kwds=dict(colorebar=False),
        #name= l + '-' + t,
        tiles=tile,
        zoom_control=False,
        zoom=11
    )
    Tgdf.explore(
    m=m,
    color='None',
    tooltip=False,
    popup=['NAME_MAHAL'],
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
        'lu' : lu,
        'typ' : typ,
        'reg' : reg,
        'Tiles' : ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"],
        'ActiveTile' : tile,
    }

    return data

def message(name, email, txtmessage):
    masages.objects.create(name=name,email=email,txtmasages=txtmessage,)
    return "پیام با موفقیت ارسال شد"