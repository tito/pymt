'''
XML widget: parse xml and create his children
'''

__all__ = ['XMLWidget']

from ...logger import pymt_logger
from ..factory import MTWidgetFactory
from widget import MTWidget
minidom = None
Node = None

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

    def getById(self, id):
        if id in self.registerdb:
            return self.registerdb[id]
        return None

    def autoconnect(self, obj):
        '''Autoconnect event handler from widget in xml to obj.
        For example, if you have a <MTButton id='plop'> in xml,
        and you want to connect on on_press event, it will search
        the obj.on_plop_press() function.
        '''
        for id, children in self.registerdb.items():
            for event in children.event_types:
                eventobj = event
                if eventobj[:3] == 'on_':
                    eventobj = eventobj[3:]
                eventobj = 'on_%s_%s' % (id, eventobj)
                if hasattr(obj, eventobj):
                    children.connect(event, getattr(obj, eventobj))


    def createNode(self, node):
        factory = MTWidgetFactory
        if node.nodeType == Node.ELEMENT_NODE:
            class_name = node.nodeName

            # parameters
            k = {}
            id = None
            for name, value in node.attributes.items():
                if str(name) == 'id':
                    id = eval(value)
                else:
                    k[str(name)] = eval(value)

            # create widget
            try:
                nodeWidget = MTWidgetFactory.get(class_name)(**k)
                if id is not None:
                    self.registerdb[id] = nodeWidget
            except:
                pymt_logger.exception('XMLWidget: unable to create widget %s' % class_name)
                raise

            # add child widgets
            for c in node.childNodes:
                w = self.createNode(c)
                if w:
                    nodeWidget.add_widget(w)

            return nodeWidget

    def loadString(self, xml):
        global minidom, Node
        if minidom is None:
            from xml.dom import minidom, Node
        doc = minidom.parseString(xml)
        root = doc.documentElement
        self.add_widget(self.createNode(root))


# Register all base widgets
MTWidgetFactory.register('XMLWidget', XMLWidget)
