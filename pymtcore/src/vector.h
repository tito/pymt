#ifndef __PYMTCORE_VECTOR
#define __PYMTCORE_VECTOR

class Vector
{
public:
    Vector()
    {
        this->x = 0;
        this->y = 0;
    }

    Vector(double x, double y)
    {
        this->x = x;
        this->y = y;
    }

    double x;
    double y;

    // TODO
};

#endif
