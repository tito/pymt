'''
Touch: base for all touch objects


Every touch in PyMT application are derivated from Touch class.
A touch can be more or less specific, it depend on the provider.
As example, TUIO provider can give you lot of information about position,
acceleration, width/height of the shape etc.. And the wiimote provider can
give you information about the button up/down etc...

So, we call that "capabilities.". Capabilities is handle in the "profile"
property on a Touch. It's a simple list with string that contains :

    * pos (tuio/property x, y)
    * pos3d (tuio/property x, y, z)
    * mov (tuio/property X, Y)
    * mov3d (tuio/property X, Y, Z)
    * dim (tuio/property w, h)
    * dim3d (tuio/property w, h, d)
    * markerid (tuio/property i (fid property))
    * sessionid (tuio/property s (id property))
    * angle (tuio/property a)
    * angle3D (tuio/property a, b, c)
    * rotacc (tuio/property A)
    * rotacc3d (tuio/property A, B, C)
    * motacc (tuio/property m)
    * shape (property shape)
    * kinetic
    * ... and other could be added by new classes

When you are on the on_touch_down(self, touch) handler, you can filter by
testing the profile ::

    def on_touch_down(self, touch):
        if 'markerid' not in touch:
            # not a fiducial, abandon
            return


'''

__all__ = ['Touch']

from ..clock import getClock

class Touch(object):
    '''Abstract class to represent a touch, and support TUIO 1.0 definition.

    :Parameters:
        `id` : str
            uniq ID of the touch
        `args` : list
            list of parameters, passed to depack() function
    '''

    __uniq_id = 0
    copy_attributes = \
        ('id','sx','sy','sz','a','b','c',
         'X','Y','Z','A','B','C','m','r',
         'profile','x','y','z','dxpos',
         'dypos','dzpos',)


    def __init__(self, device, id, args):
        if self.__class__ == Touch:
            raise NotImplementedError, 'class Touch is abstract'

        # Uniq ID
        Touch.__uniq_id += 1
        self.uid = Touch.__uniq_id
        self.device = device

        # For push/pop
        self.attr = []

        # For grab
        self.grab_list = []
        self.grab_exclusive_class = None
        self.grab_state = False
        self.grab_current = None

        # TUIO definition
        self.id = id
        self.sx = 0.0
        self.sy = 0.0
        self.sz = 0.0
        self.a = 0.0
        self.b = 0.0
        self.c = 0.0
        self.X = 0.0
        self.Y = 0.0
        self.Z = 0.0
        self.A = 0.0
        self.B = 0.0
        self.C = 0.0
        self.m = 0.0
        self.r = 0.0
        self.profile = ('pos', )

        # new parameters
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.shape = None
        self.dxpos = None
        self.dypos = None
        self.dzpos = None
        self.oxpos = None
        self.oypos = None
        self.ozpos = None
        self.time_start = getClock().get_time()
        self.is_timeout = False
        self.have_event_down = False
        self.do_event = None
        self.is_double_tap = False
        self.double_tap_time = 0
        self.no_event = False
        self.userdata = {}

        self.depack(args)

    def depack(self, args):
        '''Depack `args` into attributes in class'''
        if self.oxpos is None:
            self.oxpos, self.oypos = self.sx, self.sy
            self.dxpos, self.dypos = self.sx, self.sy

    def grab(self, class_instance, exclusive=False):
        '''Grab a touch. You can grab a touch if you absolutly want to receive
        on_touch_move() and on_touch_up(), even if the touch is not dispatched
        by your parent ::

            def on_touch_down(self, touch):
                touch.grab(self)

            def on_touch_move(self, touch):
                if touch.grab_current == self:
                    # i receive my grabbed touch
                else:
                    # it's a normal touch

            def on_touch_up(self, touch):
                if touch.grab_current == self:
                    # i receive my grabbed touch, i must ungrab it !
                    touch.ungrab(self)
                else:
                    # it's a normal touch

        '''
        if self.grab_exclusive_class is not None:
            raise Exception('Cannot grab the touch, touch are exclusive')
        if exclusive:
            self.grab_exclusive_class = class_instance
        self.grab_list.append(class_instance)

    def ungrab(self, class_instance):
        '''Ungrab a previous grabbed touch'''
        if self.grab_exclusive_class == class_instance:
            self.grab_exclusive_class = None
        if class_instance in self.grab_list:
            self.grab_list.remove(class_instance)

    def move(self, args):
        '''Move the touch to another position.'''
        self.dxpos, self.dypos, self.dzpos = self.x, self.y, self.z
        self.depack(args)

    def scale_for_screen(self, w, h, p=None):
        '''Scale position for the screen'''
        self.x = self.sx * float(w)
        self.y = self.sy * float(h)
        if p:
            self.z = self.sz * float(p)

    def push(self, attrs='xyz'):
        '''Push attributes values in `attrs` in the stack'''
        values = map(lambda x: getattr(self, x), attrs)
        self.attr.append((attrs, values))

    def pop(self):
        '''Pop attributes values from the stack'''
        attrs, values = self.attr.pop()
        for i in xrange(len(attrs)):
            setattr(self, attrs[i], values[i])

    def copy_to(self, to):
        '''Copy some attribute to another touch object.'''
        for attr in self.copy_attributes:
            to.__setattr__(attr, self.__getattribute__(attr))

    def __str__(self):
        classname = str(self.__class__).split('.')[-1].replace('>', '').replace('\'', '')
        return '<%s spos=%s pos=%s>' % (classname, str(self.spos), str(self.pos))

    # facility
    pos = property(lambda self: (self.x, self.y),
            doc='''Return (self.x, self.y)''')
    dpos = property(lambda self: (self.dxpos, self.dypos),
            doc='''Return (self.dxpos, self.dypos)''')
    opos = property(lambda self: (self.oxpos, self.oypos),
            doc='''Return (self.oxpos, self.oypos)''')
    spos = property(lambda self: (self.sx, self.sy),
            doc='''Return (self.sx, self.sy)''')

    # compatibility bridge
    xpos = property(lambda self: self.x)
    ypos = property(lambda self: self.y)
    blobID = property(lambda self: self.id)
    xmot = property(lambda self: self.X)
    ymot = property(lambda self: self.Y)
    zmot = property(lambda self: self.Z)
    mot_accel = property(lambda self: self.m)
    rot_accel = property(lambda self: self.r)
    angle = property(lambda self: self.a)
