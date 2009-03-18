#
# matrix.py
#
# Copyright 2007, Paul McGuire
#
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# version 1.0.0 - January 23, 2007
'''
Matrix: matrix implementation, used for scatter
'''

import random,math,operator

stringPrecision = 3
epsilon = 1e-8

def any(lst):
    for item in lst:
        if item: return True
    return False

# Caching decorators
def cacheValue(f):
    fname = f.func_name
    def cachedRetValFunc(*args):
        self = args[0]
        if not fname in self._CACHE_:
            self._CACHE_[fname] = f(*args)
        return self._CACHE_[fname]
    cachedRetValFunc.func_name = fname
    return cachedRetValFunc

def cacheValueWithArgs(f):
    fname = f.func_name
    def cachedRetValFunc(*args):
        self = args[0]
        funcArgsTuple = (fname,)+tuple(args[1:])
        if not funcArgsTuple in self._CACHE_:
            self._CACHE_[funcArgsTuple] = f(*args)
        return self._CACHE_[funcArgsTuple]
    cachedRetValFunc.func_name = fname
    return cachedRetValFunc

def resetCache(f):
    fname = f.func_name
    def resetCacheFunc(*args):
        self = args[0]
        retval = f(*args)
        self._CACHE_.clear()
        return retval
    resetCacheFunc.func_name = fname
    return resetCacheFunc

def initCache(f):
    def __init__(*args):
        self = args[0]
        self._CACHE_ = {}
        return f(*args)
    return __init__

def verboseCache(f):
    fname = f.func_name
    def func(*args):
        self = args[0]
        if fname in self._CACHE_:
            print "getting",fname,"from cache"
        else:
            print "computing",fname
        return f(*args)
    func.func_name = fname
    return func

def verboseCacheWithArgs(f):
    fname = f.func_name
    def func(*args):
        self = args[0]
        funcArgsTuple = (fname,)+tuple(args[1:])
        if funcArgsTuple in self._CACHE_:
            print "getting",fname,"(with args) from cache"
        else:
            print "computing",fname
        return f(*args)
    func.func_name = fname
    return func


class MatrixException(Exception):
    pass

class Vector(object):
    @initCache
    def __init__(self,vallist):
        if isinstance(vallist,str):
            try:
                vallist = map(float,vallist.split())
            except ValueError,ve:
                vallist = map(complex,vallist.split())

        elif vallist and isinstance(vallist[0],int):
            vallist = map(float,vallist)
        else:
            vallist = map(float,vallist)
        self.values = vallist[:]
        self.parent = None

    def __getitem__(self,idx):
        if isinstance(idx,slice):
            return self.values[idx]
        return self.values[idx-1]

    @resetCache
    def __setitem__(self,idx,val):
        self.values[idx-1] = val
        if self.parent is not None:
            self.parent.notifyContentsChange()

    @cacheValue
    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return iter(self.values)

    @cacheValue
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__,self.values)

    @cacheValue
    def __str__(self):
        if any([ isinstance(v,complex) for v in self.values ]):
            return ", ".join( [ str(v) for v in self.values ] )
        else:
            return ", ".join( [ str(round(v,stringPrecision)) for v in self.values ] )

    def __add__(self,other):
        if self.__class__ == other.__class__:
            return self.__class__( [ a+b for a,b in zip(self,other) ] )
        elif isinstance(other,(int,float)):
            return self.__class__( [a+other for a in self] )
        else:
            raise Exception("???")

    def __sub__(self,other):
        if self.__class__ == other.__class__:
            return self.__class__( [ a-b for a,b in zip(self,other) ] )
        elif isinstance(other,(int,float)):
            return self.__class__( [a-other for a in self] )
        else:
            print self,self.__class__.__name__
            print other,other.__class__.__name__
            raise Exception("???")

    def __eq__(self,other):
        return self.__class__.__name__ == other.__class__.__name__ and \
            self.values == other.values

    def __ne__(self,other):
        return not self==other

    @cacheValue
    def __nonzero__(self):
        for v in self.values:
            if v: return True
        return False

    @cacheValue
    def __abs__(self):
        return self.__class__( map(abs,self.values) )

    def __lt__(self,other):
        if self.__class__ == other.__class__:
            if len(self) == len(other):
                for a,b in zip(self,other):
                    if not a<b: return False
                return True
            else:
                raise MatrixException("can only compare vectors of same length")
        else:
            raise MatrixException("can only compare vectors of same type")

    def setParent(self,p):
        self.parent = p

    @cacheValue
    def minval(self):
        return min(self.values)

    @cacheValue
    def maxval(self):
        return max(self.values)

    @cacheValue
    def normalized(self):
        mag = math.sqrt(sum(a*a for a in self))
        return self * (1.0/mag)

    @cacheValue
    def complex(self):
        return self.__class__( [ complex(v) for v in self.values ] )

    @cacheValue
    def conjugate(self):
        return self.__class__( [ v.conjugate() for v in self.complex().values ] )


class ColVector(Vector):
    @cacheValue
    def transpose(self):
        return RowVector(self.values)

    def __mul__(self,other):
        if isinstance(other,(int,float)):
            return ColVector([a*other for a in self])
        elif isinstance(other,RowVector):
            return Matrix([RowVector(other*a) for a in self])
        else:
            raise MatrixException("Can only multiply RowVectors with ColVectors")

    @cacheValue
    def numRows(self):
        return len(self)

    @cacheValue
    def numCols(self):
        return 1


class RowVector(Vector):
    @cacheValue
    def transpose(self):
        return ColVector(self.values)

    def __mul__(self,other):
        if isinstance(other,ColVector):
            if len(other)==len(self):
                return sum([a*b for a,b in zip(self, other)])
            else:
                raise MatrixException("Vectors must be same length")
        elif isinstance(other,Matrix):
            if len(self) == other.numRows():
                return RowVector([self*other.col(i) for i in other.colrange()])
            else:
                raise MatrixException("Matrix has wrong number of rows")
        elif isinstance(other,(int,float)):
            return RowVector([a*other for a in self])
        else:
            raise MatrixException("Can only multiply RowVectors with ColVectors")

    @cacheValue
    def numRows(self):
        return 1

    @cacheValue
    def numCols(self):
        return len(self)

class Matrix(object):
    @initCache
    def __init__(self,data):
        if isinstance(data,str):
            self._rows = [RowVector(s) for s in data.split("\n")]
        elif isinstance(data,(list,tuple)):
            if isinstance(data[0],str):
                self._rows = map(RowVector,data)
            elif isinstance(data[0],RowVector):
                self._rows = data[:]
            elif isinstance(data[0],ColVector):
                self._rows = zip(data)
        for r in self._rows:
            r.setParent(self)
        self.parent = None
        self.submatrixcache = {}

    @resetCache
    def notifyContentsChange(self):
        pass

    def __mul__(self,other):
        if isinstance(other,(int,float)):
            return Matrix( [ r*other for r in self._rows ] )
        if isinstance(other,ColVector):
            if self.numCols() == other.numRows():
                return RowVector( [r*other for r in self._rows ] )
            else:
                raise MatrixException("mismatch sizes for multiplication")
        if isinstance(other,Matrix):
            if self.numCols() == other.numRows():
                othercols = [ other.col(i) for i in other.colrange() ]
                newrows = [ RowVector( [r*col for col in othercols] ) for r in self._rows ]
                return Matrix(newrows)
            else:
                raise MatrixException("mismatch sizes for multiplication")
        raise MatrixException("mismatch types for matrix multiplication")

    def __rmul__(self,other):
        if isinstance(other,(int,float)):
            return Matrix( [ r*other for r in self._rows ] )
        raise MatrixException("mismatch types for matrix multiplication")

    @resetCache
    def __imul__(self,other):
        tmp = self*other
        self._rows = tmp._rows
        for r in self._rows:
            r.setParent(self)
        return self

    @cacheValue
    def __str__(self):
        return "\n".join(map(str,self._rows))

    def __eq__(self,other):
        return self.__class__.__name__ == other.__class__.__name__ and \
            self._rows == other._rows

    def __ne__(self,other):
        return not self==other

    @cacheValue
    def __nonzero__(self):
        for r in self._rows:
            if r: return True
        return False

    @cacheValue
    def transpose(self):
        """Function to return the transpose of a matrix."""
        tmp = zip( *[ r.values for r in self._rows ] )
        return Matrix( map(RowVector,tmp) )

    @cacheValue
    def numRows(self):
        return len(self._rows)

    @cacheValue
    def numCols(self):
        return len(self[1])

    @cacheValue
    def isSquare(self):
        return self.numCols() == self.numRows()

    @cacheValue
    def isSymmetric(self):
        if self.isSquare():
            for i in self.rowrange():
                for j in self.colrange():
                    if abs(self[i][j]-self[j][i]) > epsilon:
                        return False
            return True
        return False

    @cacheValueWithArgs
    def col(self,idx):
        return ColVector( [ a[idx] for a in self._rows ] )

    @cacheValueWithArgs
    def row(self,idx):
        return self._rows[idx-1]

    def __getitem__(self,idx):
        if isinstance(idx,slice):
            return Matrix([ RowVector(r.values) for r in self._rows[idx]])
        return self.row(idx)

    def __delitem__(self,idx):
        del self._rows[idx-1]

    def __add__(self,other):
        if isinstance(other,(int,float)):
            return Matrix( [ row+other for row in self._rows ] )
        elif isinstance(other,Matrix):
            if self.numRows() == other.numRows() and self.numCols() == other.numCols():
                return Matrix( [ a+b for a,b in zip(self._rows,other._rows) ] )
            else:
                raise MatrixException("cannot add matrices of unlike dimensions")
        else:
            raise MatrixException("unlike types for matrix addition")

    def __radd__(self,other):
        if isinstance(other,(int,float)):
            return Matrix( [ row+other for row in self._rows ] )
        else:
            raise MatrixException("unlike types for matrix addition")

    def __sub__(self,other):
        if isinstance(other,(int,float)):
            return self + -other
        elif isinstance(other,Matrix):
            if self.numRows() == other.numRows() and self.numCols() == other.numCols():
                return Matrix( [ a-b for a,b in zip(self._rows,other._rows) ] )
            else:
                raise MatrixException("cannot subtract matrices of unlike dimensions")
        else:
            raise MatrixException("unlike types for matrix subtraction")

    def __rsub__(self,other):
        raise MatrixException("unlike types for matrix subtraction")

    @cacheValue
    def trace(self):
        """Function to return the trace of a matrix."""
        if self.isSquare():
            return sum( r[i] for r,i in zip(self._rows,self.colrange()) )
        else:
            raise MatrixException("can only compute trace for square matrices")

    @cacheValue
    def colrange(self):
        return range(1,self.numCols()+1)

    @cacheValue
    def rowrange(self):
        return range(1,self.numRows()+1)

    def getCachedMatrix( self,rowVectList ):
        if self.parent is not None:
            return self.parent.getCachedMatrix(rowVectList)
        vals = tuple( tuple(v.values) for v in rowVectList )
        if vals not in self.submatrixcache:
            self.submatrixcache[vals] = m = Matrix(rowVectList)
            m.parent = self
        return self.submatrixcache[vals]

    #@verboseCache - add this decorator to view cache effectivity
    @cacheValue
    def det(self):
        "Function to return the determinant of the matrix."
        if self.isSquare():
            if self.numRows() > 2:
                multiplier = 1
                firstRow = self[1]
                tmp = self._rows[1:]
                rangelentmp = range(len(tmp))
                col = 0
                detsum = 0
                for val in firstRow:
                    if val:
                        #~ tmp2 = Matrix([ RowVector(t[0:col]+t[col+1:]) for t in tmp ])
                        tmp2 = self.getCachedMatrix([ RowVector(t[0:col]+t[col+1:]) for t in tmp ])
                        detsum += ( multiplier * val * tmp2.det() )
                    multiplier = -multiplier
                    col += 1
                return detsum
            if self.numRows() == 2:
                return self[1][1]*self[2][2]-self[1][2]*self[2][1]
            if self.numRows() == 1:
                return self[1][1]
            if self.numRows() == 0:
                return 0
        else:
            raise MatrixException("can only compute det for square matrices")

    # @cacheValueWithArgs (don't bother cacheing cofactor, its caller is cached)
    def cofactor(self,i,j):
        i-=1
        j-=1
        #~ tmp = Matrix([ RowVector(r[:i]+r[i+1:]) for r in (self._rows[:j]+self._rows[j+1:]) ])
        tmp = self.getCachedMatrix([ RowVector(r[:i]+r[i+1:]) for r in (self._rows[:j]+self._rows[j+1:]) ])
        if (i+j)%2:
            return -tmp.det()
        else:
            return tmp.det()
        #~ return (-1) ** (i+j) * tmp.det()

    @cacheValue
    def inverse(self):
        if self.isSquare():
            if self.det() != 0:
                ret = Matrix( [ RowVector( [ self.cofactor(i,j) for j in self.colrange() ] )
                                 for i in self.rowrange() ] )
                ret *= (1.0/self.det())
                return ret
            else:
                raise MatrixException("cannot compute inverse for singular matrices")
        else:
            raise MatrixException("can only compute inverse for square matrices")

    @cacheValue
    def conjugate(self):
        return Matrix( [ vec.conjugate() for vec in self._rows ] )

    @cacheValue
    def round(self,digits):
        def roundTo(n):
            return lambda x : round(x,n)
        return Matrix([ RowVector( map(roundTo(digits), r.values ) ) for r in self._rows ])

    @cacheValue
    def eigen(self):
        epsvec = RowVector( [epsilon*epsilon]*self.numRows() )
        escape = 0
        v = RowVector([ random.random() for i in self.rowrange()]).normalized()
        lastv = abs(v) + 2 * epsvec
        while epsvec < abs(v-lastv) and escape < 500:
            lastv = RowVector( v[:] )
            v = (v*self).normalized()
            escape += 1
        if escape == 500:
            raise MatrixException("eigenvector did not converge")

        v2 = v*self
        for a,b in zip(v2,v):
            if b:
                return v,a/b
        raise MatrixException("generated zero vector")

    @cacheValue
    def eigenAll(self):
        if self.isSymmetric():
            m2 = self[:]
            ret = []
            for i in self.rowrange():
                vec,val = m2.eigen()
                ret.append( (vec,val) )
                m2 = m2 - (vec.transpose()*vec*val)
            return ret
        else:
            return [ self.eigen(), ]

    @staticmethod
    def Identity(n):
        """A factory method to construct an nxn identity matrix."""
        return Matrix([ RowVector([0]*i+[1]+[0]*(n-i-1)) for i in range(n) ] )

    @staticmethod
    def Zero(n):
        """A factory method to construct an nxn zero matrix."""
        row = [0]*n
        return Matrix([ RowVector(row[:]) for i in range(n) ] )


def testMatrix(m):
    print "----------------"
    print "A"
    print m
    print
    print " T"
    print "A"
    print m.transpose()
    print
    print "tr(A) =",m.trace()
    print
    if m.isSymmetric():
        print "Eigenvectors of A"
        m2 = m[:]
        vecs = []
        vals = []
        for i in m.rowrange():
            try:
                vec,val = m2.eigen()
                vecs.append(vec)
                vals.append(val)
                print vec, ":", val
                m2 = m2 - (vec.transpose()*vec*val)
            except Exception,e:
                print e
                break

        print
        print "verify eigenvectors (expect zero matrix)"
        m3 = Matrix.Zero(m.numRows())
        for vec,val in zip(vecs,vals):
            m3 = m3 + (vec.transpose()*vec)*val
        print m3-m
    else:
        print "Principal Eigenvector of A"
        try:
            print m.eigen()[0], ":", m.eigen()[1]
        except Exception,e:
            print e
    print
    try:
        print "|A| =",m.det()
    except Exception,e:
        print e
    print
    print "inv(A)"
    try:
        print m.inverse()
    except Exception,e:
        print e
    print
    print "A*inv(A) (expect identity matrix)"
    try:
        print m*m.inverse()
    except Exception,e:
        print e
    print


if __name__ == "__main__":
    testMatrix(Matrix( [ RowVector([1,0]),
                        RowVector([0,1])]) )

def test():
    # create matrix the hard way
    avec = RowVector("1 2 3")
    bvec = ColVector("4 5 6")
    testMatrix( Matrix([avec,bvec.transpose(),RowVector([10,9,10])]) )

    # create matrix the easy way
    testMatrix( Matrix(  """1 2 3 4
                             5 11 20 3
                             2 7 11 1
                             0 5 3 1""") )

    # some helpers for common matrix construction
    testMatrix( Matrix.Zero(3) )
    testMatrix( Matrix.Identity(5) )

    # create special matrix - note indexing is 1-based, not 0-based
    m = Matrix.Identity(6)
    m[1][2] = -10
    m[4][3] = 5
    m[1][6] = 3
    m[6][1] = 1
    testMatrix(m)

    # diagonal matrix
    m = Matrix.Identity(6)
    m[2][2] = 5
    m[3][3] = 8
    m[4][4] = 11
    m[5][5] = 9
    m[6][6] = 7
    testMatrix(m)

    testMatrix( Matrix(  """2 3
                             2 1""") )

    # try a large symmetric matrix for eigenvalue calcs and inversion performance
    n = 10
    m = Matrix.Zero(n)
    for i in range(1,n+1):
        m[i][i] = random.random()*100
        for j in range(i+1,n+1):
            m[i][j] = random.random()*10-5
            m[j][i] = m[i][j]
    testMatrix(m)
