import psycopg2
import sys
import psycopg2.extras

import cv2
import numpy as np

def connect (host, dbname, user, pswd):
    conn_string = "host=%s dbname=%s user=%s password=%s" % (host, dbname, user, pswd,)
    # print "Connecting to database\n ->%s" % (conn_string)
    try:
        db = psycopg2.connect(conn_string)
    except psycopg2.Error as e:
        #print "I am unable to connect to the database"
        #print e.pgerror
        sys.exit()
    return db

def CurrentLocation(cursor, db, f2):
    way = open('MrkWay.txt', 'a')
    way.write('%s %s\n' % (f2[0],f2[1],))
    way.close()
    cursor.execute("update planet_osm_point set way = ST_SetSRID(ST_MakePoint(%s,%s),4326) where name = 'current_location';",(f2[0],f2[1],))
    db.commit()
    return 0

def MrkWayUpdate(cursor, db):
    arg_line = []
    f2 = open('MrkWay.txt', 'r')
    for line in f2:
       arg_line.extend(line.split(' '))
    i = 0
    str1 = 'LINESTRING( '
    for a in arg_line:
        if i < len(arg_line):
            str1 = str1 + arg_line[i] + '  ' + arg_line[i+1] + ','
        i = i+2
    str1 = str1[0: -1]
    str1 = str1 + ')'
    cursor.execute("update planet_osm_line set way = ST_GeomFromText(%s,4326) where name = 'MrkWay';",(str1,))
    f2.close()
    db.commit()
    return 0

def SetPolygon(cursor, db, polygons):
    res = 0
    polygon_string = 'LINESTRING(' + ', '.join('{} {}'.format(x[0], x[1]) for x in polygons) + ',' + str(polygons[0][0]) + ' ' + str(polygons[0][1]) + ')'
    cursor.execute("select osm_id from planet_osm_polygon where ST_SetSRID(ST_MakePolygon(ST_GeomFromText(%s)),4326) && way;",(polygon_string,))
    ins = 1
    for row in cursor:
        res = NewPointInclude(db,row ['osm_id'], polygons)
        if res >= 70:
            ins = 0
    if(ins == 1):
        cursor.execute("insert into planet_osm_polygon(name,way) values (%s,ST_SetSRID(ST_MakePolygon(ST_GeomFromText(%s)),4326));",('new',polygon_string,))
        #print 'polygon inserted'
    db.commit()
    return 0

def SetEmptyPolygon(cursor, db, polygons):
    polygon_string = 'LINESTRING(' + ', '.join('{} {}'.format(x[0], x[1]) for x in polygons) + ',' + str(polygons[0][0]) + ' ' + str(polygons[0][1]) + ')'
    #вывод ид полигонов, которые пересекаются с полигоном из файла
    cursor2 = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("select osm_id from planet_osm_polygon where ST_SetSRID(ST_MakePolygon(ST_GeomFromText(%s)),4326) && way;",(polygon_string,))
    for row in cursor: #В курсоре список ид полигонов, в которые входит точка
        res = NewPointInclude(db,row ['osm_id'], polygons)
        if res >= 70 or True:
            cursor2.execute("delete from planet_osm_polygon where osm_id = %s and name = 'new';",(row ['osm_id'],))
    db.commit()
    return 0

def Cikle (cursor, db):
    polygons  = TestPolygon(cursor, db)
    for pol1 in polygons:
        SetPolygon(cursor, db, pol1)
        SetEmptyPolygon(cursor, db, pol1)

def NewPointInclude(db,osm_id,f_point):
    res = 0.0
    cursor2 = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    i = 0.0
    count = 0.0
    for a in f_point:
        cursor2.execute("SELECT osm_id FROM planet_osm_polygon where ST_DWithin(way, ST_SetSRID(ST_MakePoint(%s, %s),4326), 0);" ,(float(a[0]),float(a[1]),))
        for row in cursor2:
            if row ['osm_id'] == osm_id:
                i = i +1
        count = count + 1
    res = i/(count /100.0)
    return res

def TestPolygon(cursor, db):
    image = cv2.imread('test.png')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    polygons, hier = cv2.findContours(image, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)
    return polygons

def main():
    db2 = connect('localhost','gis','gis','123')
    cursor = db2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    f2 = []
    f2.append('58.05378')
    f2.append('56.22206')
    CurrentLocation(cursor, db2, f2)
    #MrkWayUpdate(cursor, db2)
    #Cikle (cursor, db2)

if __name__ == "__main__":
    main()