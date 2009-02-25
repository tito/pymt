from xml.dom import minidom, Node
from pymt.ui.widgets.widget import MTWidget
from pymt.ui.factory import MTWidgetFactory
from pymt.logger import pymt_logger

class XMLWidget(MTWidget):
    def __init__(self, xml=None):
        MTWidget.__init__(self)
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


def showNode(node):
	if node.nodeType == Node.ELEMENT_NODE:
		print 'Element name: %s' % node.nodeName
		for (name, value) in node.attributes.items():
			print '    Attr -- Name: %s  Value: %s' % (name, value)
		if node.attributes.get('ID') is not None:
			print '    ID: %s' % node.attributes.get('ID').value

# Register all base widgets
MTWidgetFactory.register('XMLWidget', XMLWidget)
