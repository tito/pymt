from python cimport Py_DECREF

cdef class Property:
    '''Base class for build more complex property. This handle all the basics
    setter and getter, None handling, and observers.
    '''

    cdef str name
    cdef int allownone
    cdef object defaultvalue
    cdef dict storage

    def __cinit__(self):
        self.name = ''
        self.allownone = 0
        self.defaultvalue = None
        self.storage = {}

    def __init__(self, defaultvalue, **kw):
        self.defaultvalue = defaultvalue
        self.allownone = <int>kw.get('allownone', 0)

    cdef init_storage(self, storage):
        storage['value'] = self.defaultvalue
        storage['allownone'] = self.allownone
        storage['observers'] = []

    cpdef link(self, object obj, str name):
        d = dict()
        self.name = name
        self.init_storage(d)
        self.storage[obj] = d

        # XXX God. Let's pray that python people don't see that.
        # The issue with dictionnary is if we use the object (obj) directly, we
        # are referencing it. And it will be never deleted. Weakref would
        # introduce a lot of overhead for nothing. Looking on a uniq id
        # attribute introduce the dot looking overhead (obj.something). So, to
        # prevent any more looking, we just unref our reference, and in the
        # __del__ of the object, we unlink the ourself from the object.
        Py_DECREF(obj)

    cpdef link_deps(self, object obj, str name):
        pass

    cpdef unlink(self, obj):
        if obj in self.storage:
            del self.storage[obj]

    cpdef bind(self, obj, observer):
        '''Add a new observer to be called only when the value is changed
        '''
        observers = self.storage[obj]['observers']
        if not observer in observers:
            observers.append(observer)

    cpdef unbind(self, obj, observer):
        '''Remove a observer from the observer list
        '''
        observers = self.storage[obj]['observers']
        if observer in observers:
            observers.remove(observer)

    def __set__(self, obj, val):
        self.set(obj, val)

    def __get__(self, obj, objtype):
        return self.get(obj)

    cpdef set(self, obj, value):
        '''Set a new value for the property
        '''
        value = self.convert(obj, value)
        d = self.storage[obj]
        realvalue = d['value']
        if realvalue == value:
            return False
        self.check(obj, value)
        d['value'] = value
        self.dispatch(obj)
        return True

    cpdef get(self, obj):
        '''Return the value of the property
        '''
        return self.storage[obj]['value']

    cpdef doc(self):
        '''Return the generated doc from the property.
        '''
        return self.__class__.__name__

    #
    # Private part
    #

    cdef check(self, obj, x):
        '''Check if the value is correct or not, depending the settings of the
        property class.
        '''
        if x is None:
            if not self.storage[obj]['allownone']:
                raise ValueError('None is not allowed')
            else:
                return True

    cdef convert(self, obj, x):
        '''Convert the initial value to a correct value.
        Can be used for multiple type of argument, and simplify into only one.
        '''
        return x

    cdef dispatch(self, obj):
        '''Dispatch the value change to all observers
        '''
        observers = self.storage[obj]['observers']
        value = self.storage[obj]['value']
        for observer in observers:
            observer(obj, value)


cdef class NumericProperty(Property):
    cdef check(self, obj, value):
        if Property.check(self, obj, value):
            return True
        if type(value) not in (int, float):
            raise ValueError('Value of the property is not a numeric (int/float)')


cdef class StringProperty(Property):
    cdef check(self, obj, value):
        if Property.check(self, obj, value):
            return True
        if not isinstance(value, basestring):
            raise ValueError('Value of the property is not a string')


cdef class BoundedNumericProperty(Property):
    cdef int use_min
    cdef int use_max
    cdef long min
    cdef long max

    def __cinit__(self):
        self.use_min = 0
        self.use_max = 0
        self.min = 0
        self.max = 0

    def __init__(self, *largs, **kw):
        value = kw.get('min', None)
        if value is None:
            self.use_min = 0
        else:
            self.use_min = 1
            self.min = value
        value = kw.get('max', None)
        if value is None:
            self.use_max = 0
        else:
            self.use_max = 1
            self.max = value
        Property.__init__(self, *largs, **kw)

    cdef init_storage(self, storage):
        Property.init_storage(self, storage)
        storage['min'] = self.min
        storage['max'] = self.max
        storage['use_min'] = self.use_min
        storage['use_max'] = self.use_max

    cdef check(self, obj, value):
        if Property.check(self, obj, value):
            return True
        s = self.storage['obj']
        if s['use_min']:
            _min = s['min']
            if _min and value < _min:
                raise ValueError('Value is below the minimum bound (%d)' % _min)
        if s['use_max']:
            _max = s['max']
            if _max and value > _max:
                raise ValueError('Value is below the maximum bound (%d)' % _max)
        return True


cdef class OptionProperty(Property):
    cdef list options

    def __cinit__(self):
        self.options = []

    def __init__(self, *largs, **kw):
        self.options = <list>(kw.get('options', []))
        Property.__init__(self, *largs, **kw)

    cdef init_storage(self, storage):
        Property.init_storage(self, storage)
        storage['options'] = self.options[:]

    cdef check(self, obj, value):
        if Property.check(self, obj, value):
            return True
        if value not in self.storage[obj]['options']:
            raise ValueError('Value is not in available options')


cdef class ReferenceListProperty(Property):
    cdef list properties

    def __cinit__(self):
        self.properties = list()

    def __init__(self, *largs, **kw):
        for prop in largs:
            self.properties.append(prop)
        Property.__init__(self, largs, **kw)

    cdef init_storage(self, storage):
        Property.init_storage(self, storage)
        storage['properties'] = self.properties
        storage['stop_event'] = 0

    cpdef link_deps(self, object obj, str name):
        Property.link_deps(self, obj, name)
        for prop in self.properties:
            prop.bind(obj, self.trigger_change)

    cpdef trigger_change(self, obj, value):
        if self.storage[obj]['stop_event']:
            return
        self.storage[obj]['value'] = [
            x.get(obj) for x in self.storage[obj]['properties']]

    cdef convert(self, obj, value):
        if type(value) not in (list, tuple):
            raise ValueError('Value must be a list or tuple')
        return <list>value

    cdef check(self, obj, value):
        if len(value) != len(self.storage[obj]['properties']):
            raise ValueError('Value must have the same size as beginning')

    cpdef set(self, obj, value):
        '''Set a new value for the property
        '''
        cdef int idx
        storage = self.storage[obj]
        value = self.convert(obj, value)
        if storage['value'] == value:
            return False
        self.check(obj, x)
        # prevent dependice loop
        storage['stop_event'] = 1
        props = storage['properties']
        for idx in xrange(len(x)):
            prop = props[idx]
            x = value[idx]
            prop.set(obj, x)
        storage['stop_event'] = 0
        storage['value'] = value
        self.dispatch(obj)
        return True


'''
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

'''
