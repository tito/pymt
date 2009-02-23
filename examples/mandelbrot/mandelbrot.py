from pymt import *

"""
The shader source to draw the mandelbrot set is taken from the TyphonLab Tutorial on Advanced OpenGl shaders
http://www.opengl.org/sdk/docs/tutorials/TyphoonLabs/Chapter_4.pdf
"""

vertex_shader_src = """

varying vec3 position;

void main()
{
    position = vec3(gl_MultiTexCoord0 - 0.5) * 5.0;
    gl_Position = ftransform();
}

"""


fragment_shader_src = """

varying vec3 position;
uniform int maxIterations;
uniform vec2 center;
uniform vec3 outerColor1;
uniform vec3 outerColor2;
uniform float zoom;

void main()
{


    maxIterations = 50;
    center = vec2(0,0);
    outerColor1 = vec3(0.0,0.5,1.0);
    outerColor2 = vec3(1.0,1.0,0.0);


    float real = position.x * (1.0/zoom) + center.x;
    float imag = position.y * (1.0/zoom) + center.y;
    float cReal = real;
    float cImag = imag;
    float r2 = 0.0;

    int iter;
    for (iter = 0; iter < maxIterations && r2 < 4.0; ++iter)
    {
        float tempreal = real;
        real = (tempreal * tempreal) - (imag * imag) + cReal;
        imag = 2.0 * tempreal * imag + cImag;
        r2 = real*real;  // this line is missing in the tutorial
    }

    // Base the color on the number of iterations.
    vec3 color;
    if (r2 < 4.0)
        color = vec3(0.0);
    else
        color = mix(outerColor1, outerColor2, fract(float(iter)*0.05));
    gl_FragColor = vec4 (clamp(color, 0.0, 1.0), 1.0);
}

"""

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'mandelbrot Viewer'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_DESCRIPTION = 'Uses a fragment shader to draw the mandelbrot set, so you can just keep zooming and zooming and zoomming :)'



class MandelbrotViewer(MTScatterWidget):

    def __init__(self, **kwargs):
        super(MandelbrotViewer, self).__init__(**kwargs)
        self.shader = Shader(vertex_shader_src, fragment_shader_src)
        self.zoom = 1.0

    def draw(self):
        print self.zoom
        w,h = self.size
        self.shader.use()
        self.shader['zoom'] = self.zoom
        vertcoords = (0.0,0.0, w,0.0, w,h, 0.0,h)
        texcoords  = (0.0,0.0, 1.0,0.0, 1.0,1.0, 0.0,1.0)
        draw(4, GL_QUADS, ('v2f', vertcoords), ('t2f', texcoords))
        self.shader.stop()




def pymt_plugin_activate(w, ctx):
    ctx.root = MTWidget()
    ctx.mbv = MandelbrotViewer(size=(512,512))
    ctx.root.add_widget(ctx.mbv)
    w.add_widget(ctx.root)

def pymt_plugin_deactivate(w, ctx):
    w.remove_widget(ctx.root)

if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
