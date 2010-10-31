#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec4 frag_color;
varying vec2 tex_coord;

/* vertex attributes */
attribute vec4     vPosition;
attribute vec4     vColor;
attribute vec4     vNormal;
attribute vec2     vTexCoords0;
attribute vec2     vTexCoords1;
attribute vec2     vTexCoords2;
attribute vec2     vTexCoords3;

/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform sampler2D  texture0;
uniform sampler2D  texture1;
uniform sampler2D  texture2;
uniform sampler2D  texture3;
    
void main (void){
  gl_Position =  projection_mat*modelview_mat * vPosition;
  frag_color = vColor;
  tex_coord = vTexCoords0;
}