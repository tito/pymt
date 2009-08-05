from pymt import *

if __name__ == '__main__':
    m = MTWindow()
    #fb = MTFileBrowser(filters=['.*\.[Pp][Nn][Gg]$'])
    fb = MTFileBrowser()
    m.add_widget(fb)
    @fb.event
    def on_select(list):
        print list
    runTouchApp()
