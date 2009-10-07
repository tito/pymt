#ifndef __PYMTCORE_UTILS
#define __PYMTCORE_UTILS

struct pos2d
{
    double x;
    double y;

    char *__str__(void)
    {
        static char tmp[128];
        snprintf(tmp, sizeof(tmp), "(%f, %f)", this->x, this->y);
        return tmp;
    }
};

double get_ticks();

#endif
