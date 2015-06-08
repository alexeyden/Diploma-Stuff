import DatabaseFunc as dbf

class GisConnector:
	def __init__(self, ip):
		self.db = dbf.connect(ip, 'test_database','test_user','123')
		self.cursor = self.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
		
	def sendObject(self, poly):
		pass
	
	def sendHole(self, hole):
		pass
	
	def sendPosition(self, position):
		pass