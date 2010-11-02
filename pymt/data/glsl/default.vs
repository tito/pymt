#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec4 frag_color;
varying vec2 tex_coord;

/* vertex attributes */
attribute vec2     vPosition;
attribute vec4     vColor;
attribute vec2     vTexCoords0;


/* uniform variables */
uniform mat4       modelview_mat;
uniform mat4       projection_mat;
uniform sampler2D  texture0;
uniform sampler2D  texture1;
uniform sampler2D  texture2;
uniform sampler2D  texture3;
    
void main (void){
  gl_Position = projection_mat * modelview_mat * vec4(vPosition, 0.0,1.0);
  frag_color  = vec4(vColor.agb,1.0);
  tex_coord   = vTexCoords0;
}
