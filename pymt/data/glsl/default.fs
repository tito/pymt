#ifdef GL_ES
    precision highp float;
#endif

/* Outputs to the fragment shader */
varying vec4 frag_color;
varying vec2 tex_coord;

/* uniform texture samplers */
uniform sampler2D  texture0;
uniform sampler2D  texture1;
uniform sampler2D  texture2;
uniform sampler2D  texture3;

void main (void){
    vec4 tex_color = texture2D(texture0, tex_coord);
    gl_FragColor = frag_color;
}
