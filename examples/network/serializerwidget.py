from pymt.logger import pymt_logger
from serializer import SerializerNetworkServer, SerializerNetworkClient, Serializer
from pymt import MTWidget, runTouchApp, set_color, drawRectangle

class SerializerNetworkWidget_Receiver(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('host', '0.0.0.0')
        kwargs.setdefault('port', 12000)
        super(SerializerNetworkWidget_Receiver, self).__init__(**kwargs)

        # start a network server
        self.server = SerializerNetworkServer(kwargs.get('host'), kwargs.get('port'))

    def on_update(self):
        super(SerializerNetworkWidget_Receiver, self).on_update()
        try:
            clientid, message = self.server.queue.pop()

            # Got a message, unserialize it
            serializer = Serializer()
            widget = serializer.unserialize(message.data)

            # Got a widget, add to tree
            self.add_widget(widget)

        except IndexError:
            pass

        except:
            pymt_logger.exception('Error while unserialize xml')

class SerializerNetworkWidget_Sender(MTWidget):
    def __init__(self, **kwargs):
        kwargs.setdefault('host', '0.0.0.0')
        kwargs.setdefault('port', 12000)
        super(SerializerNetworkWidget_Sender, self).__init__(**kwargs)

        # start a client
        self.client = SerializerNetworkClient(kwargs.get('host'), kwargs.get('port'))
        self.sendlist = []

    def on_update(self):
        # searching for widget in the position of the drop zone
        for w in self.parent.children:

            # ignore ourself
            if w == self:
                continue

            # if the center is in the box ?
            if Vector.in_bbox(w.center, self.pos, Vector(self.pos) + self.size):
                print 'Eat new widget'
                self.sendlist.append(w)
                self.parent.remove_widget(w)

        # empty sendlist
        for w in self.sendlist:
            self.client.send_widget(w)
        self.sendlist = []

    def draw(self):
        set_color(.1,.1,.1,.4)
        drawRectangle(pos=self.pos, size=self.size)


if __name__ == '__main__':
    import sys
    from pymt import *
    if len(sys.argv) <= 1:
        print 'Usage: python serializerwidget.py {client|server}'
        sys.exit(-1)
    elif sys.argv[1] == 'client':
        m = MTWindow()

        w = SerializerNetworkWidget_Sender(size=(50, m.height / 2.), pos=(m.width - 50, 0))
        m.add_widget(w)

        for i in xrange(1, 7):
            m.add_widget(MTScatterImage(filename='../pictures/images/pic%d.jpg' % i))

        runTouchApp()
    elif sys.argv[1] == 'server':
        w = SerializerNetworkWidget_Receiver()
        runTouchApp(w)
