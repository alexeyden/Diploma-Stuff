#ifndef RESPONSEGRID_H
#define RESPONSEGRID_H

#include <algorithm>
#include <cstdlib>
#include "util.hpp"

#include <stdexcept>

using std::min;
using std::max;

class ResponseGridBlock
{
public:
	ResponseGridBlock(unsigned side, unsigned n)
	 : _side(side), _angles(n) {
		 
		_poMap = new float[_side * _side];
		std::fill(_poMap, _poMap + _side*_side, 0.5f);
		
		_prMap = new float*[_angles];
		
		for(int i = 0; i < _angles; i++) {
			_prMap[i] = new float[_side * _side];
			std::fill(_prMap[i], _prMap[i] + _side*_side, 1.0f - pow(0.5, 1.0/float(_angles)));
		}
	}
	
	~ResponseGridBlock() {
		delete [] _poMap;
		
		for(int i = 0; i < _angles; i++) {
			delete [] _prMap[i];
		}
		delete [] _prMap;
	}
	
	void update(double R, double theta, double alpha, double posX, double posY, bool blackout) {
		vec2<double> OA(R * cos(theta + alpha/2), R * sin(theta + alpha/2));
		vec2<double> OB(R * cos(theta - alpha/2), R * sin(theta - alpha/2));
		vec2<double> OC(R * cos(theta), R * sin(theta));
		
		vec2<double> pos(posX, posY);
		
		vec2<int> P(
			round(min(0.0, OA.x, OB.x, OC.x) + pos.x),
			round(max(0.0, OA.y, OB.y, OC.y) + pos.y)
		);
		
		vec2<int> Q(
			round(max(0.0, OA.x, OB.x, OC.x) + pos.x),
			round(min(0.0, OA.y, OB.y, OC.y) + pos.y)
		);
		
		P.x = max(0, min(P.x, (int) _side-1));
		P.y = max(0, min(P.y, (int) _side-1));
		Q.x = max(0, min(Q.x, (int) _side-1));
		Q.y = max(0, min(Q.y, (int) _side-1));
		
		for(int x = P.x; x <= Q.x; x++) {
			for(int y = Q.y; y <= P.y; y++) {
				vec2<double> loc = vec2<double>(x, y) - pos;
				
				if((loc.x * OA.y - loc.y * OA.x >= 0) &&
					(loc.x * OB.y - loc.y * OB.x <= 0) && (loc.length() <= R))
				{
					updateCell(x, y, loc.length(), R, theta, alpha, blackout);
				}
			}
		}
	}

	int side() const {
		return _side;
	}
	
	int angles() const {
		return _angles;
	}
	
	float* poData() {
		return _poMap;
	}
	
	float* prData(unsigned angle_index) {
		return _prMap[angle_index];
	}
	
	ResponseGridBlock* clone() {
		ResponseGridBlock* clone = new ResponseGridBlock(_side, _angles);
		
		memcpy(clone->poData(), this->poData(), sizeof(float) * _side * _side);
		for(int i = 0; i < _angles; i++) {
			memcpy(clone->prData(i), this->prData(i), sizeof(float) * _side * _side);
		}
		
		return clone;
	}
	
protected:
	void updateCell(int x, int y, double s, double r, double theta, double alpha, bool blackout) {
		int theta_index = int(to_deg(theta)/(360.0/_angles));

		double k = 20.0/(alpha * r);
		//std::cout << alpha * r * _scale << std::endl;
		double eps = 1.5;
		
		double Ps = (fabs(s - r) > eps || blackout) ? 0.05 : min(1.0, k);
		double Pp = _prMap[theta_index][y * _side + x];
		double Pn = min(Ps * Pp / (Ps * Pp + (1.0 - Ps)*(1.0 - Pp) + 0.001), 1.0);
		
		_prMap[theta_index][y * _side + x] = Pn;
		
		double Po  = 1.0;
		for(int i = 0; i < _angles; i++)
			Po *= (1.0 - _prMap[i][y * _side + x]);
		Po = 1.0 - Po;
		_poMap[y * _side + x] = Po;
	}
	
private:	
	int _side, _angles;
	
	float* _poMap;
	float** _prMap; 
};

#endif // RESPONSEGRID_H
