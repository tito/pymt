from pymt import *

# create the filebrowser
fb = MTFileBrowser()

# when selection will be done, it will print the selected files
@fb.event
def on_select(list):
    print list

runTouchApp(fb)
