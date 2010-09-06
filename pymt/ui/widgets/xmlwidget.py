'''
XML widget: parse xml and create his children
'''

__all__ = ('XMLWidget', )

from pymt.logger import pymt_logger
from pymt.ui.factory import MTWidgetFactory
from pymt.ui.widgets.widget import MTWidget

class XMLWidget(MTWidget):
    '''XML widget create all his children by parsing and execute xml ::

        from pymt import *
        data = """<?xml version="1.0"?>
        <MTKinetic>
            <MTButton label="1" pos="(50,50)"/>
            <MTButton label="2" pos="(250,50)"/>
            <MTButton label="3" pos="(50,250)"/>
        </MTKinetic>
        """
        w = XMLWidget(xml=data)

    .. warning::
        the value is passed to eval function. Don't provide xml from
        untrusted source !


    :Parameters:
        `xml` : string, default is None
            XML string that contain all the data
    '''
    def __init__(self, **kwargs):
        kwargs.setdefault('xml', None)
        super(XMLWidget, self).__init__(**kwargs)
        xml = kwargs.get('xml')
        self.registerdb = {}
        if xml is not None:
            self.loadString(xml)

    @property
    def root(self):
        '''Return the root widget of the xml'''
        if len(self.children):
            return self.children[0]
        return None

    def getById(self, widget_id):
        if widget_id in self.registerdb:
            return self.registerdb[widget_id]
        return None

    def autoconnect(self, obj):
        '''Autoconnect event handler from widget in xml to obj.
        For example, if you have a <MTButton id='plop'> in xml,
        and you want to connect on on_press event, it will search
        the obj.on_plop_press() function.
        '''
        for widget_id, children in self.registerdb.items():
            for event in children.event_types:
                eventobj = event
                if eventobj[:3] == 'on_':
                    eventobj = eventobj[3:]
                eventobj = 'on_%s_%s' % (widget_id, eventobj)
                if hasattr(obj, eventobj):
                    children.connect(event, getattr(obj, eventobj))


    def createNode(self, node):
        from xml.dom import Node
        factory = MTWidgetFactory.get
        if node.nodeType == Node.ELEMENT_NODE:
            class_name = node.nodeName

            # parameters
            k = {}
            widget_id = None
            for name, value in node.attributes.items():
                name = str(name)
                if name == 'id':
                    widget_id = eval(value)
                else:
                    if name == 'xid':
                        name = 'id'
                    k[name] = eval(value)

            # create widget
            try:
                nodeWidget = factory(class_name)(**k)
                if widget_id is not None:
                    self.registerdb[widget_id] = nodeWidget
            except:
                pymt_logger.exception('XMLWidget: unable to create widget %s' \
                                      % class_name)
                raise

            # add child widgets
            for c in node.childNodes:
                w = self.createNode(c)
                if w:
                    nodeWidget.add_widget(w)

            return nodeWidget

    def loadString(self, xml):
        from xml.dom import minidom
        doc = minidom.parseString(xml)
        root = doc.documentElement
        self.add_widget(self.createNode(root))

