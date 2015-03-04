from math import * 
import numpy as np
import sys

class KalmanFilter:
	"""
		Q - м. ковариации шума процесса
		R - м. ковариации шума измерения
		
		F - м. перехода состоянияй
		B - м. перехода упр.воздействия
		
		H - м. отношения измерений и состояний
	"""
	def __init__(self, Q, R, F, B, H):
		self.Q = Q
		self.R = R
		self.F = F
		self.B = B
		self.H = H
	
	"""
		x0 - началоьное состояние
		u0 - нач. упр. воздействие
		p0 - начальная ошибкf
	"""
	def reset(self, x0, u0, p0 = None):
		self.x = x0
		self.u = u0
		if not p0 is None:
			self.p = p0
		
	def correct(self, z):
		x_pred = np.dot(self.F, self.x) + np.dot(self.B, self.u)
		p_pred = np.dot(np.dot(self.F, self.p), np.transpose(self.F)) + self.Q
			
		HT = np.transpose(self.H)
		H_P_HT = np.dot(np.dot(self.H, self.p), HT)
			
		K = np.dot(np.dot(p_pred, HT), np.linalg.inv(H_P_HT + self.R))
			
		self.p = np.dot(np.eye(np.shape(K)[0]) - np.dot(K, self.H), p_pred)
		self.x = x_pred + np.dot(K, z - np.dot(self.H, x_pred))
		
		return self.x

if __name__ == "__main__":
	f = open(sys.argv[1], 'r')
	
	data = []
	for line in f:
		data.append((float(line.split("\t")[0]), float(line.split("\t")[1])))
	
	data = np.array(data)
	
	Q = 0.1 * np.eye(2) #шум процесса
	R = 0.2 * np.eye(2) #шум измеренеия
	
	F = np.eye(2)
	B = np.eye(2)
	H = np.eye(2)
	kalman = KalmanFilter(Q, R, F, B, H)
	kalman.reset(np.array([0, 0]), np.array([0, 0]), 0.3 * np.eye(2))
	
	f.close()
	f = open(sys.argv[2], 'w')
	for point in data:
		res = kalman.correct(point)
		f.write('{0:.3}\t{1:.3}\n'.format(res[0], res[1]))
	f.close()