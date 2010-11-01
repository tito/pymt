cdef extern from "stdlib.h":
    ctypedef unsigned long size_t
    void free(void *ptr)
    void *realloc(void *ptr, size_t size)

cdef extern from "string.h":
    void *memcpy(void *dest, void *src, size_t n)


cdef class Buffer:
    '''Buffer class is designed to manage very fast a list of fixed size block.
    You can easily add and remove data from the buffer.
    '''
    def __cinit__(self):
        self.data = NULL
        self.blocksize = 0
        self.blockcount = 0
        self.l_free = []


    def __del__(self):
        if self.data != NULL:
            free(self.data)
            self.data = NULL
        self.blockcount = 0
        self.blocksize = 0
        self.l_free = []


    def __init__(self, int blocksize):
        self.blocksize = blocksize


    cdef grow(self, int blockcount):
        '''Automaticly realloc the memory if they are no enough block.
        Work only for "grow" operation, not the inverse.
        '''
        cdef void *newptr = NULL

        # set blockcount to the nearest 8 block
        diff = blockcount % 8
        if diff != 0:
            blockcount = (8 - (blockcount % 8)) + blockcount

        if blockcount < self.blockcount:
            return

        # Try to realloc
        newptr = realloc(self.data, self.blocksize * self.blockcount)
        if newptr == NULL:
            raise SystemError('Unable to realloc memory for buffer')

        # Realloc work, put the new pointer
        self.data = newptr

        # Create the free blocks
        diff = blockcount - self.blockcount
        self.l_free.extend(range(self.blockcount, self.blockcount + diff))

        # Update how many block are allocated
        self.blockcount = blockcount


    cdef list add(self, void *blocks, int count):
        '''Add a list of block inside our buffer
        '''
        cdef int i, block
        cdef void *p
        cdef list out = []

        # Ensure that our buffer is enough for having all the elements
        if count > len(self.l_free):
            self.grow(self.blockcount + count)

        # Add all the block inside our buffer
        for i in xrange(count):
            p = blocks + (self.blocksize * i)

            # Take a free block
            block = self.l_free.pop(0)

            # Copy content
            memcpy(p, self.data + (block * self.blocksize), self.blocksize)

            # Push the current block as indices
            out.append(block)

        return out


    cdef void remove(self, list indices):
        '''Remove block from our list
        '''
        # Actually, it's really more simpler,
        # We are just mark them as freed.
        self.l_free = list(set(self.l_free + indices))


    cdef int count(self):
        '''Return how many block are currently used
        '''
        return self.blockcount - len(self.l_free)


    cdef int size(self):
        '''Return the size of the allocated buffer
        '''
        return self.blocksize * self.blockcount


    cdef void *pointer(self):
        '''Return the data pointer
        '''
        return self.data

'''
def run():
    cdef float a[6]
    cdef Buffer b

    a[0] = 1
    a[1] = 1
    a[2] = 1
    a[3] = 1
    a[4] = 1
    a[5] = 1

    b = Buffer(sizeof(float))
    print 'size=', b.size(), 'count=', b.count()
    f1 = b.add(a, 1)
    print 'indices', f1
    print 'size=', b.size(), 'count=', b.count()
    f2 = b.add(a, 1)
    print 'indices', f2
    print 'size=', b.size(), 'count=', b.count()
    f3 = b.add(a, 4)
    print 'indices', f3
    print 'size=', b.size(), 'count=', b.count()

    print 'remove====='
    b.remove(f2)
    print 'size=', b.size(), 'count=', b.count()
    f2 = b.add(a, 4)
    print 'indices', f2
    print 'size=', b.size(), 'count=', b.count()

    b.remove(f1)
    b.remove(f2)
    b.remove(f3)
    print 'size=', b.size(), 'count=', b.count()


if __name__ == '__main__':
    run()
'''
