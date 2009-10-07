#include <Python.h>
#include <iostream>
#include <GL/gl.h>
#include "graphx.h"
#include "corewidget.h"
#include "texture.h"

void drawTexturedRectangle(Texture *texture, pos2d pos, pos2d size, float texcoords[12])
{
    glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT | GL_TEXTURE_BIT);

    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glEnable(texture->target);
    glBindTexture(texture->target, texture->id);
    glBegin(GL_QUADS);
    glColor4f(1., 1., 1., 1.);
    glTexCoord2d(texcoords[0], texcoords[1]);
    glVertex2f((GLfloat)pos.x, (GLfloat)pos.y);
    glTexCoord2d(texcoords[3], texcoords[4]);
    glVertex2f((GLfloat)(pos.x + size.x), (GLfloat)pos.y);
    glTexCoord2d(texcoords[6], texcoords[7]);
    glVertex2f((GLfloat)(pos.x + size.x), (GLfloat)(pos.y + size.y));
    glTexCoord2d(texcoords[9], texcoords[10]);
    glVertex2f((GLfloat)pos.x, (GLfloat)(pos.y + size.y));
    glEnd();

    glPopAttrib();
}
