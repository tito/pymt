'''
Serializer: a way to save and restore a widget tree.

Many methods are available to control serialization of a class :
    * __serialize_start__() : called when serialization on the object start. if False, object will be not serialized
    * __serialize_classname__() : may return the real classname to use
    * __serialize_member__(member) : ask the value of a member, if None, the member will be skipped
    * __serialize_end__() : end of serialization
    * __unserialize_start__() : unserialization start
    * __unserialize_end__() : end of unserialization

All methods implementation in class are optionnals.

Limitations
===========

Serializer can't handle :
    * non-object class based (all class must derivate from object class)
    * callbacks (callback on a widget are attached at runtime so...)
    * pure-gl objects (based on ctypes or not)

Serializer handle :
    * all object class with builtins properties
    * recursivity link between objects

Simple serialization example
============================

Serializer example ::
    serializer = Serializer()
    widget = MTWidget()
    data = serializer.serialize(widget)

Unserializer example ::
    widget = serialize.unserialize(data)

How serialization work ?
========================

In the example upside, `data` will contains the widget in a serialized version.
The whole process consist to :
    * 1. call the __serialize_start__() on the widget
    * 2. get the widget name from __class__.__name__
    * 3. get the widget name from __serialize_classname__() if found
    * 4. enumerate all members on the class (except member starting with __)
    * 5. get the widget attribute value with __serialize_member__(attribute),
         or fallback with getattr if the method is not implemented
    * 6. if it's a class, start from the 1. for the subclass.
    * 7. call the __serialize_end__() on the widget

'''

import pymt
from pymt.logger import pymt_logger
from pymt.ui.factory import MTWidgetFactory

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
import array


builtinlist = (int, float, str, unicode, long, float, complex, bool)
builtinliststr = map(lambda x: x.__name__, builtinlist)

class SerializerNetworkException(Exception):
    '''Exception for network serializer'''
    def __init__(self, msg):
        self.msg = msg


class SerializerNetworkMessage(object):
    '''The object will handle a network message.

    :Attributes:
        `command` : int
            Command index (COMMAND_ERROR, COMMAND_SENDXML)

        `data` : bytes
            Will contain the data part of message

        `datasize` : int
            Size of data

        `timestamp` : float
            Timestamp of the packet
    '''

    PROTOCOL_VERSION    = 0x01

    # protocol version 0x01
    COMMAND_HELLO       = 0x01
    COMMAND_ERROR       = 0x02
    COMMAND_SENDXML     = 0x03

    # header size
    HEADER_FORMAT       = 'IfhhI'
    HEADER_SIZE         = struct.calcsize(HEADER_FORMAT)

    # supported timestamp shifting
    TIMESTAMP_SHIFT     = 172800 # 2 days

    _id = 0
    def __init__(self, command=None, data='', fromheader=None):
        if fromheader:
            # Message from network
            self.unpack_header(fromheader)
            self.data = ''
        else:
            # Message from user
            self._id += 1
            self.id = self._id
            self.datasize = len(data)
            self.timestamp = time.time()
            self.command = command
            self.protocol_version = self.PROTOCOL_VERSION
            self.data = data

    def unpack_header(self, data):
        '''Unpack the data header to the class'''
        # verify header size
        if len(data) != self.HEADER_SIZE:
            raise SerializerNetworkException('Invalid header size (%d instead of %d)' % (
                len(data), self.HEADER_SIZE))

        (self.id, self.timestamp, self.protocol_version,
         self.command, self.datasize) = struct.unpack(self.HEADER_FORMAT, data)

        # ensure the protocol version
        if self.protocol_version != self.PROTOCOL_VERSION:
            raise SerializerNetworkException('Unsupported protocol %d' % self.protocol_version)

        # ensure the command version
        if self.command < 0x01 or self.command > 0x04:
            raise SerializerNetworkException('Unsupported command %d' % self.command)

        # ensure the timestamp
        if self.timestamp < time.time() - self.TIMESTAMP_SHIFT or \
           self.timestamp > time.time() + self.TIMESTAMP_SHIFT:
            raise SerializerNetworkException(
                    'Timestamp is too far from actual time (%d, current is %d, allowed shift is %d)'
                    % (self.timestamp, time.time(), self.TIMESTAMP_SHIFT))

    def pack_header(self):
        '''Get the header in pack version to transmit'''
        # id, timestamp, protocol version, command, datasize
        data = struct.pack(self.HEADER_FORMAT, self.id, self.timestamp,
                self.PROTOCOL_VERSION, self.command, self.datasize)
        return data

    def pack_data(self):
        '''Get the data in pack version to transmit'''
        return self.data

    def __str__(self):
        return '<SerializerNetworkMessage id=%d datasize=%d timestamp=%d command=%d protocol_version=%d>' % (
            self.id, self.datasize, self.timestamp, self.command, self.protocol_version)


class SerializerNetworkClient(threading.Thread):
    '''
    Create a network client, to send data on a Serializer server.

    :Parameters:
        `host` : str
            Server to connect
        `port` : int, default to 12000
            Port on server

    :Attributes:
        `is_running` : bool
            Indicate if the client is currently running
        `have_socket` : bool
            Indicate if the socket is created

    Note.. ::
        The client is a thread, it will start himself as soon as the class is created.
    '''
    def __init__(self, host, port=12000):
        super(SerializerNetworkClient, self).__init__()
        self.daemon         = True
        self.host           = host
        self.port           = port
        self.is_running     = True
        self.have_socket    = False

        self._queue         = collections.deque()
        self._sem           = threading.Semaphore(0)

        self.start()

    def stop(self):
        '''Stop the client'''
        self.is_running = False

    def waitstop(self):
        '''Wait that the client is stopped'''
        self.stop()
        while self.is_running:
            time.sleep(.5)

    def _errorclose(self, data):
        message = SerializerNetworkMessage(command=SerializerNetworkMessage.COMMAND_ERROR, data=data)
        self._send(message.pack_header())
        self._send(message.pack_data())
        self._close()
        self.stop()

    def _close(self):
        if not self.have_socket:
            return
        try:
            self.socket.close()
            self.socket = None
        except:
            pass

    def _recv(self, size):
        data = ''
        while len(data) < size:
            d = self.socket.recv(size - len(data))
            if len(d) <= 0:
                return None
            data += d
        return data

    def _send(self, data):
        sent = 0
        while sent < len(data):
            s = self.socket.send(data[sent:])
            if s <= 0:
                return 0
            sent += s
        return s

    def run(self):

        #
        # 1. Connect to the server
        #
        self.have_socket = False
        while not self.have_socket and self.is_running:
            try:
                pymt_logger.info('Connecting to %s:%d' % (self.host, self.port))

                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(0.5)

                self.socket.connect((self.host, self.port))
                self.have_socket = True

                pymt_logger.info('Connected to %s:%d' % (self.host, self.port))

            except Exception, e:

                error, message = e.args

                # special handle for EADDRINUSE
                if error == errno.EADDRINUSE:
                    pymt_logger.error('Address %s:%i already in use, retry in 2 second' % (self.host, self.port))
                else:
                    pymt_logger.exception(e)

                self.have_socket = False
                time.sleep(2)

        #
        # 2. Receive the HELLO command from the server
        #
        try:
            data = self._recv(SerializerNetworkMessage.HEADER_SIZE)
            if data is None:
                pymt_logger.error('Error in recv()')
                self._close()
                return
            message = SerializerNetworkMessage(fromheader=data)
            if message.command != SerializerNetworkMessage.COMMAND_HELLO:
                self._errorclose('Invalid HELLO packet')
                return
            pymt_logger.info('Server hello, protocol is %d' % message.protocol_version)
        except SerializerNetworkException, e:
            pymt_logger.exception('Error at HELLO packet: %s' % e.msg)
            self._close()
            return


        #
        # 3. Send all queues messages
        #
        while self.is_running:

            # get a message
            pymt_logger.debug('Waiting for message')
            self._sem.acquire()
            try:
                msg = self._queue.pop()
                pymt_logger.debug('Got a message to send : %s', str(msg))
            except:
                continue

            # send data
            if self._send(msg.pack_header()) is None:
                pymt_logger.error('Error while sending data')
                break
            if self._send(msg.pack_data()) is None:
                pymt_logger.error('Error while sending data')
                break

        #
        # 4. Exist from main loop
        #
        self._close()


    def send_xml(self, data):
        '''Send a XML data to the server'''
        # create network message
        msg = SerializerNetworkMessage(
                SerializerNetworkMessage.COMMAND_SENDXML, data)
        # add to the queue
        self._queue.appendleft(msg)
        # increment semaphore
        self._sem.release()

    def send_widget(self, widget):
        '''Send a widget to the server (will be converted into XML)'''
        serializer = Serializer()
        data = serializer.serialize(widget)
        self.send_xml(data)

class _SerializerNetworkServerChild(threading.Thread):
    def __init__(self, s, address, id, queue):
        super(_SerializerNetworkServerChild, self).__init__()
        self.queue              = queue
        self.socket             = s
        self.host, self.port    = address
        self.id                 = id
        self.is_running         = True
        self.daemon             = True

    def _handle(self, message):
        if message.command == SerializerNetworkMessage.COMMAND_ERROR:
            pymt_logger.warning('Client %d send an error: <%s>' % (self.id, str(message.data)))
        elif message.command == SerializerNetworkMessage.COMMAND_HELLO:
            pass
        elif message.command == SerializerNetworkMessage.COMMAND_SENDXML:
            self.queue.appendleft((self.id, message))
        else:
            pymt_logger.warning('Client %d drop unhandled message %d' % (self.id, message.command))

    def _recv(self, size):
        data = ''
        while len(data) < size:
            d = self.socket.recv(size - len(data))
            if len(d) <= 0:
                return None
            data += d
        return data

    def _send(self, data):
        sent = 0
        while sent < len(data):
            s = self.socket.send(data[sent:])
            if s <= 0:
                return None
            sent += s
        return sent

    def run(self):
        pymt_logger.info('Client %d connected from %s:%d' % (self.id, self.host, self.port))
        self.socket.settimeout(0.5)

        # Send an hello message
        message = SerializerNetworkMessage(command=SerializerNetworkMessage.COMMAND_HELLO)
        self._send(message.pack_header())
        self._send(message.pack_data())

        # Enter in the loop :)
        while self.is_running:
            try:
                data = self._recv(SerializerNetworkMessage.HEADER_SIZE)
                if data is None:
                    pymt_logger.error('Client %d recv header' % self.id)
                    break

                # create the message from the data
                message = SerializerNetworkMessage(fromheader=data)
                if message.datasize > 0:
                    message.data = self._recv(message.datasize)
                    if message.data is None:
                        pymt_logger.error('Client %d recv data' % self.id)

                # handle the message
                self._handle(message)

            except SerializerNetworkException, e:
                pymt_logger.warning('Error on client %d: %s' % (self.id, e.msg))

            except Exception, e:
                if type(e) == socket.timeout:
                    continue
                pymt_logger.exception('Error in SerializerNetworkServer recv()')
                break

        pymt_logger.info('Client %d disconnected' % (self.id))
        self.is_running = False



class SerializerNetworkServer(threading.Thread):
    '''Start a serializer server.

    :Parameters:
        `host` : str, default to '0.0.0.0'
            Address to listen
        `port` : int, default to 12000
            Port to listen


    :Attributes:
        `queue` : deque with (clientid, message) format
            The queue with all message for client
            He must handle itself unserialization if needed.
        `is_running` : bool
            Indicate if the client is currently running
        `have_socket` : bool
            Indicate if the socket is created
    '''
    def __init__(self, host='0.0.0.0', port=12000):
        super(SerializerNetworkServer, self).__init__()
        self.host           = host
        self.port           = port
        self.have_socket    = False
        self.is_running     = True
        self.clients        = {}
        self._id            = 0
        self.daemon         = True
        self.queue          = collections.deque()
        self.start()

    def stop(self):
        '''Stop the server'''
        self.is_running = False

    def waitstop(self):
        '''Wait that the server is stopped'''
        self.stop()
        while self.is_running:
            time.sleep(1.)

    def run(self):
        #
        # 1. create the socket
        #
        self.have_socket = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if os.name in ('posix', 'mac') and hasattr(socket, 'SO_REUSEADDR'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        #
        # 2. bind the socket
        #
        while not self.have_socket and self.is_running:
            try:
                self.socket.bind((self.host, self.port))
                self.socket.listen(5)
                self.socket.settimeout(0.5)
                self.have_socket = True
                pymt_logger.info('Listen on %s:%d' % (self.host, self.port))
            except socket.error, e:
                error, message = e.args

                # special handle for EADDRINUSE
                if error == errno.EADDRINUSE:
                    pymt_logger.error('Address %s:%i already in use, retry in 2 second' % (self.host, self.port))
                else:
                    pymt_logger.exception(e)
                self.have_socket = False

                time.sleep(2)

        #
        # 3. accept client
        #
        while self.is_running:
            try:
                (clientsocket, address) = self.socket.accept()
                self._id += 1
                ct = _SerializerNetworkServerChild(clientsocket, address, self._id, self.queue)
                ct.run()
                self.clients[self._id] = ct
            except socket.error, e:
                if type(e) == socket.timeout:
                    continue
                pymt_logger.exception('')

        #
        # 4. close
        #
        if not self.have_socket:
            return
        try:
            self.socket.close()
        except:
            pass


class Serializer:
    '''Class to use for serialize / unserialize widget.'''
    def __init__(self):
        self.maps = {}

    def _serialize_value(self, doc, value):
        if value is None:
            v = doc.createElement('None')
        elif type(value) in (list, tuple):
            v = doc.createElement(type(value).__name__)
            for element in value:
                c = self._serialize_value(doc, element)
                if c is None:
                    continue
                v.appendChild(c)
            return v
        elif type(value) in (dict, ):
            v = doc.createElement(type(value).__name__)
            for key in value.keys():
                c = self._serialize_value(doc, value[key])
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
            v = self._serialize_subclass(doc, value)
        return v

    def _serialize_subclass(self, doc, w):
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
            pymt_logger.debug('Missing __serialize_start__ for <%s>' % w.__class__.__name__)
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
                pymt_logger.debug('Missing __serialize_member__ for <%s>' % w.__class__.__name__)
                value = getattr(w, name)
            if value is None:
                continue

            p = doc.createElement('prop')
            p.setAttribute('name', name)
            if value is not None:
                try:
                    pymt_logger.debug(
                        'Serialize subclass %s:%s:%s' %
                        (w.__class__.__name__, name, str(value)))
                    value = self._serialize_value(doc, value)
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
            pymt_logger.debug('Missing __serialize_end__ for <%s>' % w.__class__.__name__)
            pass

        return root

    def serialize(self, w):
        '''Serialize a widget into a string.
        Usage ::
            w = MTWidget()
            data = Serializer().serialize(w)
        '''
        doc = x.Document()
        root = self._serialize_subclass(doc, w)
        if root is not None:
            doc.appendChild(root)
        return doc.toprettyxml()


    def _unserialize_value(self, node):
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
                value.append(self._unserialize_value(x))
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
                    val = self._unserialize_value(x2)
                    break
                value[key] = val
        elif ptype == 'refobject':
            classid = node.getAttribute('classid')
            value = self.maps[classid]
        else:
            value = self._unserialize_subclass(node)
        return value


    def _unserialize_subclass(self, node):

        # get classid
        classid = node.getAttribute('classid')

        # search widget, and create
        try:
            clsobj = MTWidgetFactory.get(node.nodeName)
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
            pymt_logger.debug('Missing __unserialize_start__ for <%s>' % node.nodeName)
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
                value = self._unserialize_value(valuenode)
            cls.__setattr__(key, value)

        try:
            cls.__unserialize_end__()
        except:
            pymt_logger.debug('Missing __unserialize_end__ for <%s>' % node.nodeName)
            pass

        return cls

    def unserialize(self, data):
        '''Unserialize a string into a widget.
        Usage ::
            widget = Serializer().unserialize(xmlstring)
        '''
        doc = x.parseString(data)
        instance = self._unserialize_subclass(doc.childNodes[0])
        return instance

