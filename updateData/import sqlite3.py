import sqlite3
from updateData.models import propertyModel

connection = sqlite3.connect("db.sqlite3")
cursor = connection.cursor()
a = cursor.execute("SELECT * FROM updateData_propertymodel;").fetchall()
for i in range(len(a)):
    try:
        c = a[i]
        print(i)
        if not propertyModel.objects.filter(
            landuse=c[1],type=c[2],price=c[3],area=c[4],Cyear=c[5],
            mortgage=c[6],rent=c[7],lat=c[8],lon=c[9],
            mahale=c[10],exp=c[11],link=c[12],date_time=c[13]):
            propertyModel.objects.create(
                landuse=c[1],
                type=c[2], 
                price=c[3], 
                area=c[4], 
                Cyear=c[5], 
                mortgage=c[6], 
                rent=c[7], 
                lat=c[8], 
                lon=c[9], 
                mahale=c[10], 
                exp=c[11], 
                link=c[12], 
                date_time=c[13])
    except:
        continue