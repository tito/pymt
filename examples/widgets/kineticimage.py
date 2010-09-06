from pymt import *
import glob, os

k = MTKineticList(size=getWindow().size, friction=1, do_x=True,
                  h_limit=4, do_y=False, title=None, deletable=False,
                  searchable=False, w_limit=0)

# search file in image directory
pattern = os.path.join(os.path.dirname(__file__), 'images', '*.png')
for x in xrange(10):
    for filename in glob.glob(pattern):
        item = MTKineticImage(image=Loader.image(filename))
        k.add_widget(item)

runTouchApp(k)
