#ifndef UTIL_HPP
#define UTIL_HPP

#include <algorithm>
#include <cmath>
#include <iostream>

const double PI = 3.141592653;

int to_deg(double rad) {
	int deg = int(round(rad * 180.0 / PI)) % 360;
	
	return (deg < 0) ? deg + 360 : deg;
}

template<typename T> class vec2 {
public:
	vec2() : x(0), y(0) {}
	vec2(T x, T y) : x(x), y(y) {}	
	
	T x, y;
	
	vec2<T> operator+(const vec2<T>& t) const {
		return vec2<T>(x + t.x, y + t.y);
	}
	vec2<T> operator-(const vec2<T>& t) const {
		return vec2<T>(x - t.x, y - t.y);
	}
	double length() const {
		return sqrt(x*x + y*y);
	}
};

template<typename T> T max(T a1, T a2, T a3, T a4) {
	return std::max<T>(a1, std::max(a2, std::max(a3, a4)));
}

template<typename T> T min(T a1, T a2, T a3, T a4) {
	return std::min<T>(a1, std::min(a2, std::min(a3, a4)));
}

#endif