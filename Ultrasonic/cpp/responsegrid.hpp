#ifndef RESPONSEGRID_H
#define RESPONSEGRID_H

#include <cstdint>
#include <algorithm>
#include <cstdlib>
#include "util.hpp"

using std::min;
using std::max;

class ResponseGrid
{
public:
	ResponseGrid(unsigned width, unsigned height, float scale)
	 : _width(width), _height(height), _scale(scale), _angles(16) {
		 
		_poMap = new uint8_t[_width * _height];
		memset(_poMap, prob2byte(0.5), _width * _height);
		
		_prMap = new uint8_t*[_angles];
		
		for(int i = 0; i < _angles; i++) {
			_prMap[i] = new uint8_t[_width * _height];
			memset(_prMap[i], prob2byte(1.0 - pow(0.5, 1.0/_angles)), _width * _height);
		}
	}
	
	~ResponseGrid() {
		delete [] _poMap;
		
		for(int i = 0; i < _angles; i++) {
			delete [] _prMap[i];
		}
		delete [] _prMap;
	}
	
	void update(double R, double theta, double alpha, double posX, double posY) {
		vec2<double> OA(R * cos(theta + alpha/2), R * sin(theta + alpha/2));
		vec2<double> OB(R * cos(theta - alpha/2), R * sin(theta - alpha/2));
		vec2<double> OC(R * cos(theta), R * sin(theta));
		
		vec2<double> pos(posX, posY);
		
		/*
		vec2<int> OAg = world2grid(OA + pos);
		vec2<int> OBg = world2grid(OB + pos);
		*/

		vec2<int> P = world2grid(vec2<double>(
			round(min(0.0, OA.x, OB.x, OC.x) + pos.x),
			round(max(0.0, OA.y, OB.y, OC.y) + pos.y)
		));
		
		vec2<int> Q = world2grid(vec2<double>(
			round(max(0.0, OA.x, OB.x, OC.x) + pos.x),
			round(min(0.0, OA.y, OB.y, OC.y) + pos.y)
		));
		
		P.x = max(0, min(P.x, (int) _width-1));
		P.y = max(0, min(P.y, (int) _height-1));
		Q.x = max(0, min(Q.x, (int) _width-1));
		Q.y = max(0, min(Q.y, (int) _height-1));
		
		for(int x = P.x; x <= Q.x; x++) {
			for(int y = Q.y; y <= P.y; y++) {
				vec2<double> loc = grid2world(vec2<int>(x, y)) - pos;
				
				if((loc.x * OA.y - loc.y * OA.x >= 0) &&
					(loc.x * OB.y - loc.y * OB.x <= 0) && (loc.length() <= R))
				{
					updateCell(x, y, loc.length(), R, theta, alpha);
				}
			}
		}
	}

	unsigned width() const {
		return _width;
	}
	unsigned height() const {
		return _height;
	}
	double scale() const {
		return _scale;
	}
	unsigned angles() const {
		return _angles;
	}
	
	vec2<int> world2grid(const vec2<double>& wp) {
		return vec2<int>(
			wp.x * _scale + _width/2.0,
			wp.y * _scale + _height/2.0
		);
	}
	
	vec2<double> grid2world(const vec2<int>& gp) {
		return vec2<double>(
			(gp.x - _width/2.0) / _scale,
			(gp.y - _height/2.0) / _scale
		);
	}
	
	uint8_t* poData() {
		return _poMap;
	}
	
	uint8_t* prData(unsigned angle_index) {
		return _prMap[angle_index];
	}
	
protected:
	void updateCell(int x, int y, double s, double r, double theta, double alpha) {
		int theta_index = int(to_deg(theta)/(360.0/_angles));
		
		double k = 5.0/alpha;
		double eps = 1.0/_scale;
		
		double Ps = (fabs(s - r) > eps) ? 0.05 : min(1.0, k/(r * _scale));
		double Pp = byte2prob(_prMap[theta_index][y * _width + x]);
		double Pn = min(Ps * Pp / (Ps * Pp + (1.0 - Ps)*(1.0 - Pp) + 0.01), 1.0);
		
		_prMap[theta_index][y * _width + x] = prob2byte(Pn);
		
		double Po  = 1.0;
		for(int i = 0; i < _angles; i++)
			Po *= (1.0 - byte2prob(_prMap[i][y * _width + x]));
		Po = 1.0 - Po;
		_poMap[y * _width + x] = prob2byte(Po);
	}
	
private:	
	int _width, _height, _angles;
	double _scale;
	
	uint8_t* _poMap;
	uint8_t** _prMap; 
};

#endif // RESPONSEGRID_H
