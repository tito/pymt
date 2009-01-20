from xml.dom import minidom, Node
from pymt.ui.widget import MTWidget
from pymt.ui.factory import MTWidgetFactory

class XMLWidget(MTWidget):
    def __init__(self, xml=None):
        MTWidget.__init__(self)
        if xml is not None:
            self.loadString(xml)

    def createNode(self, node):
        if node.nodeType == Node.ELEMENT_NODE:
            class_name = node.nodeName

            #create widget
            nodeWidget  = MTWidgetFactory.get(class_name)()

            #set attributes
            for (name, value) in node.attributes.items():
                nodeWidget.__setattr__(name, eval(value))

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
