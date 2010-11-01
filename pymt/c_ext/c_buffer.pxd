cdef class Buffer:
    cdef void *data
    cdef list l_free
    cdef int blocksize
    cdef int blockcount

    cdef grow(self, int blockcount)
    cdef list add(self, void *blocks, int count)
    cdef void remove(self, list indices)
    cdef int count(self)
    cdef int size(self)
    cdef void *pointer(self)
