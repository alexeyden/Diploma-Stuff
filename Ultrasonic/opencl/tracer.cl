kernel void trace
(
	global const unsigned char* image,
	unsigned width,
	unsigned height,
	global const int4* points,
	global int2* results
) {
	int id = get_global_id(0);
	int x1 = points[id].x, y1 = points[id].y;
	int x2 = points[id].z, y2 = points[id].w;
	
	const int dx = abs(x2 - x1), dy = abs(y2 - y1);
	const int sx = x1 < x2  ? 1 : -1, sy = y1 < y2 ? 1 : -1;
	int err = dx - dy;
	
	while((x1 != x2 || y1 != y2) && (image[y1 * width + x1] != 0x00)) {
		if(err * 2 > -dy) {
			err -= dy;
			x1 += sx;
		}
		if(err * 2 < dx) {
			err += dx;
			y1 += sy;
		}
	}
	
	results[id].x = x1;
	results[id].y = y1;
}