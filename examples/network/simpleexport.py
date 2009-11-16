import os
os.environ['PYMT_SHADOW_WINDOW'] = '0'
from pymt import *

import inspect
import new
import xml.dom.minidom as x

builtinlist = (int, float, str, unicode, long,
               float, complex, tuple, list,
               dict, bool)
builtinliststr = map(lambda x: x.__name__, builtinlist)

class Network:

    @staticmethod
    def serialize_subclass(doc, w):
        root = doc.createElement(w.__class__.__name__)
        for name, value in inspect.getmembers(w):
            if name.startswith('__'):
                continue
            if type(value) == new.instancemethod:
                continue
            p = doc.createElement('prop')
            p.setAttribute('name', name)
            p.setAttribute('type', type(value).__name__)

            if value is None:
                pass
            elif type(value) in builtinlist:
                p.setAttribute('value', str(value))
            else:
                value = Network.serialize_subclass(doc, value)
                p.appendChild(value)
            root.appendChild(p)
        return root

    @staticmethod
    def serialize(w):
        doc = x.Document()
        root = Network.serialize_subclass(doc, w)
        doc.appendChild(root)
        return doc.toprettyxml()

    @staticmethod
    def unserialize_subclass(node):
        clsobj = MTWidgetFactory.get(node.nodeName)
        cls = object.__new__(clsobj)
        for child in node.childNodes:
            if child.nodeName != 'prop':
                continue
            pname = child.getAttribute('name')
            ptype = child.getAttribute('type')
            if ptype == 'NoneType':
                pvalue = None
            elif ptype in builtinliststr:
                pvalue = child.getAttribute('value')
                if ptype == 'str':
                    s = '%s("%s")' % (ptype, pvalue.replace('"', '\"'))
                elif ptype == 'unicode':
                    s = '%s(u"%s")' % (ptype, pvalue.replace('"', '\"'))
                else:
                    s = '%s(%s)' % (ptype, pvalue)
                # FIXME secure this
                pvalue = eval(s)
            else:
                pvalue = Network.unserialize_subclass(child.childNodes[0])
            cls.__dict__.update({pname: pvalue})
        return cls

    @staticmethod
    def unserialize(data):
        doc = x.parseString(data)
        instance = Network.unserialize_subclass(doc.childNodes[0])
        return instance


box = MTBoxLayout()
box.add_widget(MTSlider(max=2000, value=500))
box.add_widget(MTSlider(value=75, orientation='horizontal'))

data = Network.serialize(box)
print data
box = Network.unserialize(data)
runTouchApp(box)
