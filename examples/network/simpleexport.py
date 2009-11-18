'''
Network serialization: a way to save and restore a widget tree

Many method are available for subclass ::
    * __serialize_start__() : called when serialization on the object start. if False, object will be not serialized
    * __serialize_classname__() : may return the real classname to use
    * __serialize_member__(member) : ask the value of a member, if None, the member will be skipped
    * __serialize_end__() : end of serialization
    * __unserialize_start__() : unserialization start
    * __unserialize_end__() : end of unserialization

'''


from pymt import *

import pymt
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
                c = self.serialize_value(doc, element)
                if c is None:
                    continue
                v.appendChild(c)
            return v
        elif type(value) in (dict, ):
            v = doc.createElement(type(value).__name__)
            for key in value.keys():
                c = self.serialize_value(doc, value[key])
                if c is None:
                    continue
                node = doc.createElement('entry')
                node.setAttribute('key', key)
                node.appendChild(c)
                v.appendChild(node)
            return v
        elif type(value) in builtinlist:
            v = doc.createElement(type(value).__name__)
            v.setAttribute('value', str(value))
        else:
            v = self.serialize_subclass(doc, value)
        return v

    def serialize_subclass(self, doc, w):
        # check if class have already been serialized
        classid = w.__hash__()
        if classid in self.maps:
            root = doc.createElement('refobject')
            root.setAttribute('classid', str(classid))
            return root

        # inform object that serialization start
        # object may return a list of attribute he want to serialize
        members = None
        try:
            members = w.__serialize_start__()
        except:
            pymt.pymt_logger.debug('Missing __serialize_start__ for <%s>' % w.__class__.__name__)
            pass

        # skip this subclass ?
        if members == False:
            return
        if type(members) not in (list, tuple):
            members = inspect.getmembers(w)

        # if class got a name for serialization ?
        classname = w.__class__.__name__
        try:
            classname = w.__serialize_classname__()
        except:
            pass


        # ok, create the class
        root = doc.createElement(classname)
        root.setAttribute('classid', str(classid))

        # add to maps
        self.maps[classid] = (w, root)

        # fill the class
        for name, value in members:
            if name.startswith('__'):
                continue

            # match name like _OBJNAME__value
            v = name.split('_', 2)
            if len(v) > 2 and v[2][0] == '_':
                continue

            # ignore instance
            if type(value) == new.instancemethod:
                continue

            # ignore constructed properties
            if hasattr(w.__class__, name):
                if type(getattr(w.__class__, name)) == property:
                    continue

            # ask to object about serialize the current member
            try:
                value = w.__serialize_member__(name)
            except:
                pymt.pymt_logger.debug('Missing __serialize_member__ for <%s>' % w.__class__.__name__)
                value = getattr(w, name)
            if value is None:
                continue

            p = doc.createElement('prop')
            p.setAttribute('name', name)
            if value is not None:
                try:
                    pymt.pymt_logger.debug(
                        'Serialize subclass %s:%s:%s' %
                        (w.__class__.__name__, name, str(value)))
                    value = self.serialize_value(doc, value)
                except:
                    print 'Error while serialize value for', w, name, value
                    raise
                if value is not None:
                    p.appendChild(value)
            root.appendChild(p)

        # inform object that serialization end
        try:
            w.__serialize_end__()
        except:
            pymt.pymt_logger.debug('Missing __serialize_end__ for <%s>' % w.__class__.__name__)
            pass

        return root

    def serialize(self, w):
        doc = x.Document()
        root = self.serialize_subclass(doc, w)
        if root is not None:
            doc.appendChild(root)
        return doc.toprettyxml()


    def unserialize_value(self, node):
        value = None

        # search the type node
        ptype = node.nodeName
        ptypenode = node

        if ptype in ('None', None):
            value = None
        elif ptype in builtinliststr:
            pvalue = node.getAttribute('value')
            if ptype == 'str':
                value = str(pvalue)
            elif ptype == 'unicode':
                value = unicode(pvalue)
            else:
                s = '%s(%s)' % (ptype, pvalue)
                # FIXME secure this
                value = eval(s)

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

        # get classid
        classid = node.getAttribute('classid')

        # search widget, and create
        try:
            clsobj = MTWidgetFactory.get(node.nodeName)
        except:
            try:
                # widget not found in factory ?
                clsobj = globals()[node.nodeName]
                print clsobj
            except:
                raise Exception('Unable to found a class for <%s>' % node.nodeName)
        cls = object.__new__(clsobj)

        try:
            cls.__unserialize_start__()
        except:
            pymt.pymt_logger.debug('Missing __unserialize_start__ for <%s>' % node.nodeName)
            pass

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
            cls.__setattr__(key, value)

        try:
            cls.__unserialize_end__()
        except:
            pymt.pymt_logger.debug('Missing __unserialize_end__ for <%s>' % node.nodeName)
            pass

        return cls

    def unserialize(self, data):
        doc = x.parseString(data)
        instance = self.unserialize_subclass(doc.childNodes[0])
        return instance


#box = MTBoxLayout()
#box.add_widget(MTSlider(max=2000, value=500))
#box.add_widget(MTSlider(value=75, orientation='horizontal'))
#box.add_widget(MTButton(label='hello'))
#box.add_widget(MTScatterWidget())
box = MTScatterWidget()

data = NetworkShare()
xml = data.serialize(box)
print 'OUTPUT XML'
print xml

data = NetworkShare()
box = data.unserialize(xml)

runTouchApp(box)

