import os
os.environ['PYMT_SHADOW_WINDOW'] = '0'
from pymt import *

import inspect
import new
import xml.dom.minidom as x

builtinlist = (int, float, str, unicode, long,
               float, complex, bool)
builtinliststr = map(lambda x: x.__name__, builtinlist)

class NetworkShare:

    def __init__(self):
        self.maps = {}

    def serialize_value(self, doc, value):
        if value is None:
            v = doc.createElement('None')
        elif type(value) in (list, tuple):
            v = doc.createElement(type(value).__name__)
            for element in value:
                v.appendChild(self.serialize_value(doc, element))
            return v
        elif type(value) in (dict, ):
            v = doc.createElement(type(value).__name__)
            for key in value.keys():
                node = doc.createElement('entry')
                node.setAttribute('key', key)
                node.appendChild(self.serialize_value(doc, value[key]))
                v.appendChild(node)
            return v
        elif type(value) in builtinlist:
            v = doc.createElement(type(value).__name__)
            v.setAttribute('value', str(value))
        else:
            v = self.serialize_subclass(doc, value)
        return v

    def serialize_subclass(self, doc, w):
        # check if class hav(e already been serialized
        classid = w.__hash__()
        if classid in self.maps:
            root = doc.createElement('refobject')
            root.setAttribute('classid', str(classid))
            return root

        # ok, create the class
        root = doc.createElement(w.__class__.__name__)
        root.setAttribute('classid', str(classid))
        # add to maps
        self.maps[classid] = (w, root)
        # fill the class
        for name, value in inspect.getmembers(w):
            if name.startswith('__'):
                continue
            if type(value) == new.instancemethod:
                continue
            p = doc.createElement('prop')
            p.setAttribute('name', name)
            if value is not None:
                value = self.serialize_value(doc, value)
                p.appendChild(value)
            root.appendChild(p)

        return root

    def serialize(self, w):
        doc = x.Document()
        root = self.serialize_subclass(doc, w)
        doc.appendChild(root)
        return doc.toprettyxml()


    def unserialize_value(self, node):
        value = None

        # search the type node
        ptype = node.nodeName
        ptypenode = node

        if ptype is None:
            value = None
        elif ptype in builtinliststr:
            pvalue = node.getAttribute('value')
            if ptype == 'str':
                s = '%s("%s")' % (ptype, pvalue.replace('"', '\"'))
            elif ptype == 'unicode':
                s = '%s(u"%s")' % (ptype, pvalue.replace('"', '\"'))
            else:
                s = '%s(%s)' % (ptype, pvalue)
            # FIXME secure this
            pvalue = eval(s)

        elif ptype in ('list', 'tuple'):
            value = list()
            for x in node.childNodes:
                if x.nodeType != 1:
                    continue
                value.append(self.unserialize_value(x))
            if ptype == 'tuple':
                value = tuple(value)

        elif ptype == 'dict':
            value = dict()
            for x in node.childNodes:
                if x.nodeType != 1:
                    continue
                key = x.getAttribute('key')
                val = None
                for x2 in x.childNodes:
                    if x2.nodeType != 1:
                        continue
                    val = self.unserialize_value(x2)
                    break
                value[key] = val
        elif ptype == 'refobject':
            classid = node.getAttribute('classid')
            value = self.maps[classid]
        else:
            value = self.unserialize_subclass(node)
        return value

    def unserialize_subclass(self, node):
        print 'unserialize_subclass', node

        # get classid
        classid = node.getAttribute('classid')

        # search widget, and create
        clsobj = MTWidgetFactory.get(node.nodeName)
        cls = object.__new__(clsobj)

        # set to map
        self.maps[classid] = cls

        for child in node.childNodes:
            # accept only nodes
            if child.nodeType != 1:
                continue
            # got prop node ?
            assert(child.nodeName == 'prop')
            value = None
            valuenode = None
            key = child.getAttribute('name')
            for subchild in child.childNodes:
                if subchild.nodeType != 1:
                    continue
                valuenode = subchild
            if valuenode is not None:
                value = self.unserialize_value(valuenode)
            print 'update', cls, key, value
            cls.__dict__.update({key: value})

        return cls

    def unserialize(self, data):
        doc = x.parseString(data)
        instance = self.unserialize_subclass(doc.childNodes[0])
        return instance


box = MTBoxLayout()
box.add_widget(MTSlider(max=2000, value=500))
box.add_widget(MTSlider(value=75, orientation='horizontal'))

data = NetworkShare()
xml = data.serialize(box)
print 'OUTPUT XML'
print xml

data = NetworkShare()
box = data.unserialize(xml)
runTouchApp(box)
