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
        if xml is not None:
            self.loadString(xml)

    def createNode(self, node):
        factory = MTWidgetFactory
        if node.nodeType == Node.ELEMENT_NODE:
            class_name = node.nodeName

            # parameters
            k = {}
            for (name, value) in node.attributes.items():
                k[str(name)] = eval(value)

            # create widget
            try:
                nodeWidget  = MTWidgetFactory.get(class_name)(**k)
            except:
                pymt_logger.exception('XMLWidget: unable to create widget %s' % class_name)
                raise

            #add child widgets
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
