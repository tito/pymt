#ifndef __PYMTCORE_GRAPHX
#define __PYMTCORE_GRAPHX

class Texture;
struct pos2d;

void drawTexturedRectangle(Texture *texture, pos2d pos, pos2d size, float tex_coords[12]);

#endif
