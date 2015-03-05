from math import *
import sys

def max_dist(pointcloud):
	dist = 0
	for p in pointcloud:
		d = vec_len(pointcloud[0], p)
		dist = max(d, dist)
	return dist

def vec_len(p1, p2):
	return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def pca_trend(pointcloud):
	sum_x, sum_y, sum_xx, sum_yy, sum_xy = 0, 0, 0, 0, 0
	for x,y in pointcloud:
		sum_x += x; sum_y += y
		sum_xx += x**2; sum_yy += y**2
		sum_xy += x * y
	n = len(pointcloud)
	Mx, My = sum_x/n, sum_y/n
	Dx, Dy = sum_xx/n - Mx*Mx, sum_yy/n - My*My
	Cxy = sum_xy/n - Mx * My
	
	sum_D = Dx + Dy
	dif_D = Dx - Dy
	discr_square = sqrt(dif_D * dif_D + 4 * Cxy * Cxy)
	lmbd_plus = (sum_D + discr_square)/2
	lmbd_minus = (sum_D - discr_square)/2
	
	ap = Dx + Cxy - lmbd_minus
	bp = Dy + Cxy - lmbd_minus
	
	a_len = sqrt(ap*ap + bp*bp)
	amp = 1.2 * max_dist(pointcloud)/2
	
	ap = amp * ap / a_len
	bp = amp * bp / a_len
	
	am = Dx + Cxy - lmbd_plus
	bm = Dy + Cxy - lmbd_plus
	
	start = [-ap + Mx, -bp + My]
	end = [ap + Mx, bp + My]
	
	return (start, end)

if __name__ == "__main__":
	f = open(sys.argv[1], 'r')
	fout = open(sys.argv[2], 'w')
	chains = []
	chain = []
	for line in f:
		if line == '\n':
			chains.append(chain)
			chain = []
		else:
			x,y = float(line.split(' ')[0]), float(line.split(' ')[1])
			chain.append((x,y))
	prev_end = (-10000, -100000)
	for ch in chains:
		beg,end = pca_trend(ch)
		
		if vec_len(prev_end, beg) < 0.1:
			beg = prev_end
			
		fout.write('{0:.3f} {1:.3f}\n'.format(beg[0], beg[1]))
		fout.write('{0:.3f} {1:.3f}\n'.format(end[0], end[1]))
		fout.write('\n')
		prev_end = end
		
	f.close()
	fout.close()
