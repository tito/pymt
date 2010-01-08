import OpenGL
#OpenGL.FULL_LOGGING = True

# PYMT Plugin integration
IS_PYMT_PLUGIN = True
PLUGIN_TITLE = 'Mandelbrot Viewer'
PLUGIN_AUTHOR = 'Thomas Hansen'
PLUGIN_DESCRIPTION = 'Uses a fragment shader to draw the mandelbrot set, so you can just keep zooming and zooming and zoomming :)'




#The shader source to draw the mandelbrot set is taken from the TyphonLab Tutorial on Advanced OpenGl shaders
#http://www.opengl.org/sdk/docs/tutorials/TyphoonLabs/Chapter_4.pdf

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
uniform float zoom;

void main()
{
    vec2 center = vec2(-0.65,0);
    vec3 outerColor1 = vec3(0.0,0.2,0.7);
    vec3 outerColor2 = vec3(1.0,1.0,1.0);

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

    vec3 color;
    if (r2 < 4.0)
        color = vec3(0.1,0.0,0.0);
    else{
        float intensity = float(iter) + 1.0 -  (( log( log( sqrt(r2) ) )/log(2.0)  )  /log(2.0));
        float val = float(intensity)*0.02;
        if (mod(val,2.0) < 1.0){
            color = mix(outerColor1, outerColor2, fract(float(intensity)*0.02));
        }else{
            color = mix(outerColor2, outerColor1, fract(float(intensity)*0.02));
        }

    }
    gl_FragColor = vec4 (clamp(color, 0.0, 1.0), 1.0);
}
"""




from pymt import *
from OpenGL.GL import *




class MandelbrotViewer(MTScatterWidget):
    """ Mandelbrot viewer.   Draws a square and uses a Shader to draw the mandelbrot set on it """
    def __init__(self, **kwargs):
        super(MandelbrotViewer, self).__init__(**kwargs)
        self.shader = Shader(vertex_shader_src, fragment_shader_src)
        self.zoom = 1.8
        self.iterations = 100

    def draw(self):
        w,h = self.size
        self.shader.use()
        self.shader['zoom'] = self.zoom
        self.shader['maxIterations'] = self.iterations
        drawTexturedRectangle(None, size=(w,h))
        self.shader.stop()


def update_iterations(viewer, label, value):
    # simple callback function for the slider on_value_changed event.
    # sets iterations on mandelbrot viewer and uopates text label
    viewer.iterations = int(value)
    label.text = "Number of iterations: "+str(int(value))


def pymt_plugin_activate(w, ctx):
    # crerate a widget and put the mandelbrot viwer inside it
    #( otherwise the touchsimulator draws teh cuircles underneath?!  probably a bug)
    root = MTWidget()
    mbviewer = MandelbrotViewer(size=(512,512))
    root.add_widget(mbviewer)

    #create a label and a slider for setting the number of iterations
    label = MTLabel(label="Number of iterations: 50", pos=(10,50), autosize=True)
    slider = MTSlider(orientation='horizontal', min=25, max=250, value=100, size=(w.width-20, 30), pos=(10,10))

    # attach the event handler to the slider
    # uses curry to save the firt two arguments, since this is where we have the refernce to them
    # and the on_value_changed event only provides on argument ('value')
    callback = curry(update_iterations, mbviewer, label)
    slider.push_handlers(on_value_change=callback)

    # add the widgets to the window
    w.add_widget(root)
    w.add_widget(label)
    w.add_widget(slider)


def pymt_plugin_deactivate(w, ctx):
    w.children = []



#so you can run it as a standalone app
if __name__ == '__main__':
    w = MTWindow()
    ctx = MTContext()
    pymt_plugin_activate(w, ctx)
    runTouchApp()
    pymt_plugin_deactivate(w, ctx)
