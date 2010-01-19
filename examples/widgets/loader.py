from pymt import *

if __name__ == '__main__':

    img = Loader.image('http://pymt.txzone.net/themes/K2DC/img/pymt-logo-bg.png')

    runTouchApp(MTContainer(img))

