#
# New extension XInputExtension for python-xlib.
#
# Copyright (C) 2010 Mathieu Virbel <tito@bankiz.org>
#
#
# Note: this is currently in development
# Some changes is needed into python-xlib, to support GenericEvent
# Otherwise, as soon as you ask for event from a MT hardware,
# it will completly failed, and crash python-xlib.
#

import struct
from Xlib import X
from Xlib.protocol import rq, structs

extname = 'XInputExtension'

X_XIQueryPointer        = 40
X_XIWarpPointer         = 41
X_XIChangeCursor        = 42
X_XIChangeHierarchy     = 43
X_XISetClientPointer    = 44
X_XIGetClientPointer    = 45
X_XISelectEvents        = 46
X_XIQueryVersion        = 47
X_XIQueryDevice         = 48
X_XISetFocus            = 49
X_XIGetFocus            = 50
X_XIGrabDevice          = 51
X_XIUngrabDevice        = 52
X_XIAllowEvents         = 53
X_XIPassiveGrabDevice   = 54
X_XIPassiveUngrabDevice = 55
X_XIListProperties      = 56
X_XIChangeProperty      = 57
X_XIDeleteProperty      = 58
X_XIGetProperty         = 59
X_XIGetSelectedEvents   = 60

# Device types
XIMasterPointer         = 1
XIMasterKeyboard        = 2
XISlavePointer          = 3
XISlaveKeyboard         = 4
XIFloatingSlave         = 5

# Device classes
XIKeyClass              = 0
XIButtonClass           = 1
XIValuatorClass         = 2

# Fake device ID's for event selection
XIAllDevices            = 0
XIAllMasterDevices      = 1

# Event types
XI_DeviceChanged        = 1
XI_KeyPress             = 2
XI_KeyRelease           = 3
XI_ButtonPress          = 4
XI_ButtonRelease        = 5
XI_Motion               = 6
XI_Enter                = 7
XI_Leave                = 8
XI_FocusIn              = 9
XI_FocusOut             = 10
XI_HierarchyChanged     = 11
XI_PropertyEvent        = 12
XI_RawKeyPress          = 13
XI_RawKeyRelease        = 14
XI_RawButtonPress       = 15
XI_RawButtonRelease     = 16
XI_RawMotion            = 17

def XISetMask(ptr, event):
    ptr[(event)>>3] |=  (1 << ((event) & 7))

def XIClearMask(ptr, event):
    ptr[(event)>>3] &= ~(1 << ((event) & 7))

def XIMaskIsSet(ptr, event):
    return ptr[(event)>>3] & (1 << ((event) & 7))

class Card64(rq.ValueField):
    structcode = 'q'
    structvalues = 1

# Requests #

class QueryVersion(rq.ReplyRequest):
    _request = rq.Struct(
        rq.Card8('opcode'),
        rq.Opcode(X_XIQueryVersion),
        rq.RequestLength(),
        rq.Card16('major_version'),
        rq.Card16('minor_version'),
        )
    _reply = rq.Struct(
        rq.ReplyCode(),
        rq.Pad(1),
        rq.Card16('sequence_number'),
        rq.ReplyLength(),
        rq.Card32('major_version'),
        rq.Card32('minor_version')
        )

def query_version(self):
    """Get the current version of the RandR extension.

    """
    return QueryVersion(
        display=self.display,
        opcode=self.display.get_extension_major(extname),
        major_version=2,
        minor_version=0,
        )


# http://cgit.freedesktop.org/xorg/lib/libXi/tree/src/XIQueryDevice.c?id=d0be870ee7798deb8cb50cdf350892c9dfc64538

ButtonState = rq.Struct(
    rq.LengthOf('mask', 2),
    rq.String8('mask')
    )

AnyInfo = rq.Struct(
    rq.Card16('type'),
    rq.Card16('length'),
    rq.Card16('sourceid'),
    rq.Card16('pad'),
    )

ButtonInfo = rq.Struct(
    rq.Card16('type'),
    rq.Card16('length'),
    rq.Card16('sourceid'),
    rq.LengthOf('buttons', 2),
    rq.List('buttons', rq.Card32),
    )

KeyInfo = rq.Struct(
    rq.Card16('type'),
    rq.Card16('length'),
    rq.Card16('sourceid'),
    rq.LengthOf('keys', 2),
    rq.List('keys', rq.Int32)
    )

ValuatorInfo = rq.Struct(
    rq.Card16('type'),
    rq.Card16('length'),
    rq.Card16('sourceid'),
    rq.Card16('number'),
    rq.Card32('label'),
    rq.Int32('min'),
    rq.Int32('max'),
    rq.Int32('value'),
    rq.Card32('resolution'),
    rq.Card8('mode'),
    rq.Pad(3)
    )

class DeviceInfoClasses(rq.ValueField):
    structcode = None
    def __init__(self, name):
        ValueField.__init__(self, name)

    @staticmethod
    def parse_binary(data, display):
        info, d = AnyInfo.parse_binary(data, display)

        if info.type == XIButtonClass:
            c = ButtonInfo
            t = 'ButtonInfo'
        elif info.type == XIKeyClass:
            c = KeyInfo
            t = 'KeyInfo'
        elif info.type == XIValuatorClass:
            c = ValuatorInfo
            t = 'ValuatorInfo'
        else:
            raise Exception('Unknown info.type=%d, please implement!' %
                            info.type)

        v, d = c.parse_binary(data, display)

        return v, buffer(data, info.length * 4)

DeviceInfo = rq.Struct(
    rq.Card16('device_id'),
    rq.Card16('use'),
    rq.Card16('attachment'),
    rq.LengthOf('classes', 2),
    rq.LengthOf('name', 2),
    rq.Card8('enabled'),
    rq.Pad(1),
    rq.String8('name', pad=1),
    rq.List('classes', DeviceInfoClasses),
    )


class QueryDevice(rq.ReplyRequest):
    _request = rq.Struct(
        rq.Card8('opcode'),
        rq.Opcode(X_XIQueryDevice),
        rq.RequestLength(),
        rq.Card16('device_id'),
        rq.Pad(2)
        )

    _reply = rq.Struct(
        rq.ReplyCode(),
        rq.Pad(1),
        rq.Card16('sequence_number'),
        rq.ReplyLength(),
        rq.LengthOf('devices', 2),
        #rq.Card16('num_devices'),
        rq.Pad(22),
        rq.List('devices', DeviceInfo, pad=0)
        #rq.FixedString('devices', 1024)
        )

def query_device(self, device_id):
    return QueryDevice(
        display=self.display,
        opcode=self.display.get_extension_major(extname),
        device_id=device_id
        )

class ListProperties(rq.ReplyRequest):
    _request = rq.Struct(
        rq.Card8('opcode'),
        rq.Opcode(X_XIListProperties),
        rq.RequestLength(),
        rq.Card16('device_id'),
        rq.Pad(2)
        )
    _reply = rq.Struct(
        rq.ReplyCode(),
        rq.Pad(1),
        rq.Card16('sequence_number'),
        rq.ReplyLength(),
        rq.LengthOf('properties', 2),
        rq.Pad(22),
        rq.List('properties', rq.Card32)
        )

def list_properties(self, device_id):
    return ListProperties(
        display=self.display,
        opcode=self.display.get_extension_major(extname),
        device_id=device_id
        )

class GetProperty(rq.ReplyRequest):
    _request = rq.Struct(
        rq.Card8('opcode'),
        rq.Opcode(X_XIGetProperty),
        rq.RequestLength(),
        rq.Card16('device_id'),
        rq.Card8('delete'),
        rq.Pad(1),
        rq.Card32('property'),
        rq.Card32('type'),
        rq.Card32('offset'),
        rq.Card32('len'),
        )
    _reply = rq.Struct(
        rq.ReplyCode(),
        rq.Pad(1),
        rq.Card16('sequence_number'),
        rq.ReplyLength(),
        rq.Card32('type'),
        rq.Card32('bytes_after'),
        rq.LengthOf('value', 4),
        rq.Card8('format'),
        rq.Pad(11),
        rq.String8('value'),
        )

def get_property(self, device_id, property, type, offset, len, delete=0):
    # FIXME if bytes_after is in request, redo a request to fetch
    # the rest of the value, until bytes_after is 0
    return GetProperty(
        display=self.display,
        opcode=self.display.get_extension_major(extname),
        device_id=device_id,
        property=property,
        type=type,
        offset=offset,
        len=len,
        delete=delete
        )

    _reply = rq.Struct(
        rq.ReplyCode(),
        rq.Pad(1),
        rq.Card16('sequence_number'),
        rq.ReplyLength(),
        rq.Card32('major_version'),
        rq.Card32('minor_version')
        )

class ChangeProperty(rq.Request):
    _request = rq.Struct(
        rq.Card8('opcode'),
        rq.Opcode(X_XIChangeProperty),
        rq.RequestLength(),
        rq.Card16('device_id'),
        rq.Card8('mode'),
        rq.Card8('format'),
        rq.Card32('property'),
        rq.Card32('type'),
        rq.Card32('num_items'),
        rq.Int32('value'),
    )

def change_property(self, device_id, property, type, format, value):
    # TODO change to be everything, not only int
    return ChangeProperty(
        display=self.display,
        opcode=self.display.get_extension_major(extname),
        device_id=device_id,
        mode=0, # PropModeReplace
        property=property,
        type=type,
        format=format,
        num_items=1,
        value=value)

EventMask = rq.Struct(
    rq.Card16('device_id'),
    rq.LengthOf('mask', 2),
    rq.List('mask', rq.Card8)
)

class GrabDevice(rq.ReplyRequest):
    _request = rq.Struct(
        rq.Card8('opcode'),
        rq.Opcode(X_XIGrabDevice),
        rq.RequestLength(),
        rq.Card32('window'),
        rq.Card32('time'),
        rq.Card32('cursor'),
        rq.Card16('device_id'),
        rq.Set('grab_mode', 1, (X.GrabModeSync, X.GrabModeAsync)),
        rq.Card8('paired_device_mode'),
        rq.Card8('owner_events'),
        rq.Pad(1),
        rq.LengthOf('masks', 2),
        rq.List('masks', EventMask)
        )
    _reply = rq.Struct(
        rq.ReplyCode(),
        rq.Pad(1),
        rq.Card16('sequence_number'),
        rq.ReplyLength(),
        rq.Card8('status'),
        rq.Pad(23)
        )

def grab_device(self, device_id, masks,
                grab_mode=X.GrabModeSync,
                paired_device_mode=X.GrabModeSync,
                owner_events=0):
    return GrabDevice(
        display=self.display,
        window=self.id,
        opcode=self.display.get_extension_major(extname),
        time=X.CurrentTime,
        cursor=0,
        device_id=device_id,
        grab_mode=grab_mode,
        paired_device_mode=paired_device_mode,
        owner_events=owner_events,
        masks=masks)

class UngrabDevice(rq.Request):
    _request = rq.Struct(
        rq.Card8('opcode'),
        rq.Opcode(X_XIUngrabDevice),
        rq.RequestLength(),
        rq.Card32('time'),
        rq.Card16('device_id'),
        rq.Pad(2)
        )

def ungrab_device(self, device_id):
    return UngrabDevice(
        display=self.display,
        opcode=self.display.get_extension_major(extname),
        time=X.CurrentTime,
        device_id=device_id)

class SelectEvent(rq.Request):
    _request = rq.Struct(
        rq.Card8('opcode'),
        rq.Opcode(X_XISelectEvents),
        rq.RequestLength(),
        rq.Card32('window'),
        rq.LengthOf('masks', 2),
        rq.Pad(2),
        rq.List('masks', EventMask)
        )

def select_event(self, masks):
    return SelectEvent(
        display=self.display,
        opcode=self.display.get_extension_major(extname),
        window=self.id,
        masks=masks)

X_GenericEvent = 35
X_GenericEventCookie = 36

class RawField(rq.ValueField):
    """A field with raw data, stored as a string"""
    structcode = None
    def pack_value(self, val):
        return val, len(val), None
    def parse_binary_value(self, data, display, length, format):
        return str(data), ''

class GenericEvent(rq.Event):
    _code = X_GenericEvent
    _fields = rq.Struct(
        rq.Card8('type'),
        rq.Card8('extension'),
        rq.Card16('sequence_number'),
        rq.Card32('length'),
        rq.Int16('evtype'),
        rq.Int16('device_id'),
        rq.Card32('time'),
        rq.Card32('detail'),
        rq.FixedString('header', 12),
        RawField('data')
    )

import Xlib.protocol.display
Xlib.protocol.display.Display.event_classes[X_GenericEvent] = GenericEvent

def setup(disp):
    info = disp.query_extension(extname)
    disp.display.set_extension_major(extname, info.major_opcode)
    disp.extension_add_method('display', 'xi2_query_version', query_version)
    disp.extension_add_method('display', 'xi2_query_device', query_device)
    disp.extension_add_method('display', 'xi2_list_properties', list_properties)
    disp.extension_add_method('display', 'xi2_change_property', change_property)
    disp.extension_add_method('window', 'xi2_grab_device', grab_device)
    disp.extension_add_method('window', 'xi2_ungrab_device', ungrab_device)
    disp.extension_add_method('window', 'xi2_select_event', select_event)

if __name__ == '__main__':
    from Xlib import X, display, Xutil

    disp = display.Display()
    setup(disp)

    print '== XInputExtension ==', info.major_opcode

    prop_tracking_id = disp.get_atom('Abs MT Tracking ID')
    prop_multitouch = disp.get_atom('Evdev MultiTouch')
    print 'Atom Tracking ID = ', prop_tracking_id
    print 'Atom Multitouch = ', prop_multitouch

    version = disp.xi2_query_version()
    print 'Version = %d.%d' % (version.major_version, version.minor_version)
    devices = disp.xi2_query_device(XIAllDevices)
    print 'Number of devices = %d' % len(devices.devices)

    root = disp.screen().root
    print 'Root =', root.id

    for device in devices.devices:
        props = disp.xi2_list_properties(device.device_id)
        print ''
        print '*', device.name
        print device
        for cls in device.classes:
            print 'cls', cls
        for x in props.properties:
            print ' \-', disp.get_atom_name(x)

        if prop_multitouch not in props.properties:
            continue

        print '-> Enable multitouch'

        '''
        print '-> Remove Ghost slaves'
        disp.xi2_change_property(device_id=device.device_id,
                                 format=8,
                                 type=19, # XA_INTEGER
                                 property=prop_multitouch,
                                 value=0)
        disp.flush()

        print '-> Activate 20 slaves'
        disp.xi2_change_property(device_id=device.device_id,
                                 format=8,
                                 type=19, # XA_INTEGER
                                 property=prop_multitouch,
                                 value=1)
        disp.flush()
        '''

        mask = rq.DictWrapper({})
        mask.device_id = XIAllDevices #device.device_id
        mask.mask = [0,0]
        XISetMask(mask.mask, XI_Motion)
        print mask.mask

        disp.flush()
        print root.xi2_grab_device(device_id=device.device_id, masks=[mask])
        #print root.xi2_ungrab_device(device_id=device.device_id)

    print 'Starting loop...'
    disp.flush()
    mt = rq.Struct(
        Card64('x'),
        Card64('y'),
        Card64('sx'),
        Card64('sy'),
        rq.Pad(24),
        rq.Int32('id'),
        rq.Int32('_1'),
        rq.Int32('_2'),
        rq.Int32('_3'),
        rq.Int32('use'),
        rq.Int32('_5'),
    )

    while 1:
        ev = root.display.next_event()
        d = ev.data[8:]

        v, d = mt.parse_binary(d, disp.display)
        print len(ev.data), ev, v

