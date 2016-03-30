import gis
import psycopg2


class GisConnector:
    def __init__(self, ip):
        self.db = gis.connect(ip, 'gis','gis','123')
        self.cursor = self.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def sendObject(self, poly):
        origin = (58.05377, 56.22206)
        poly = [(p[0][0] * 0.000002 + origin[1], p[0][1] * 0.000002 + origin[0]) for p in poly]
        gis.SetPolygon(self.cursor, self.db, poly)

    def sendHole(self, hole):
        origin = (58.05377, 56.22206)
        hole = [(p[0][0] * 0.000002 + origin[1], p[0][1] * 0.000002 + origin[0]) for p in hole]

        gis.SetEmptyPolygon(self.cursor, self.db, hole)

    def sendPosition(self, position):
        origin = (58.05377, 56.22206)

        gis.CurrentLocation(self.cursor, self.db,
                                            (
                                                position[0] * 0.000002 + origin[1],
                                                position[1] * 0.000002 + origin[0]
                                            ))
        gis.MrkWayUpdate(self.cursor, self.db)