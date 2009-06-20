'''
XML widget: parse xml and create his children
'''

__all__ = ['XMLWidget']

from xml.dom import minidom, Node
from ...logger import pymt_logger
from ..factory import MTWidgetFactory
from widget import MTWidget

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

            #create widget
            try:
                nodeWidget  = MTWidgetFactory.get(class_name)()
            except:
                pymt_logger.exception('unable to create widget %s' % class_name)
                raise

            #set attributes
            for (name, value) in node.attributes.items():
                try:
                    nodeWidget.__setattr__(name, eval(value))
                except NameError:
                    #if it is a NameError its probably a regular string property like e.g. id
                    #if xml is e.g. <... name="myval" ...> it breaks (had to be: name="'myval'")\
                    #so lets try with just the string value itself
                    nodeWidget.__setattr__(name, value)
                    pymt_logger.warning('NameError when setting %s on %s.  Defaulting to string value!'  % (name, class_name))
                except:
                    pymt_logger.exception('unable to set %s on %s' % (name, class_name))
                    raise

            #add child widgets
            for c in node.childNodes:
                w = self.createNode(c)
                if w:
                    nodeWidget.add_widget(w)

            return nodeWidget

    def loadString(self, xml):
        doc = minidom.parseString(xml)
        root = doc.documentElement
        self.add_widget(self.createNode(root))


# Register all base widgets
MTWidgetFactory.register('XMLWidget', XMLWidget)
