# -*- coding: utf-8 -*-

import psycopg2
import sys
import psycopg2.extras

#test_file.txt - координаты из таблицы planet_osm_point
#file.txt - в файле хранятся координаты точек, которые необходимо вставить
#file_p.txt - в файле хранятся координаты полигонов, которые необходимо вставить
#current_location.txt - в файле хранятся координаты, текущего местоположения МРК
#MrkWay.txt - в файле хранится пройденный маршрут МРК


def connect (dbname, user, pswd):#подключение к базе
    conn_string = "host='10.42.0.1' dbname=%s user=%s password=%s" % (dbname, user, pswd,)
    print "Connecting to database\n	->%s" % (conn_string)
    try:
        db = psycopg2.connect(conn_string)
    except psycopg2.Error as e:
        print "I am unable to connect to the database"
        print e.pgerror #выводит код ошибки при подключении, попрбовать в SELECT
        sys.exit()
    return db

def WriteFile(db):#запись координат в файл
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)#объявление курсора
    cursor.execute("SELECT ST_AsText(ST_Transform(way,4326)) FROM  planet_osm_point")
    f = open('test_file.txt', 'w')
    for row in cursor:
        f.write('point: %s' % (row['st_astext']) + '\n')
        #print 'point: %s' % (row['st_astext'])#в качестве индекса в row выступает название столбца
    #после for cursor становится в конечное положение, чтобы его вернуть в
    # начальное положение используется функция scroll(...)
    #cursor.scroll(0, mode='absolute')
    #for row in cursor:
    #    print 'POINT: %s' % (row ['st_astext'])
    f.close()
    return 0

def InsertPoint(cursor, db):#запись данных в БД из файла
    arg_line = []#объявление списка
    f2 = '10 10\n20 20\n30 30'.split('\n')
    for line in f2:
       #arg_line = line.split(' ')# вернул список
       arg_line.extend(line.split(' '))
    i = 0
    for a in arg_line:
        if i < len(arg_line):
            cursor.execute("insert into planet_osm_point(name,way) values (%s,ST_SetSRID(ST_MakePoint(%s,%s),4326));",('python33',arg_line[i],arg_line[i+1],))
        i = i+2
    db.commit()
    #insert into planet_osm_point(name,way) values ('TEST 3d',ST_SetSRID(ST_MakePoint(56.2133000,58.0492000),4326));
        #print 'point: %s' % (row ['st_astext'])#в качестве индекса в raw выступает название столбца
    return 0

def InsertPolygon(cursor, db):#запись полигонов из файла в БД
    f2 = open('ins_pol.txt', 'r')#в файле хранятся координаты полигонов, которые необходимо вставить
    f2 = '10 10\n20 20\n30 30'.split('\n')
    for line in f2:
        cursor.execute("insert into planet_osm_polygon(name,way) values (%s,ST_SetSRID(ST_MakePolygon(ST_GeomFromText(%s)),4326));",('python23',line,))
    f2.close()
    db.commit()
    #insert into planet_osm_point(name,way) values ('TEST 3d',ST_SetSRID(ST_MakePoint(56.2133000,58.0492000),4326));
        #print 'point: %s' % (row ['st_astext'])#в качестве индекса в raw выступает название столбца
    return 0

def CurrentLocation(cursor, db):#надо запустить в глобальном цикле, для обнавления каждые несколько секунд
    #update planet_osm_point set way = ST_SetSRID(ST_MakePoint(11,21),4326) where name = 'current_location';
    arg_line = []#объявление списка
    f2 = open('current_location.txt', 'r')#в файле хранятся координаты, текущего местоположения МРК
    for line in f2:
       #arg_line = line.split(' ')# вернул список
       arg_line.extend(line.split(' '))
    way = open('MrkWay.txt', 'a')#открытие файла на дозапись
    way.write('%s %s' % (arg_line[0],arg_line[1],))
    way.close()
    for a in arg_line:
            cursor.execute("update planet_osm_point set way = ST_SetSRID(ST_MakePoint(%s,%s),4326) where name = 'current_location';",(arg_line[0],arg_line[1],))#читаем и записываем в БД только первую строчку, предполагается,что в файле будет хранится лишь одна координата
    f2.close()
    db.commit()
    #insert into planet_osm_point(name,way) values ('TEST 3d',ST_SetSRID(ST_MakePoint(56.2133000,58.0492000),4326));
        #print 'point: %s' % (row ['st_astext'])#в качестве индекса в raw выступает название столбца
    return 0

def SetCurrentLocation(cursor, db, arg_line):
    cursor.execute("update planet_osm_point set way = ST_SetSRID(ST_MakePoint(%s,%s),4326) where name = 'current_location';",(arg_line[0],arg_line[1],))#читаем и записываем в БД только первую строчку, предполагается,что в файле будет хранится лишь одна координата
    db.commit()
    return 0

def MrkWayUpdate(cursor, db):#запись пройденого пути мрк в бд, обновление каждые 30 сек,
    #добавлять тек. местоположение в файл MrkWay.txt в CurrentLocation()
    #считываю файл MrkWay.txt и обновляю way в planet_osm_line, name = MrkWay
    #update planet_osm_line set way = ST_GeomFromText('LINESTRING(1.1111 2.2222, 3.333 4.444)',4326) where name = 'MrkWay';
    arg_line = [] #объявление списка
    f2 = open('MrkWay.txt', 'r')#в файле хранится пройденный маршрут МРК
    for line in f2:
       #arg_line = line.split(' ')# вернул список
       arg_line.extend(line.split(' '))
    i = 0
    str1 = 'LINESTRING( '
    for a in arg_line:
        if i < len(arg_line):
            str1 = str1 + arg_line[i] + '  ' + arg_line[i+1] + ','
        i = i+2
    str1 = str1[0: -1]#удалить последний символ(лишняя запятая) из строки
    str1 = str1 + ')'
    cursor.execute("update planet_osm_line set way = ST_GeomFromText(%s,4326) where name = 'MrkWay';",(str1,))
    print str1
    f2.close()
    db.commit()
    #insert into planet_osm_point(name,way) values ('TEST 3d',ST_SetSRID(ST_MakePoint(56.2133000,58.0492000),4326));
        #print 'point: %s' % (row ['st_astext'])#в качестве индекса в raw выступает название столбца
    return 0

def NewPolygon(cursor, db):#Запись данных, полученных с дальномеров
    #select osm_id from planet_osm_polygon where ST_SetSRID(ST_MakePolygon(ST_GeomFromText('LINESTRING(0 0, 0 5, 5 5, 5 0, 0 0)')),4326) && way;
    #cursor2 = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    f2 = open('file_p.txt', 'r')#в файле хранятся координаты полигонов, которые необходимо вставить
    #При вставке добавлять метку в поле name = 'new'
    res = 0
    for line in f2:#line координаты полигона от дальномера
        #cursor.execute("insert into planet_osm_polygon(name,way) values (%s,ST_SetSRID(ST_MakePolygon(ST_GeomFromText(%s)),4326));",('new',line,))
        #вывод ид полигонов, которые пересекаются с полигоном из файла
        cursor.execute("select osm_id from planet_osm_polygon where ST_SetSRID(ST_MakePolygon(ST_GeomFromText(%s)),4326) && way;",(line,))
        #for a in cursor:
        #    print 'id %s' % (a ['osm_id'])

        ins = 1 #флаг, если 1, то вставляем полигон в БД, иначе ничего не делаем
        for row in cursor: #В курсоре список ид полигонов, в которые входит точка
            #print '%s' % (row ['osm_id']) #out osm_id
            res = PointInclude(db,row ['osm_id'])
            if res >= 70:
                #полигон уже в БД ничего не делать
                print 'Polygon into bd'
                print 'osm_id = %s' % (row ['osm_id'])
                ins = 0
            if res < 70 and res >= 50:
                #объединяем полигоны
                print 'union polygon'
                print 'osm_id = %s' % (row ['osm_id'])
                ins = 0
        if(ins == 1):
            cursor.execute("insert into planet_osm_polygon(name,way) values (%s,ST_SetSRID(ST_MakePolygon(ST_GeomFromText(%s)),4326));",('new',line,))
            print 'polygon inserted'
            print 'osm_id = %s' % (row ['osm_id'])

       # for row in cursor2: #В курсоре2 список ид полигонов, в которые входит точка
       #     print '%s' % (row ['osm_id']) #out osm_id

    f2.close()
    #db.commit()
    #insert into planet_osm_point(name,way) values ('TEST 3d',ST_SetSRID(ST_MakePoint(56.2133000,58.0492000),4326));
        #print 'point: %s' % (row ['st_astext'])#в качестве индекса в raw выступает название столбца
    return 0

def SetPolygon(cursor, db, f2):#Запись данных, полученных с дальномеров
    #select osm_id from planet_osm_polygon where ST_SetSRID(ST_MakePolygon(ST_GeomFromText('LINESTRING(0 0, 0 5, 5 5, 5 0, 0 0)')),4326) && way;
    #cursor2 = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    #f2 = open('file_p.txt', 'r')#в файле хранятся координаты полигонов, которые необходимо вставить
    #При вставке добавлять метку в поле name = 'new'
    res = 0
    polygon_string = '\'LINESTRING(' + ', '.join('{} {}'.format(x[0][0], x[0][1]) for x in f2) + ')\'' #строка для вставки в пол
    polygon_string = 'LINESTRING(-16 80, 16 80, 100 100, 200 200, 300 300, -16 80)'
    print polygon_string
    for line in f2:#line координаты полигона от дальномера
        #cursor.execute("insert into planet_osm_polygon(name,way) values (%s,ST_SetSRID(ST_MakePolygon(ST_GeomFromText(%s)),4326));",('new',line,))
        #вывод ид полигонов, которые пересекаются с полигоном из файла
        cursor.execute("select osm_id from planet_osm_polygon where ST_SetSRID(ST_MakePolygon(ST_GeomFromText(%s)),4326) && way;",(polygon_string,))
        #for a in cursor:
        #    print 'id %s' % (a ['osm_id'])

        ins = 1 #флаг, если 1, то вставляем полигон в БД, иначе ничего не делаем
        for row in cursor: #В курсоре список ид полигонов, в которые входит точка
            #print '%s' % (row ['osm_id']) #out osm_id
            res = NewPointInclude(db,row ['osm_id'], line)
            if res >= 70:
                #полигон уже в БД ничего не делать
                print 'Polygon into bd'
                print 'osm_id = %s' % (row ['osm_id'])
                ins = 0
            if res < 70 and res >= 50:
                #объединяем полигоны
                print 'union polygon'
                print 'osm_id = %s' % (row ['osm_id'])
                ins = 0
        if(ins == 1):
            cursor.execute("insert into planet_osm_polygon(name,way) values (%s,ST_SetSRID(ST_MakePolygon(ST_GeomFromText(%s)),4326));",('new',line,))
            print 'polygon inserted'
            print 'osm_id = %s' % (row ['osm_id'])

       # for row in cursor2: #В курсоре2 список ид полигонов, в которые входит точка
       #     print '%s' % (row ['osm_id']) #out osm_id

    f2.close()
    #db.commit()
    #insert into planet_osm_point(name,way) values ('TEST 3d',ST_SetSRID(ST_MakePoint(56.2133000,58.0492000),4326));
        #print 'point: %s' % (row ['st_astext'])#в качестве индекса в raw выступает название столбца
    return 0

def NewPointInclude(db,osm_id,f_point):#возвращает процент попадания точек в полигон
    #print '\n\nfunction point include()'
    res = 0.0
    cursor2 = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    arg_line = []#объявление списка
    #f_point = open('f_point.txt', 'r')# в файле хранятся точки, образующие полигон от дальномеров
    i = 0.0 # счетчик точек, входящих в полигон
    count = 0.0
    j = 0

    #count = float(len(arg_line)) / 2.0 #общее число точек
    #print 'len_result = %s' % (res)
    for a in f_point:
        if j < len(f_point):
            cursor2.execute("SELECT osm_id FROM planet_osm_polygon where ST_DWithin(way, ST_SetSRID(ST_MakePoint(%s, %s),4326), 0);" ,(a[0][j],a[0][j+1],))
        j = j + 2
        for row in cursor2: #В курсоре2 список ид полигонов, в которые входит точка
            #print '%s' % (row ['osm_id']) #out osm_id
            if row ['osm_id'] == osm_id:
                i = i +1 #счетчик вхождения точки в полигон
        count = count + 1
    count = count/2
    print 'count = %s' % (count)
    print 'i = %s' % (i)
    res = i/(count /100.0) #процент попадания точек в полигон
    print 'result = %s \n' % (res)
    f_point.close()
    return res #res





def PointInclude(db,osm_id):#возвращает процент попадания точек в полигон
    print '\n\nfunction point include()'
    res = 0.0
    cursor2 = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    arg_line = []#объявление списка
    f_point = open('f_point.txt', 'r')# в файле хранятся точки, образующие полигон от дальномеров
    i = 0.0 # счетчик точек, входящих в полигон
    count = 0.0
    j = 0
    for line in f_point:
       arg_line.extend(line.split(' '))
    #count = float(len(arg_line)) / 2.0 #общее число точек
    #print 'len_result = %s' % (res)
    for a in arg_line:
        if j < len(arg_line):
            cursor2.execute("SELECT osm_id FROM planet_osm_polygon where ST_DWithin(way, ST_SetSRID(ST_MakePoint(%s, %s),4326), 0);" ,(arg_line[j],arg_line[j+1],))
        j = j + 2
        for row in cursor2: #В курсоре2 список ид полигонов, в которые входит точка
            #print '%s' % (row ['osm_id']) #out osm_id
            if row ['osm_id'] == osm_id:
                i = i +1 #счетчик вхождения точки в полигон
        count = count + 1
    count = count/2
    print 'count = %s' % (count)
    print 'i = %s' % (i)
    res = i/(count /100.0) #процент попадания точек в полигон
    print 'result = %s \n' % (res)
    f_point.close()
    return res #res

def main():
    #tuple_cursor.execute("SELECT ST_AsText(ST_Transform(way,4326)) FROM  planet_osm_point")
    #my_row = tuple_cursor.fetchone()
    db2 = connect('test_database','test_user','123')
    WriteFile(db2)
    cursor = db2.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    #InsertPoint(cursor, db2)
    #InsertPolygon(cursor, db2)
    #CurrentLocation(cursor, db2)
    #NewPolygon(cursor, db2)
    #MrkWayUpdate(cursor, db2)

if __name__ == "__main__":
    main()