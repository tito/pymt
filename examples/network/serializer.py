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

import pymt
import inspect
import new
import xml.dom.minidom as x
import threading
import socket
import struct
import time
import collections
import os
import errno


builtinlist = (int, float, str, unicode, long, float, complex, bool)
builtinliststr = map(lambda x: x.__name__, builtinlist)

class SerializerNetworkException(Exception):
    def __init__(self, msg):
        self.msg = msg

class SerializerNetworkMessage(object):
    PROTOCOL_VERSION    = 0x01

    # protocol version 0x01
    COMMAND_PINGREQUEST = 0x01
    COMMAND_PINGREPLY   = 0x02
    COMMAND_SENDXML     = 0x03
    COMMAND_ACKXML      = 0x04

    # header size
    HEADER_FORMAT       = 'IfhhI'
    HEADER_SIZE         = struct.calcsize(HEADER_FORMAT)

    # supported timestamp shifting
    TIMESTAMP_SHIFT     = 172800 # 2 days

    _id = 0
    def __init__(self, command=None, data=None, dataheader=None):
        if dataheader:
            # Message from network
            self.unpack_header(dataheader)
            self.data = None
        else:
            self._id += 1
            self.id = self._id
            self.datasize = len(data)
            self.timestamp = time.time()
            self.command = command
            self.protocol_version = self.PROTOCOL_VERSION
            self.data = data

    def unpack_header(self, data):
        # verify header size
        if len(data) != self.HEADER_SIZE:
            raise SerializerNetworkException('Invalid header size (%d instead of %d)' % (
                len(data), self.HEADER_SIZE))

        (self.id, self.timestamp, self.protocol_version,
         self.command, self.datasize) = struct.unpack(self.HEADER_FORMAT, data)

        # ensure validity of packet
        if self.protocol_version != self.PROTOCOL_VERSION:
            raise SerializerNetworkException('Unsupported protocol %d' % self.protocol_version)
        if self.command < 0x01 or self.command > 0x04:
            raise SerializerNetworkException('Unsupported command %d' % self.command)
        if self.timestamp < time.time() - self.TIMESTAMP_SHIFT or \
           self.timestamp > time.time() + self.TIMESTAMP_SHIFT:
            raise SerializerNetworkException('Timestamp is too far from actual time (%d, current is %d, allowed shift is %d)'
                    % (self.timestamp, time.time(), self.TIMESTAMP_SHIFT))

    def pack_header(self):
        # id, timestamp, protocol version, command, datasize
        return struct.pack(self.HEADER_FORMAT, self.id, self.timestamp,
                self.PROTOCOL_VERSION, self.command, self.datasize)

    def __str__(self):
        return '<SerializerNetworkMessage id=%d datasize=%d timestamp=%d command=%d protocol_version=%d>' % (
            self.id, self.datasize, self.timestamp, self.command, self.protocol_version)

class SerializerNetworkClient(threading.Thread):
    def __init__(self, host, port=12000):
        super(SerializerNetworkClient, self).__init__()
        self.host = host
        self.port = port
        self.is_running = False
        self.have_socket = False
        self.queue = collections.deque()
        self.sem = threading.Semaphore(0)
        self.daemon = True

    def run(self):
        self.have_socket = False
        self.is_running = True
        while not self.have_socket and self.is_running:
            try:
                pymt.pymt_logger.info('Connecting to %s:%d' % (self.host, self.port))
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(0.5)
                self.socket.connect((self.host, self.port))
                self.have_socket = True
                pymt.pymt_logger.info('Connected to %s:%d' % (self.host, self.port))
            except Exception, e:
                error, message = e.args
                # special handle for EADDRINUSE
                if error == errno.EADDRINUSE:
                    pymt.pymt_logger.error('Address %s:%i already in use, retry in 2 second' % (self.host, self.port))
                else:
                    pymt.pymt_logger.exception(e)
                self.have_socket = False
                time.sleep(2)

        while self.is_running:
            pymt.pymt_logger.debug('Waiting for message')
            self.sem.acquire()
            try:
                msg = self.queue.pop()
                pymt.pymt_logger.debug('Got a message to send : %s', str(msg))
            except:
                continue

            # send header
            data = msg.pack_header()
            sent = 0
            pymt.pymt_logger.debug('Sending header... (%d)' % len(data))
            while sent != len(data):
                sz = self.socket.send(data[sent:])
                sent += sz

            # send data
            data = msg.data
            sent = 0
            pymt.pymt_logger.debug('Sending data... (%d)', len(data))
            while sent != len(data):
                sz = self.socket.send(data)
                sent += sz

            pymt.pymt_logger.debug('Send done !')

    def send_xml(self, data):
        # create network message
        msg = SerializerNetworkMessage(
                SerializerNetworkMessage.COMMAND_SENDXML, data)
        pymt.pymt_logger.debug('Append new message')
        # add to the queue
        self.queue.appendleft(msg)
        # increment semaphore
        self.sem.release()

    def send_widget(self, widget):
        # Serialize the tree
        serializer = Serializer()
        data = serializer.serialize(widget)
        self.send_xml(data)

class SerializerNetworkServerChild(threading.Thread):
    def __init__(self, s, address, id, queue):
        super(SerializerNetworkServerChild, self).__init__()
        self.socket = s
        self.host, self.port = address
        self.id = id
        self.is_running = True
        self.daemon = True
        self.queue = queue

    def run(self):
        pymt.pymt_logger.info('Client %d connected from %s:%d' % (self.id, self.host, self.port))
        self.is_running = True
        self.socket.settimeout(0.5)
        while self.is_running:
            try:
                header = self.socket.recv(SerializerNetworkMessage.HEADER_SIZE)
                if len(header) == 0:
                    break
                pymt.pymt_logger.debug('Client %d sent a packet with size=%d' % (self.id, len(header)))
                message = SerializerNetworkMessage(dataheader=header)

                pymt.pymt_logger.debug('Client %d sent HEADER %s' % (self.id, str(message)))
                message.data = self.socket.recv(message.datasize)

                pymt.pymt_logger.debug('Client %d sent DATA %s' % (self.id, str(message)))

                self.queue.appendleft((self.id, message))

            except SerializerNetworkException, e:
                pymt.pymt_logger.warning('Error on client %d: %s' % (self.id, e.msg))
            except Exception, e:
                if type(e) == socket.timeout:
                    continue
                pymt.pymt_logger.exception('Error in SerializerNetworkServer recv()')
        pymt.pymt_logger.info('Client %d disconnected' % (self.id))
        self.is_running = False

class SerializerNetworkServer(threading.Thread):
    def __init__(self, host='127.0.0.1', port=12000):
        super(SerializerNetworkServer, self).__init__()
        self.host = host
        self.port = port
        self.have_socket = False
        self.is_running = True
        self.clients = {}
        self._id = 0
        self.daemon = True
        self.queue = collections.deque()

    def run(self):
        self.is_running = True
        self.have_socket = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if os.name in ('posix', 'mac') and hasattr(socket, 'SO_REUSEADDR'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        while not self.have_socket and self.is_running:
            try:
                self.socket.bind((self.host, self.port))
                self.socket.listen(5)
                self.socket.settimeout(0.5)
                self.have_socket = True
                pymt.pymt_logger.info('Listen on %s:%d' % (self.host, self.port))
            except socket.error, e:
                error, message = e.args

                # special handle for EADDRINUSE
                if error == errno.EADDRINUSE:
                    pymt.pymt_logger.error('Address %s:%i already in use, retry in 2 second' % (self.host, self.port))
                else:
                    pymt.pymt_logger.exception(e)
                self.have_socket = False

                time.sleep(2)

            while self.is_running:
                try:
                    (clientsocket, address) = self.socket.accept()
                    self._id += 1
                    ct = SerializerNetworkServerChild(clientsocket, address, self._id, self.queue)
                    ct.run()
                    self.clients[self._id] = ct
                except socket.error, e:
                    if type(e) == socket.timeout:
                        continue
                    pymt.pymt_logger.exception('')

class Serializer:

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
            clsobj = pymt.MTWidgetFactory.get(node.nodeName)
        except:
            try:
                # widget not found in factory ?
                clsobj = getattr(pymt, [node.nodeName])
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
