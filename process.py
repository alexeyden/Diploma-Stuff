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

def can_be_joined(chain1, chain2):
	eps_dir  = 0.9900
	eps_ends = 0.0001
	eps_dist = 0.05
	
	c1_a, c1_b = pca_trend(chain1)
	c2_a, c2_b = pca_trend(chain2)
	c1_len = vec_len(c1_a, c1_b)
	c2_len = vec_len(c2_a, c2_b)
	
	c1_dir = [(c1_b[0] - c1_a[0])/c1_len, (c1_b[1] - c1_a[1])/c1_len]
	c2_dir = [(c2_b[0] - c2_a[0])/c2_len, (c2_b[1] - c2_a[1])/c2_len]
	
	#parallell?
	if abs(c1_dir[0] * c2_dir[0] + c1_dir[1] * c2_dir[1]) < eps_dir:
		return False
	
	A = min(c1_a, c1_b)
	B = max(c1_a, c1_b)
	C = min(c2_a, c2_b)
	D = max(c2_a, c2_b)
	
	lA = 1/c1_dir[0]
	lB = -1/c1_dir[1]
	lC = -c1_a[0]/c1_dir[0] + c1_a[1]/c1_dir[1]
	d = abs(lA * c2_a[0] + lB * c2_a[1] + lC)/sqrt(lA**2 + lB**2)
	if d > eps_dist:
		return False
	
	#matching ends?
	#if vec_len(c1_a,c2_a) < eps_ends or vec_len(c1_a, c2_b) < eps_ends or vec_len(c1_b,c2_a) < eps_ends or vec_len(c1_b,c2_b) < eps_ends:
	#	return True
	
	sAC = c1_dir[0] * (C[0] - A[0]) + c1_dir[1] * (C[1] - A[1]) > 0
	sAD = c1_dir[0] * (D[0] - A[0]) + c1_dir[1] * (D[1] - A[1]) > 0
	sBC = -c1_dir[0] * (C[0] - B[0]) + -c1_dir[1] * (C[1] - B[1]) > 0
	sBD = -c1_dir[0] * (D[0] - B[0]) + -c1_dir[1] * (D[1] - B[1]) > 0
	
	#c2 intersects c1?
	if not (sAC or sAD) or not (sBC or sBD):
		return False
	
	return True
	
def join_chains(chains):
	copy = chains[:]
	joined = []
	used = []
	#cnt = 2
	for i, c1 in enumerate(chains):
		for j, c2 in enumerate(chains):
			if c1 != c2 and (not (c2,c1) in used) and can_be_joined(c1, c2):
				joined.append(c1 + c2)
				#joined.append(c1)
				#joined.append(c2)
				used.append((c1, c2))
				#cnt -= 1
				#if cnt < 0:
				#	return joined
			print('{0:.3f}% joined: {1}'.format((i * len(chains) + j) * 100  / len(chains) ** 2, len(joined)))
	for c in chains:
		c
	return joined

def count_in(data, x,y, r):
	n = 0
	for p in data:
		if p[0] >= x and p[0] < x + r and p[1] >= y and p[1] < y + r:
			n += 1
	return n

def grid(chains):
	data = []
	for ch in chains:
		data += ch
	rows = []
	for row in range(0, 10 * 5):
		rows.append([])
		for col in range(0, 10 * 5):
			rows[row].append(0)
			if count_in(data, row/5.0 - 5.0, col/5.0 - 5.0, 0.2) > 4:
				rows[row][col] = 1
	return rows

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

	j = join_chains(chains)
	for ch in j:
		beg,end = pca_trend(ch)
		
		fout.write('{0:.3f} {1:.3f}\n'.format(beg[0], beg[1]))
		fout.write('{0:.3f} {1:.3f}\n'.format(end[0], end[1]))
		fout.write('\n')
	
	#g = grid(chains)
	#for i, row in enumerate(g):
	#	for j, item in enumerate(row):
	#		if item == 1:
	#			fout.write('{0:.3f} {1:.3f}\n'.format(i/5.0 - 5.0, j/5.0 - 5.0))	
	
	f.close()
	fout.close()
