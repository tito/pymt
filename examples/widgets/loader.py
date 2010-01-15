from pymt import *

if __name__ == '__main__':

    win = getWindow()
    '''
    for x in xrange(0, 7):
        img = Loader.image('../pictures/images/pic%d.jpg' % (x+1))
        s = MTScatterWidget(pos=((x % 3 * 100), (int(x / 3) % 3 * 100)))
        s.add_widget(MTContainer(img))
        win.add_widget(s)
    '''

    img = Loader.image('http://pymt.txzone.net/themes/K2DC/img/pymt-logo-bg.png')
    win.add_widget(MTContainer(img))

    runTouchApp()

