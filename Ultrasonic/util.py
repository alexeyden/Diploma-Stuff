from math import *

def vec_sum(a, b):
	return [x+y for x,y in zip(a,b)]

def vec_sub(a, b):
	return [x-y for x,y in zip(a,b)]

def vec_dot(a, b):
	return sum([x*y for x,y in zip(a,b)])

def vec_len(a):
	return sqrt(a[0]*a[0] + a[1]*a[1])

def vec_norm(a):
	return vec_fac(a, 1/vec_len(a))

def vec_from_angle(angle):
	return [cos(angle), sin(angle)]

def vec_inv(a):
	return [-x for x in a]

def vec_fac(a, fac):
	return [fac*x for x in a]

def to_deg(angle):
	deg = angle * 180/pi
	deg = int(deg) % 360
	
	return deg if deg >= 0 else deg + 360 

def to_rad(angle):
	return angle * pi/180

def prob2byte(p):
	return int(p * 0xff)

def byte2prob(b):
	return float(b)/0xff