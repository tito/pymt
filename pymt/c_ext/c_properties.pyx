from copy import deepcopy, copy

cdef class Property:
    '''Base class for build more complex property. This handle all the basics
    setter and getter, None handling, and observers.
    '''

    cdef str name, bound_name
    cdef readonly int allownone
    cdef object defaultvalue

    def __cinit__(self):
        self.name = ''
        self.allownone = 0
        self.defaultvalue = None

    def __init__(self, defaultvalue, **kw):
        self.defaultvalue = defaultvalue
        self.allownone = <int>kw.get('allownone', 0)
        # ensure that the default value fit to the check.
        self.check(self.defaultvalue)

    cpdef link(self, obj, name):
        self.name = name
        self.bound_name = '___%s' % name
        obj.__dict__['___%s' % name] = dict(
            value = self.defaultvalue,
            observers = []
        ))

    cpdef bind(self, obj, observer):
        '''Add a new observer to be called only when the value is changed
        '''
        observers = obj.__dict__[self.bound_name]['observers']
        if not observer in observers:
            observers.append(observer)

    cpdef unbind(self, obj, observer):
        '''Remove a observer from the observer list
        '''
        observers = obj.__dict__[self.bound_name]['observers']
        if observer in observers:
            observers.remove(observer)

    def __set__(self, obj, val):
        self.pset(obj, val)

    def __get__(self, obj, objtype):
        return self.pget(obj, objtype)

    cpdef pset(self, obj, value):
        '''Set a new value for the property
        '''
        value = self.convert(value)
        d = obj.__dict__[self.bound_name]
        realvalue = d['value']
        if realvalue == value:
            return False
        self.check(value)
        d['value'] = value
        self.dispatch(obj)
        return True

    cpdef pget(self, obj, objtype):
        '''Return the value of the property
        '''
        return obj.__dict__[self.bound_name]['value']

    cpdef doc(self):
        '''Return the generated doc from the property.
        '''
        return self.__class__.__name__

    #
    # Private part
    #

    cdef check(self, object x):
        '''Check if the value is correct or not, depending the settings of the
        property class.
        '''
        if x is None:
            if not self.allownone:
                raise ValueError('None is not allowed')
            else:
                return True

    cdef convert(self, object x):
        '''Convert the initial value to a correct value.
        Can be used for multiple type of argument, and simplify into only one.
        '''
        return x

    cdef dispatch(self, obj):
        '''Dispatch the value change to all observers
        '''
        cdef object observer
        observers = obj.__dict__[self.bound_name]['observers']
        value = obj.__dict__[self.bound_name]['value']
        for observer in observers:
            observer(value)

cdef class NumericProperty(Property):
    cdef check(self, object x):
        if Property.check(self, x):
            return True
        if type(x) not in (int, float):
            raise ValueError('Value of the property is not a numeric (int/float)')

"""
cdef class StringProperty(Property):
    cdef check(self, object x):
        if Property.check(self, x):
            return True
        if not isinstance(x, basestring):
            raise ValueError('Value of the property is not a string')

cdef class BoundedNumericProperty(Property):
    cdef int _use_min
    cdef int _use_max
    cdef long min
    cdef long max

    def __cinit__(self):
        self._use_min = 0
        self._use_max = 0
        self.min = 0
        self.max = 0

    def __init__(self, *largs, **kw):
        value = kw.get('min', None)
        if value is None:
            self._use_min = 0
        else:
            self._use_min = 1
            self.min = value
        value = kw.get('max', None)
        if value is None:
            self._use_max = 0
        else:
            self._use_max = 1
            self.max = value
        Property.__init__(self, *largs, **kw)

    cdef check(self, object x):
        if Property.check(self, x):
            return True
        if self._use_min:
            _min = self.min
            if _min and x < _min:
                raise ValueError('Value is below the minimum bound (%d)' % _min)
        if self._use_max:
            _max = self.max
            if _max and x > _max:
                raise ValueError('Value is below the maximum bound (%d)' % _max)
        return True

cdef class OptionProperty(Property):
    cdef list options

    def __cinit__(self):
        self.options = []

    def __init__(self, *largs, **kw):
        self.options = list(kw.get('options', []))
        Property.__init__(self, *largs, **kw)

    cdef check(self, object x):
        if Property.check(self, x):
            return True
        if x not in self.options:
            raise ValueError('Value is not in available options')

cdef class ReferenceListProperty(Property):
    cdef list properties
    cdef int stop_event

    def __cinit__(self):
        self.properties = list()
        self.stop_event = 0

    def __init__(self, *largs, **kw):
        for prop in largs:
            self.properties.append(prop)
            prop.bind(self.trigger_change)
        Property.__init__(self, largs, **kw)

    cpdef trigger_change(self, value):
        if self.stop_event:
            return
        self.value = [x.get() for x in self.properties]

    cdef convert(self, x):
        if type(x) not in (list, tuple):
            raise ValueError('Value must be a list or tuple')
        return <list>x

    cdef check(self, x):
        if len(x) != len(self.properties):
            raise ValueError('Value must have the same size as beginning')

    cpdef bool set(self, x):
        '''Set a new value for the property
        '''
        cdef int idx
        x = self.convert(x)
        if self.value == x:
            return False
        self.check(x)
        # prevent dependice loop
        self.stop_event = 1
        for idx in xrange(len(x)):
            prop = self.properties[idx]
            value = x[idx]
            prop.set(value)
        self.stop_event = 0
        self.value = x
        self.dispatch()
        return True

    cpdef get(self):
        '''Return the value of the property
        '''
        return self.value

cdef class AliasProperty(Property):
    cdef object getter
    cdef object setter

    def __cinit__(self):
        self.getter = None
        self.setter = None

    def __init__(self, getter, setter, **kwargs):
        Property.__init__(self, None, **kwargs)
        self.getter = getter
        self.setter = setter
        for prop in kwargs.get('bind', []):
            prop.bind(self.trigger_change)

    cpdef trigger_change(self, value):
        self.dispatch()

    cdef check(self, value):
        return True

    cpdef get(self):
        return self.getter()

    cpdef bool set(self, value):
        return self.setter(value)

"""
