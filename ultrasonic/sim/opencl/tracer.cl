kernel void trace
(
	global const unsigned char* image,
	int width,
	int height,
	int pos_x,
	int pos_y,
	global const float2* dirs,
	global float* results
) {
	int id = get_global_id(0);
	int x = pos_x, y = pos_y;
	
	float dirX = dirs[id].x + 0.0001f; 
	float dirY = dirs[id].y + 0.0001f;
	
	float	ddx = sqrt(1.0f + (dirY * dirY) / (dirX * dirX));
	float	ddy = sqrt(1.0f + (dirX * dirX) / (dirY * dirY));
	
	int stepX  = 1, stepY = 1;
	float sdx = ddx, sdy = ddy;
	
	if(dirX < 0) {
		stepX = -1; sdx = 0;
	}
	if(dirY < 0) {
		stepY = -1; sdy = 0;
	}
	
	while(x > 0 && y > 0 && x < width-1 && y < height-1 && image[y * width + x] != 0x00) {
		if(sdx < sdy) {
			sdx += ddx;
			x += stepX;
		}
		else {
			sdy += ddy;
			y += stepY;
		}
	}
	
	float x_loc = x - pos_x, y_loc = y - pos_y;
	results[id] = sqrt(x_loc*x_loc + y_loc*y_loc);
}